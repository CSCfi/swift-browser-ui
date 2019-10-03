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
    delete_share_handler,
    edit_share_handler,
)


from .dict_db import InMemDB


logging.basicConfig(level=logging.DEBUG)


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


async def init_server():
    """Initialize the server."""
    app = aiohttp.web.Application()

    app["db_conn"] = InMemDB()

    app.add_routes([
        aiohttp.web.get("/access/{user}", has_access_handler),
        aiohttp.web.get("/access/{user}/{container}", access_details_handler),
        aiohttp.web.get("/share/{owner}", gave_access_handler),
        aiohttp.web.get("/share/{owner}/{container}", shared_details_handler),
        aiohttp.web.post("/share/{owner}/{container}", share_container_handler),
        aiohttp.web.patch("/share/{owner}/{contanier}", edit_share_handler),
        aiohttp.web.delete("/share/{owner}/{container}", delete_share_handler),
    ])

    return app


def run_server_devel(app):
    """Run the server in development mode (without HTTPS)."""
    aiohttp.web.run_app(
        app,
        access_log=aiohttp.web.logging.getLogger("aiohttp.access"),
        port=8080
    )


def main():
    """Run the server with the default run function."""
    if sys.version_info < (3, 6):
        logging.error("swift-x-account-sharing requires >= python3.6")
        sys.exit(1)
    run_server_devel(init_server())


if __name__ == "__main__":
    main()
