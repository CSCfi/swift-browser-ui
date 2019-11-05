"""Share request backend module."""


import sys
import logging
import asyncio

import aiohttp.web
import uvloop

from .middleware import (
    add_cors,
    check_db_conn
)
from .api import (
    handle_share_request_post,
    handle_user_owned_request_listing,
    handle_user_made_request_listing,
    handle_container_request_listing,
    handle_user_share_request_delete
)


logging.basicConfig(level=logging.DEBUG)
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


async def resume_on_start(app):
    """Resume old instance on start."""
    await app["db_conn"].open()


async def graceful_shutdown(app):
    """Correctly close the service."""
    if app["db_conn"] is not None:
        await app["db_conn"].close()


async def init_server():
    """Initialize the sharing request server."""
    app = aiohttp.web.Application(
        middlewares=[add_cors, check_db_conn]
    )

    app.add_routes([
        aiohttp.web.post("/request/user/{user}/{container}",
                         handle_share_request_post),
        aiohttp.web.delete("/request/user/{user}/{container}",
                           handle_user_share_request_delete),
        aiohttp.web.get("/request/user/{user}",
                        handle_user_made_request_listing),
        aiohttp.web.get("/request/owner/{user}",
                        handle_user_owned_request_listing),
        aiohttp.web.get("/request/container/{container}",
                        handle_container_request_listing),
    ])

    app.on_startup.append(resume_on_start)
    app.on_shutdown.append(graceful_shutdown)

    return app


def run_server_devel(app):
    """Run the server in development mode (without HTTPS)."""
    aiohttp.web.run_app(
        app,
        access_log=aiohttp.web.logging.getLogger("aiohttp.access"),
        port=9091
    )


def main():
    """Run the server with the default run function."""
    if sys.version_info < (3, 6):
        logging.error("swift-sharing-request requires >= python3.6")
        sys.exit(1)
    run_server_devel(init_server())


if __name__ == "__main__":
    run_server_devel(init_server())
