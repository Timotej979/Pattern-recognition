import logging, os, sys

import asyncio, asyncpg
import aiohttp_sqlalchemy as ahsa

from aiohttp import web
from sqlalchemy.ext.asyncio import create_async_engine

from recognition_DAL import Recognition_DAL
from db_model import metadata


# Get environment variables
APP_CONFIG = os.getenv("APP_CONFIG")
URL_PREFIX = os.getenv("API_URL_PREFIX")
DB_URI = str(os.getenv("API_DB_CONNECTION_STRING"))
DB_MAX_CONNECTIONS = int(os.getenv("API_DB_MAX_CONNECTIONS"))
DB_POOL_RECYCLE = int(os.getenv("API_DB_POOL_RECYCLE"))
DB_MAX_OVERFLOW = int(os.getenv("API_DB_MAX_OVERFLOW"))
DB_POOL_TIMEOUT = int(os.getenv("API_DB_POOL_TIMEOUT"))

#########################################################################
### API CLASS ###
class API_Server():
    """
    API_Server class controls the behaviour of API server
    """
    
    # Configure routes table and all available methods
    routes = web.RouteTableDef()

    # Healthcheck
    @routes.get('/healthz')
    async def health_check(request):
        log.info("Api test running\n")
        return web.Response(text="## API test successfull ##\n")


    ######################################################## API METHODS ###############################################################
    # Upload feature set
    @routes.post('/uploadFeatureSet')
    async def upload_feature_set(request):
        log.info("## POST upload feature set ##")

        try:
            postUploadedFeatureSetJSON = await request.json()
        except:
            log.exception("!! POST upload feature set error: Couldn't fetch request data !!\n")
            raise web.HTTPBadRequest("!! POST upload feature set error: Couldn't fetch request data !!\n")
        else:
            try:
                session = ahsa.get_session(request)
            except:
                log.exception("!! POST upload feature set error: Couldn't get SQLAlchemy ORM session !!\n")
                raise web.HTTPServiceUnavailable("!! POST upload feature set error: Couldn't get SQLAlchemy ORM session !!\n")
            else:
                try:
                    if await Recognition_DAL.upload_feature_set(session, postUploadedFeatureSetJSON):
                        return web.json_response({"status": 200, "messsage": "POST upload feature set successful"}) 
                    else:
                        return web.json_response({"status": 404, "message": "Requested upload feature set already exists"})
                except:
                    logging.exception("!! POST upload feature set error: Writing to DB error !!\n")
                    raise web.HTTPInternalServerError(body = "!! POST upload feature set error: Writing to DB error !!\n")

    # Extend existing feature set
    @routes.post('/extendFeatureSet')
    async def extend_feature_set(request):
        log.info("## POST extend feature set ##")

        try:
            postExtendFeatureSetJSON = await request.json()
        except:
            log.exception("!! POST extend feature set error: Couldn't fetch request data !!\n")
            raise web.HTTPBadRequest("!! POST extend feature set error: Couldn't fetch request data !!\n")
        else:
            try:
                session = ahsa.get_session(request)
            except:
                log.exception("!! POST extend features error: Couldn't get SQLAlchemy ORM session !!\n")
                raise web.HTTPServiceUnavailable("!! POST extend features error: Couldn't get SQLAlchemy ORM session !!\n")
            else:
                try:
                    if await Recognition_DAL.extend_feature_set(session, postExtendFeatureSetJSON):
                        return web.json_response({"status": 200, "messsage": "POST extend feature set successful"}) 
                    else:
                        return web.json_response({"status": 404, "message": "Requested extend feature set doesn't exists"})
                except:
                    logging.exception("!! POST extend feature set error: Writing to DB error !!\n")
                    raise web.HTTPInternalServerError(body = "!! POST extend feature set error: Writing to DB error !!\n")

    # Delete feature set
    @routes.delete('/deleteFeatureSet')
    async def delete_feature_set(request):
        log.info("## DELETE feature set ##")

        try:
            deleteFeatureSetJSON = await request.json()
        except:
            log.exception("!! DELETE feature set error: Couldn't fetch requested data !!\n")
            raise web.HTTPBadRequest("!! DELETE feature set error: Couldn't fetch requested data !!\n")
        else:
            try:
                session = ahsa.get_session(request)
            except:
                log.exception("!! DELETE feature set error: Couldn't get SQLAlchemy ORM session !!\n")
                raise web.HTTPServiceUnavailable("!! DELETE feature set error: Couldn't get SQLAlchemy ORM session !!\n")
            else:
                try:
                    if await Recognition_DAL.delete_feature_set(session, deleteFeatureSetJSON):
                        return web.json_response({"status": 200, "messsage": "DELETE feature set successful"})
                    else:
                        return web.json_response({"status": 404, "message": "Requested delete feature set already deleted"})
                except:
                    log.exception("!! DELETE feature set error: Writing to DB error !!\n")
                    raise web.HTTPInternalServerError(body = "!! DELETE feature set error: Writing to DB error !!\n")

    # Get list of all feature sets in DB
    @routes.get('/getListOfFeatureSets')
    async def get_list_of_feature_sets(request):
        log.info('## GET list of feature sets ##')
        
        try:
            session = ahsa.get_session(request)
        except:
            log.exception("!! GET list of feature sets error: Couldn't get SQLAlchemy ORM session !!\n")
            raise web.HTTPServiceUnavailable("!! GET list of feature sets error: Couldn't get SQLAlchemy ORM session !!\n")
        else:
            try:
                listOfFeatureSetsJSON = await Recognition_DAL.get_list_of_all_feature_sets(session)

                if listOfFeatureSetsJSON != False:
                    return web.json_response({"status": 200, "message": listOfFeatureSetsJSON})
                else:
                    return web.json_response({"status": 404, "message": "No feature sets found"})
            except:
                log.exception("!! GET list of feature sets error: Reading from DB error !!\n")
                raise web.HTTPInternalServerError(body = "!! GET list of feature sets error: Reading from DB error !!\n")


    ################################# RECOGNITION METHODS #################################
    # Get PCA
    @routes.get('/principalComponentAnalysis')
    async def PCA(request):
        log.info('## GET PCA ##')

        try:
            featureSetJSON = await request.json()
        except:
            log.exception("!! GET PCA error: Couldn't fetch requested data !!\n")
            raise web.HTTPBadRequest("!! GET PCA error: Couldn't fetch requested data !!\n")
        else:
            try:
                session = ahsa.get_session(request)
            except:
                log.exception("!! GET PCA error: Couldn't get SQLAlchemy ORM session !!\n")
                raise web.HTTPServiceUnavailable("!! GET PCA error: Couldn't get SQLAlchemy ORM session !!\n")
            else:
                try:
                    resultJSON = await Recognition_DAL.principalComponentAnalysis(session, featureSetJSON)

                    if resultJSON == False:
                        return web.json_response({"status": 404, "message": "No feature set found"})
                    else:
                        return web.json_response({"status": 200, "message": resultJSON})
                except:
                    log.exception("!! GET PCA error: Reading from DB error !!\n")
                    raise web.HTTPInternalServerError(body = "!! GET PCA error: Reading from DB error !!\n")

    # Get optimized PCA
    @routes.get('/optimizedPrincipalComponentAnalysis')
    async def optimizedPCA(request):
        log.info('## GET optimized PCA ##')

        try:
            featureSetJSON = await request.json()
        except:
            log.info("!! Get optimized PCA error: Couldn't fetch requested data !!\n")
            raise web.HTTPBadRequest("!! Get optimized PCA error: Couldn't fetch requested data !!\n")
        else:
            try:
                session = ahsa.get_session(request)
            except:
                log.exception("!! GET optimized PCA error: Couldn't get SQLAlchemy ORM session !!\n")
                raise web.HTTPServiceUnavailable("!! GET optimized PCA error: Couldn't get SQLAlchemy ORM session !!\n")
            else:
                try:
                    resultJSON = await Recognition_DAL.optimizedPrincipalComponentAnalysis(session, featureSetJSON)

                    if resultJSON == False:
                        return web.json_response({"status": 404, "message": "No feature set found"})
                    else:
                        return web.json_response({"status": 200, "message": resultJSON})
                except:
                    log.exception("!! GET optimized PCA error: Reading from DB error !!\n")
                    raise web.HTTPInternalServerError("!! GET optimized PCA error: Reading from DB error !!\n")   

    @routes.get('/hierarhicalClustering')
    async def hierahicalClustering(request):
        log.info('## GET hierarhical clustering ##')

        try:
            featureSetJSON = await request.json()
        except:
            log.info("!! GET hierarhical clusetring error: Couldn't fetch requested data !!\n")
            raise web.HTTPBadRequest("!! GET hierarhical clusetring error: Couldn't fetch requested data !!\n")
        else:
            try:
                session = ahsa.get_session(request)
            except:
                log.exception("!! GET hierarhical clusetring error: Couldn't get SQLAlchemy ORM session !!\n")
                raise web.HTTPServiceUnavailable("!! GET hierarhical clusetring error: Couldn't get SQLAlchemy ORM session !!\n")
            else:
                try:
                    resultJSON = await Recognition_DAL.hierarhicalClustering(session, featureSetJSON)

                    if resultJSON == False:
                        return web.json_response({"status": 404, "message": "No feature set found"})
                    else:
                        return web.json_response({"status": 200, "message": resultJSON})
                except:
                    log.exception("!! GET hierarhical clusetring error: Reading from DB error !!\n")


    ############################################################################################################################################
    # Initialization for API app object
    async def initialize(self):
        log.info("API initialization started")
        self.subapp = web.Application()  

        log.info("Configuring API SQLAlchemy engine")
        self.subapp['engine'] = create_async_engine(DB_URI, 
                                                    echo = (False if APP_CONFIG == 'prod' else True),
                                                    connect_args={"server_settings": {"jit": "off"}},
                                                    pool_pre_ping=True, 
                                                    pool_size=DB_MAX_CONNECTIONS,
                                                    pool_recycle=DB_POOL_RECYCLE,
                                                    max_overflow=DB_MAX_OVERFLOW,
                                                    pool_timeout=DB_POOL_TIMEOUT)
        
        log.info("Binding SQLAlchemy engine to application object")
        ahsa.setup(self.subapp, [ahsa.bind(DB_URI)])

        log.info("Creating DB tables")
        await ahsa.init_db(self.subapp, metadata)

        log.info("Adding routes to application object")
        self.subapp.router.add_routes(self.routes)

        # Add sub-app to set the IP/recognition-api request
        self.app = web.Application()
        self.app.add_subapp(URL_PREFIX, self.subapp)

        log.info("API initialization complete")

    # Run API
    def start_server(self, host, port, loop):
        log.info("Server starting on address: http://{}:{}".format(host, port))
        web.run_app(self.app, host=host, port=port, loop=loop)


if __name__ == '__main__':
    # Set up operation mode for server
    if APP_CONFIG == 'dev':
        # Development build
        logging.basicConfig(level=logging.DEBUG)
        DB_MAX_CONNECTIONS = 10
        DB_POOL_RECYCLE = 3600
        DB_MAX_OVERFLOW = 0
        DB_POOL_TIMEOUT = 60
        log = logging.getLogger()
        log.info("Running in development config")

    elif APP_CONFIG == 'prod':
        # Production build
        logging.basicConfig(level=logging.INFO)
        log = logging.getLogger()
        log.info("Running in production config")

    else:
        # If APP_CONFIG env variable is not set abort start
        logging.basicConfig(level=logging.INFO)
        log = logging.getLogger()
        log.info("Environment variable APP_CONFIG is not set (Current value is: {}), please set it in  the environment file".format(APP_CONFIG))
        sys.exit(1)

    # Get asyncio loop
    loop = asyncio.get_event_loop()

    # Create WebServer object and initialize it
    server = API_Server()
    loop.run_until_complete(server.initialize())

    # Start the server
    server.start_server(host='0.0.0.0', port=5000, loop=loop)
    



