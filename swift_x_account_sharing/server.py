"""Sharing backend server module."""


import sys
import logging
import asyncio


import aiohttp.web
import uvloop


from .api import (
    has_access_handler,
    access_details_handler,
    gave_access_handler,
    shared_details_handler,
    share_container_handler,
    unshare_container_handler
)


from .dict_db import InMemDB


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


async def init_server():
    """Initialize the server."""
    app = aiohttp.web.Application()

    app["db_conn"] = InMemDB()

    app.add_routes([
        aiohttp.web.get("/has-access", has_access_handler),
        aiohttp.web.get("/access-details", access_details_handler),
        aiohttp.web.get("/gave-access", gave_access_handler),
        aiohttp.web.get("/shared-details", shared_details_handler),
        aiohttp.web.post("/share-container", share_container_handler),
        aiohttp.web.post("/unshare-container", unshare_container_handler),
    ])

    return app


def run_server_devel(app):
    """Run the server in development mode (without HTTPS)."""
    aiohttp.web.run_app(
        app,
        access_log=logging.getLogger("aiohttp.access"),
        port=8080
    )


if __name__ == "__main__":
    if sys.version_info < (3, 6):
        logging.error("swift-x-account-sharing requires >= python3.6")
        sys.exit(1)
    run_server_devel(init_server())
