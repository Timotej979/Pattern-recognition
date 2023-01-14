import logging, os, sys, json
import asyncio

from aiohttp import web, ClientSession

# Get environment variables
APP_CONFIG = os.getenv("APP_CONFIG")
URL_PREFIX = os.getenv("WEB_URL_PREFIX")
API_CONNECTION_STRING = os.getenv("API_WEB_CONNECTION_STRING")

class WebService():
    """
        Frontend class controls routes the frontend requests to backend API 
    """

    # Configure rotes table and all available methods
    routes = web.RouteTableDef()

    # Index webpage
    @routes.get('/uploadPage')
    async def uploadPage(request):
        return web.FileResponse("./web/upload_page.html")

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

                        # Create JSON for database upload request
                        uploadLinesJSONDict = {"FeatureSet": file.filename, "Features": uploadLinesList}
                        uploadLinesJSON = json.dumps(uploadLinesJSONDict)

                        log.info(API_CONNECTION_STRING)

                        # Make an async request to API
                        async with ClientSession() as session:
                            async with session.post(API_CONNECTION_STRING + "/uploadFeatureSet", json = uploadLinesJSON) as resp:
                                if resp.status != 200:
                                    print(f'Error: {resp.status}')
                                    return web.HTTPBadRequest()
                                else:
                                    response = await resp.json()
                                    log.info("## DB request response: {} ##".format(response))
                except:
                    log.exception("!! POST upload data error: Couldn't upload data to DB !!\n")
                    return web.HTTPServerError()
                else:
                    return web.HTTPOk()

    @routes.get('/pcaPage')
    async def pcaPage(request):
        return web.Response(text = "Got pca page")

    @routes.get('/optimizedPcaPage')
    async def optimizedPcaPage(request):
        return web.Response(text = "Got optimized pca page")

    @routes.get('/hierarhicalClusteringPage')
    async def hierarhicalClusteringPage(request):
        return web.Response(text = "Got hierarhical clustering page")

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