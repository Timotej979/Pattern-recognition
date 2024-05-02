import logging, os, sys, json
import asyncio

from aiohttp import web, ClientSession

# Get environment variables
APP_CONFIG = os.getenv("APP_CONFIG")
URL_PREFIX = os.getenv("WEB_URL_PREFIX")
API_CONNECTION_STRING = os.getenv("API_WEB_CONNECTION_STRING")
API_MAX_CHUNK_SIZE = int(os.getenv("WEB_API_REQUEST_MAX_CHUNK_SIZE"))

class WebService():
    """
        Frontend class controls routes the frontend requests to backend API 
    """

    # Configure rotes table and all available methods
    routes = web.RouteTableDef()

    # Healthcheck
    @routes.get('/healthz')
    async def healthz(request):
        log.info("WEB healthcheck running...")
        return web.Response(text="## WEB healthcheck successfull ##\n")

    # Index webpage
    @routes.get('/dashboard')
    async def uploadPage(request):
        return web.FileResponse("./web/dashboard.html")

    @routes.post('/uploadData')
    async def uploadData(request):
        log.info("## POST uploadData received ##")

        # Get global variable from app object and write the whole response into it by every chunk
        uploadChunkedList = request.app['uploadChunkedList']

        try:
            formDataChunk = await request.post()
        except:
            log.exception("!! POST upload data error: Couldn't fetch request data !!\n")
            raise web.HTTPBadRequest("!! POST upload data error: Couldn't fetch request data !!\n")
        else:
            try:
                # Get data in chunks
                chunkIndex = formDataChunk['chunkIndex']
                totalChunks = formDataChunk['totalChunks']
                file = formDataChunk['file']
                fileName = str(formDataChunk['fileName'])

                if file.filename:
                    log.info("## Chunk number: {} ##".format(int(chunkIndex)))
                    uploadChunkedList.append(str(file.file.read()))
            except:
                log.exception("!! POST upload data error: Couldn't fetch chunk of data !!\n")
                raise web.HTTPBadRequest("!! POST upload data error: Couldn't fetch request data !!\n")
            else:
                try:
                    if int(chunkIndex) == int(totalChunks) - 1:
                        uploadChunkedList.append(str(file.file.read()))
                        log.info("## Last chunk: {} ##".format(int(chunkIndex)))
                        
                        # Upload data to database
                        uploadedChunkString = "".join(uploadChunkedList)
                        uploadChunkLines = uploadedChunkString.split("\\n")

                        uploadLinesList = []
                        for line in uploadChunkLines:
                            if ("b" or "'b'" or '') not in line:
                                uploadLinesList.append(line)

                        # Pop last element because it is always empty
                        uploadLinesList.pop()

                        # Determine wether we should single/chunk upload data to API
                        if sys.getsizeof(uploadLinesList) > API_MAX_CHUNK_SIZE:
                            log.info("## Initializing chunked upload to API ##")

                            # Determine how many chunks there should be using max size and modulus
                            numberOfListSplits = sys.getsizeof(uploadLinesList) % API_MAX_CHUNK_SIZE

                            for index in range(0, numberOfListSplits):
                                if index == 0:
                                    # Create JSON for database upload request
                                    uploadLinesJSON = {"FeatureSet": fileName, "Features": uploadLinesList[index::numberOfListSplits]}

                                    # Make an async request to API
                                    async with ClientSession() as session:
                                        async with session.post(API_CONNECTION_STRING + "/uploadFeatureSet", json = uploadLinesJSON, headers = {'Content-Type': 'application/json'}) as resp:
                                            if resp.status != 200:
                                                log.exception("!! POST upload data error: Failed chunk upload !!\n")
                                                return web.HTTPBadRequest("!! POST upload data error: Failed chunk upload !!\n")
                                            else:
                                                response = await resp.json()
                                                log.info("## DB request response: {} ##".format(response))
                                else:
                                    # Create JSON for database upload request
                                    uploadLinesJSON = {"FeatureSet": fileName, "Features": uploadLinesList[index::numberOfListSplits]}

                                    # Make an async request to API
                                    async with ClientSession() as session:
                                        async with session.post(API_CONNECTION_STRING + "/extendFeatureSet", json = uploadLinesJSON, headers = {'Content-Type': 'application/json'}) as resp:
                                            if resp.status != 200:
                                                log.exception("!! POST upload data error: Failed chunk upload !!\n")
                                                return web.HTTPBadRequest("!! POST upload data error: Failed chunk upload !!\n")
                                            else:
                                                response = await resp.json()
                                                log.info("## DB request response: {} ##".format(response))                            
                        else:
                            log.info("## Initializing single upload to API ##")
            
                            # Create JSON for database upload request
                            uploadLinesJSON = {"FeatureSet": fileName, "Features": uploadLinesList}

                            log.info(API_CONNECTION_STRING)

                            # Make an async request to API
                            async with ClientSession() as session:
                                async with session.post(API_CONNECTION_STRING + "/uploadFeatureSet", json = uploadLinesJSON, headers = {'Content-Type': 'application/json'}) as resp:
                                    if resp.status != 200:
                                        log.exception("!! POST upload data error: Failed single upload !!\n")
                                        return web.HTTPBadRequest("!! POST upload data error: Failed single upload !!\n")
                                    else:
                                        response = await resp.json()
                                        log.info("## DB request response: {} ##".format(response))
                except:
                    log.exception("!! POST upload data error: Couldn't upload data to DB !!\n")
                    return web.HTTPServerError("!! POST upload data error: Couldn't upload data to DB !!\n")
                else:
                    return web.HTTPOk()

    @routes.get('/getFeatureSets')
    async def getFeatureSets(request):
        log.info("## GET getFeatureSets received ##")

        try:
            # Make an async request to API
            async with ClientSession() as session:
                async with session.get(API_CONNECTION_STRING + "/getListOfFeatureSets") as resp:
                    if resp.status != 200:
                        log.exception("!! GET getFeatureSets error: Failed to fetch feature sets !!\n")
                        return web.HTTPBadRequest("!! GET getFeatureSets error: Failed to fetch feature sets !!\n")
                    else:
                        response = await resp.json()
                        log.info("## DB request response: {} ##".format(response))
        except:
            log.exception("!! GET getFeatureSets error: Couldn't fetch feature sets from DB !!\n")
            return web.HTTPServerError("!! GET getFeatureSets error: Couldn't fetch feature sets from DB !!\n")
        else:
            return web.json_response(response)

    ############################################################################################################################################
    ############################################################################################################################################
    # Initialization for API app object
    async def initialize(self):
        log.info("API initialization started")
        self.subapp = web.Application()  

        log.info("Adding routes to application object")
        self.subapp.router.add_routes(self.routes)

        # Add global upload chunk array to application object
        self.subapp['uploadChunkedList'] = []

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
    server = WebService()
    loop.run_until_complete(server.initialize())

    # Start the server
    server.start_server(host='0.0.0.0', port=4000, loop=loop)