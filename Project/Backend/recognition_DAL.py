import logging, json

from sqlalchemy import select, delete

from db_model import Feature_set, Features

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










