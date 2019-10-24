"""Sharing backend server module."""


import os
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
from .db import DBConn
from .cors import add_cors


logging.basicConfig(level=logging.DEBUG)


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


async def resume_on_start(app):
    """Resume old instance from start."""
    # If using dict_db read the database on disk, if it exists
    if (
            isinstance(app["db_conn"], InMemDB)
            and os.path.exists("swift-x-account-sharing.inmemdb")
    ):
        app["db_conn"].load_from_file("swift-x-account-sharing.inmemdb")
    if isinstance(app["db_conn"], DBConn):
        await app["db_conn"].open()


async def save_on_shutdown(app):
    """Flush the database on shutdown."""
    # If using dict_db dump the database on disk, using default file.
    if isinstance(app["db_conn"], InMemDB):
        app["db_conn"].export_to_file("swift-x-account-sharing.inmemdb")
    if isinstance(app["db_conn"], DBConn):
        await app["db_conn"].close()


async def init_server():
    """Initialize the server."""
    app = aiohttp.web.Application(
        middlewares=[add_cors]
    )

    app["db_conn"] = DBConn()

    await resume_on_start(app)

    app.add_routes([
        aiohttp.web.get("/access/{user}", has_access_handler),
        aiohttp.web.get("/access/{user}/{container}", access_details_handler),
        aiohttp.web.get("/share/{owner}", gave_access_handler),
        aiohttp.web.get("/share/{owner}/{container}", shared_details_handler),
        aiohttp.web.post("/share/{owner}/{container}",
                         share_container_handler),
        aiohttp.web.patch("/share/{owner}/{contanier}", edit_share_handler),
        aiohttp.web.delete("/share/{owner}/{container}", delete_share_handler),
    ])

    app.on_shutdown.append(save_on_shutdown)

    return app


def run_server_devel(app):
    """Run the server in development mode (without HTTPS)."""
    aiohttp.web.run_app(
        app,
        access_log=aiohttp.web.logging.getLogger("aiohttp.access"),
        port=9090
    )


def main():
    """Run the server with the default run function."""
    if sys.version_info < (3, 6):
        logging.error("swift-x-account-sharing requires >= python3.6")
        sys.exit(1)
    run_server_devel(init_server())


if __name__ == "__main__":
    main()
