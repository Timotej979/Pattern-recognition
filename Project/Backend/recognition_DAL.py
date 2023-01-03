import logging, json, re

import numpy as np

from sqlalchemy import select, delete
from db_model import Feature_set, Features

from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


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

                        featureCheck = await session.execute(select(Features).where(Features.feature == element).exists().select())

                        if featureCheck.fetchone()[0] is False:
                            newFeature = Features(feature = element)
                            newFeatureSet.feature_children.append(newFeature)
                            session.add(newFeature)
                        else:
                            newFeature = await session.execute(select(Features).where(Features.feature == element))
                            newFeatureSet.feature_children.append(newFeature)

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
    # GET exercise 1
    async def exercise1(session, json_data):
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

        logging.info(listOfFeatures)
        logging.info(listOfFeatureNames)

        # Pricipal Component Analysis
        numpyFeaturesList = np.array(listOfFeatures)
         
        X_train, X_test, y_train, y_test = train_test_split(numpyFeaturesList, listOfFeatureNames, test_size = 0.5, random_state = 42)

        sc = StandardScaler()
        X_train = sc.fit_transform(X_train)
        X_test = sc.fit_transform(X_test)

        pca = PCA(n_components = json_data.get("NumOfComponents"))

        X_train = pca.fit_transform(X_train)
        X_test = pca.fit_transform(X_test)

        explained_variance = pca.explained_variance_ratio_

        logging.info(explained_variance)

        return True









