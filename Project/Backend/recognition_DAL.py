import logging, json, re

import numpy as np

from sqlalchemy import select, delete
from db_model import Feature_set, Features

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score


class Recognition_DAL():

    # POST upload feature set
    async def upload_feature_set(session, json_data):
        async with session.begin():
            logging.info("## Session connected ##")

            uploadFeatureSetCheck = await session.execute(select(Feature_set).where(Feature_set.name == json_data.get("FeatureSet")).exists().select())

            if uploadFeatureSetCheck.fetchone()[0] is False:
                logging.info("    + " + str(json_data.get("FeatureSet")))

                newFeatureSet = Feature_set(name = json_data.get("FeatureSet"))

                logging.info(list(json_data.get("Features")))

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
            
            if listOfFeatureSets != None:
                listOfFeatureSetsJSON = {"FeatureSets": [element[0] for element in tuple(listOfFeatureSets.fetchall())]}
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

        # Parser for features with strings in them
        listOfFeatureNames = []

        for i in range(len(listOfFeatures)):
            for j in range(len(listOfFeatures[i])):
                try:
                    listOfFeatures[i][j] = float(listOfFeatures[i][j])
                except ValueError:
                    listOfFeatureNames.append(str(listOfFeatures[i][j])) 
                    listOfFeatures[i].pop() 

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

        return {"FeatureSet": json_data.get("FeatureSet"), "X_original": X_normalised.tolist(), "X_pca": X_pca.tolist(), "ExplainedVariance": explained_variance.tolist(), "1-NNScoreOriginal": scores_original.tolist(), "1-NNScorePCA": scores_pca.tolist()}

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

        # Parser for features with strings in them
        listOfFeatureNames = []

        for i in range(len(listOfFeatures)):
            for j in range(len(listOfFeatures[i])):
                try:
                    listOfFeatures[i][j] = float(listOfFeatures[i][j])
                except ValueError:
                    listOfFeatureNames.append(str(listOfFeatures[i][j]))
                    listOfFeatures[i].pop()

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

        return {"FeatureSet": json_data.get("FeatureSet"), "OptimalNumOfComponents": int(optimalNumOfComponents), "X_optimal_pca": X_optimal_pca.tolist(), "ExplainedVariance": explained_variance.tolist(), "1-NNScoreOriginal": scores_original.tolist(), "1-NNScorePCA": scores_pca.tolist()}


