import logging

import numpy as np

from sqlalchemy import select, delete, func
from model.model import Feature_set, Features

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import pairwise_distances
from scipy.cluster.hierarchy import linkage

class Recognition_DAL():

    # POST upload feature set
    async def upload_feature_set(session, json_data):
        async with session.begin():
            logging.info("## Session connected ##")

            uploadFeatureSetCheck = await session.execute(select(Feature_set).where(Feature_set.name == json_data.get("FeatureSet")).exists().select())

            if uploadFeatureSetCheck.fetchone()[0] is False:
                logging.info("    + " + str(json_data.get("FeatureSet")))

                newFeatureSet = Feature_set(name = json_data.get("FeatureSet"))

                if len(list(json_data.get("Features"))) != 0:
                    for element in list(json_data.get("Features")):
                            newFeature = Features(feature = element)
                            newFeatureSet.feature_children.append(newFeature)
                            session.add(newFeature)

                session.add(newFeatureSet)
                return True
            else:
                logging.error("!! POST upload feature set error: Inserted feature set {} already exists !!\n".format(str(json_data.get("FeatureSet"))))
                return False

    # POST extend feature set
    async def extend_feature_set(session, json_data):
        async with session.begin():
            logging.info("## Session connected ##")

            extendFeatureSetCheck = await session.execute(select(Feature_set).where(Feature_set.name == json_data.get("FeatureSet")).exists().select())

            if extendFeatureSetCheck.fetchone()[0] is True:
                logging.info("    * " + str(json_data.get("FeatureSet")))

                existingFeatureSetID = await session.execute(select(Feature_set.ID).where(Feature_set.name == json_data.get("FeatureSet")))
                existingFeatureSetID = existingFeatureSetID.fetchone()[0]

                if len(list(json_data.get("Features"))) != 0:
                    for element in list(json_data.get("Features")):
                        newFeature = Features(feature = element, parent_id = existingFeatureSetID)
                        session.add(newFeature)

                return True
            else:
                logging.error("!! POST upload feature set error: Inserted feature set {} already exists !!\n".format(str(json_data.get("FeatureSet"))))
                return False

    # DELETE feature set
    async def delete_feature_set(session, json_data):
        async with session.begin():
            logging.info("## Session connected ##")
            logging.info("    - " + str(json_data.get("FeatureSet")))

            deleteFeatureSetCheck = await session.execute(select(Feature_set).where(Feature_set.name == json_data.get("FeatureSet")).exists().select())

            if deleteFeatureSetCheck.fetchone()[0] == True:
                await session.execute(delete(Feature_set).where(Feature_set.name == json_data.get("FeatureSet"))) 
                return True
            else:
                logging.error("!! DELETE feature set error: Inserted feature set {} doesn't exist !!\n".format(str(json_data.get("FeatureSet"))))
                return False

    # GET list of all feature sets
    async def get_list_of_all_feature_sets(session):
        async with session.begin():
            logging.info("## Session connected ##")

            listOfFeatureSets = await session.execute(select(Feature_set.name))
            numOfRows = await session.execute(select(func.count()).select_from(Features).group_by(Features.parent_id))

            if listOfFeatureSets != None:
                listOfFeatureSetsJSON = {"FeatureSets": [element[0] for element in tuple(listOfFeatureSets.fetchall())], "NumOfRows": [element[0] for element in tuple(numOfRows.fetchall())]}
                return listOfFeatureSetsJSON
            else:
                logging.error("!! No feature sets found in DB !!\n")
                return False

    ################################# RECOGNITION METHODS #################################
    # GET PCA
    async def principalComponentAnalysis(session, json_data):
        async with session.begin():
            logging.info("## Session connected ##")
            logging.info("## Fetching features of dataset {} ##".format(json_data.get("FeatureSet")))

            featureSetCheck = await session.execute(select(Feature_set).where(Feature_set.name == json_data.get("FeatureSet")).exists().select())

            if featureSetCheck.fetchone()[0] is True:
                featureSetID = await session.execute(select(Feature_set.ID).where(Feature_set.name == json_data.get("FeatureSet")))
                listOfFeatures = await session.execute(select(Features.feature).where(Features.parent_id == featureSetID.fetchone()[0]))
                listOfFeatures = [element[0] for element in tuple(listOfFeatures.fetchall())]
            else:
                logging.error("!! No feature set found in DB !!\n")
                return False

        # Split features by comma and remove all whitespaces
        for i in range(len(listOfFeatures)):
            listOfFeatures[i] = [element.strip() for element in listOfFeatures[i].split(",")]

        try:
            # Parser for features with strings in them
            listOfFeatureNames = []

            for i in range(len(listOfFeatures)):
                for j in range(len(listOfFeatures[i])):
                    try:
                        listOfFeatures[i][j] = float(listOfFeatures[i][j])
                    except ValueError:
                        listOfFeatureNames.append(str(listOfFeatures[i][j])) 
                        listOfFeatures[i].pop() 
        except:
            logging.error("!! Failed at spliting feature data into numerical and other data !!")
            return False
        else:
            try:
                # Pricipal Component Analysis
                numpyFeaturesList = np.array(listOfFeatures)
                sc = StandardScaler()
                X_normalised = sc.fit_transform(numpyFeaturesList)

                pca = PCA(n_components = json_data.get("NumOfComponents"))
                X_pca = pca.fit_transform(X_normalised)
                explained_variance = pca.explained_variance_ratio_
                logging.info("## Explained variance for {} components: {} ##".format(json_data.get("NumOfComponents"), explained_variance))

                knn = KNeighborsClassifier(n_neighbors = 1)
                scores_original = cross_val_score(knn, X_normalised, listOfFeatureNames)
                scores_pca = cross_val_score(knn, X_pca, listOfFeatureNames)

                logging.info("## Original score after 1-NN evaluation: {} ##".format(scores_original))
                logging.info("## PCA score after 1-NN evaluation: {} ##".format(scores_pca))
            except:
                logging.error("!! Failed in pricipal component analysis !!")
                return False
            else:
                return {"FeatureSet": json_data.get("FeatureSet"), "X_pca": X_pca.tolist(), "ExplainedVariance": explained_variance.tolist(), "1-NNScoreOriginal": scores_original.tolist(), "1-NNScorePCA": scores_pca.tolist()}

    # GET optimized PCA
    async def optimizedPrincipalComponentAnalysis(session, json_data):
        async with session.begin():
            logging.info("## Session connected ##")
            logging.info("## Fetching features of dataset {} ##".format(json_data.get("FeatureSet")))

            featureSetCheck = await session.execute(select(Feature_set).where(Feature_set.name == json_data.get("FeatureSet")).exists().select())

            if featureSetCheck.fetchone()[0] is True:
                featureSetID = await session.execute(select(Feature_set.ID).where(Feature_set.name == json_data.get("FeatureSet")))
                listOfFeatures = await session.execute(select(Features.feature).where(Features.parent_id == featureSetID.fetchone()[0]))
                listOfFeatures = [element[0] for element in tuple(listOfFeatures.fetchall())]
            else:
                logging.error("!! No feature set found in DB !!\n")
                return False

        # Split features by comma and remove all whitespaces
        for i in range(len(listOfFeatures)):
            listOfFeatures[i] = [element.strip() for element in listOfFeatures[i].split(",")]

        try:
            # Parser for features with strings in them
            listOfFeatureNames = []
            for i in range(len(listOfFeatures)):
                for j in range(len(listOfFeatures[i])):
                    try:
                        listOfFeatures[i][j] = float(listOfFeatures[i][j])
                    except ValueError:
                        listOfFeatureNames.append(str(listOfFeatures[i][j]))
                        listOfFeatures[i].pop()
        except:
            logging.error("!! Failed at spliting feature data into numerical and other data !!")
            return False
        else:
            try:
                # Pricipal Component Analysis
                numpyFeaturesList = np.array(listOfFeatures)
                sc = StandardScaler()
                X_normalised = sc.fit_transform(numpyFeaturesList)

                # Loop over all posible number of components for PCA and find the least number of components with requested accuracy
                pca = PCA()
                pca.fit(X_normalised)
                cumsum = np.cumsum(pca.explained_variance_ratio_)
                optimalNumOfComponents = np.argmax(cumsum >= json_data.get("RequestedVariance")) + 1
            
                # Execute PCA for optimal number of components for requested accuracy
                pca = PCA(n_components = optimalNumOfComponents)
                X_optimal_pca = pca.fit_transform(X_normalised)
                explained_variance = pca.explained_variance_
                logging.info("## Explained variance for {} components: {} ##".format(optimalNumOfComponents, explained_variance))

                # k-NN model definition and cross-corelation comparison score
                knn = KNeighborsClassifier(n_neighbors = 1)
                scores_original = cross_val_score(knn, X_normalised, listOfFeatureNames)
                scores_pca = cross_val_score(knn, X_optimal_pca, listOfFeatureNames)

                logging.info("## Original score after 1-NN evaluation: {} ##".format(scores_original))
                logging.info("## PCA score after 1-NN evaluation: {} ##".format(scores_pca))
            except:
                logging.error("!! Failed in optimized pricipal component analysis !!")
                return False
            else:
                return {"FeatureSet": json_data.get("FeatureSet"), "OptimalNumOfComponents": int(optimalNumOfComponents), "X_optimal_pca": X_optimal_pca.tolist(), "ExplainedVariance": explained_variance.tolist(), "1-NNScoreOriginal": scores_original.tolist(), "1-NNScorePCA": scores_pca.tolist()}

    # GET hierarhical clustering
    async def hierarhicalClustering(session, json_data):
        async with session.begin():
            logging.info("## Session connected ##")
            logging.info("## Fetching features of dataset {} ##".format(json_data.get("FeatureSet")))

            featureSetCheck = await session.execute(select(Feature_set).where(Feature_set.name == json_data.get("FeatureSet")).exists().select())

            if featureSetCheck.fetchone()[0] is True:
                featureSetID = await session.execute(select(Feature_set.ID).where(Feature_set.name == json_data.get("FeatureSet")))
                listOfFeatures = await session.execute(select(Features.feature).where(Features.parent_id == featureSetID.fetchone()[0]))
                listOfFeatures = [element[0] for element in tuple(listOfFeatures.fetchall())]
            else:
                logging.error("!! No feature set found in DB !!\n")
                return False
    
        # Split features by comma and remove all whitespaces
        for i in range(len(listOfFeatures)):
            listOfFeatures[i] = [element.strip() for element in listOfFeatures[i].split(",")]

        try:
            # Parser for features with strings in them
            listOfFeatureNames = []
            for i in range(len(listOfFeatures)):
                for j in range(len(listOfFeatures[i])):
                    try:
                        listOfFeatures[i][j] = float(listOfFeatures[i][j])
                    except ValueError:
                        listOfFeatureNames.append(str(listOfFeatures[i][j]))
                        listOfFeatures[i].pop()
        except:
            logging.error("!! Failed at spliting feature data into numerical and other data !!")
            return False
        else:
            try:
                # Hierarhical clustering
                numpyFeaturesList = np.array(listOfFeatures)
                distance_matrix = np.array([])

                # Use standard scaler to normalise data
                sc = StandardScaler()
                X_normalised = sc.fit_transform(numpyFeaturesList)

                # Define different meassures to use in clustering
                if json_data.get("Metric") == 'cosine':
                    distance_matrix = pairwise_distances(X_normalised.T, metric='cosine')
                elif json_data.get("Metric") == 'cityblock':
                    distance_matrix = pairwise_distances(X_normalised.T, metric='cityblock')
                elif json_data.get("Metric") == 'euclidean':
                    distance_matrix = pairwise_distances(X_normalised.T, metric='euclidean')
                else:
                    logging.error("!! Metric attribute not found in JSON !!\n")

                if json_data.get("NumOfClusters") is not None:
                    if json_data.get("Linkage") is not None:
                        cluster = AgglomerativeClustering(n_clusters=json_data.get("NumOfClusters"), affinity='precomputed', linkage=json_data.get("Linkage"))
                    else:
                        cluster = AgglomerativeClustering(n_clusters=json_data.get("NumOfClusters"), affinity='precomputed', linkage='average')
                else:
                    logging.info("## Settingdefault value for number of clusters to 2 ##")
                    cluster = AgglomerativeClustering(n_clusters=2, affinity='precomputed', linkage='average')

                cluster.fit(distance_matrix)
                if json_data.get("Linkage") is not None:
                    link_matrix = linkage(distance_matrix, method=json_data.get("Linkage"), metric=json_data.get("Metric"))
                else:
                    link_matrix = linkage(distance_matrix, method='average', metric=json_data.get("Metric"))

            except:
                logging.error("!! Failed in hierarhical clustering !!")
                return False
            else:
                return {"FeatureSet": json_data.get("FeatureSet"), "Metric": json_data.get("Metric"), "DistanceMatrix": distance_matrix.tolist(), "LinkageMatrix": link_matrix.tolist(), "ClusterLabels": cluster.labels_.tolist()}