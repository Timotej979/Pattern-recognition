import logging, os, sys
import asyncio

from aiohttp import web


# Get environment variables
APP_CONFIG = os.getenv("APP_CONFIG")


class Frontend():
    """
        Frontend class controls routes the frontend requests to backend API 
    """

    routes = web.RouteTableDef()

    @routes.



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

