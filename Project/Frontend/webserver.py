import logging, os, sys
import asyncio

from aiohttp import web


# Get environment variables
APP_CONFIG = os.getenv("APP_CONFIG")
URL_PREFIX = os.getenv("WEB_URL_PREFIX")

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

        try:
            formDataChunk = await request.post()
        except:
            log.exception("!! POST upload data error: Couldn't fetch request data !!\n")
            raise web.HTTPBadRequest("!! POST upload data error: Couldn't fetch request data !!\n")
        else:
            chunkIndex = formDataChunk['chunkIndex']
            totalChunks = formDataChunk['totalChunks']
            file = formDataChunk['file']

            if file.filename:
                log.info(file.file.read())
                # TODO

            if int(chunkIndex) == int(totalChunks) - 1:
                log.info("Last chunk")
                #log.info(file)

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
    # Initialization for API app object
    async def initialize(self):
        log.info("API initialization started")
        self.subapp = web.Application()  

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