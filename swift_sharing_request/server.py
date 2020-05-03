"""Share request backend module."""


import sys
import logging
import asyncio

import aiohttp.web
import uvloop

from .middleware import (
    add_cors,
    check_db_conn,
    catch_uniqueness_error,
)
from .api import (
    handle_share_request_post,
    handle_user_owned_request_listing,
    handle_user_made_request_listing,
    handle_container_request_listing,
    handle_user_share_request_delete,
    handle_user_add_token,
    handle_user_delete_token,
    handle_user_list_tokens
)
from .db import DBConn
from .preflight import handle_delete_preflight
from .auth import (
    read_in_keys,
    handle_validate_authentication,
)


logging.basicConfig(level=logging.DEBUG)
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


async def resume_on_start(
        app: aiohttp.web.Application
):
    """Resume old instance on start."""
    await app["db_conn"].open()


async def graceful_shutdown(
        app: aiohttp.web.Application
):
    """Correctly close the service."""
    if app["db_conn"] is not None:
        await app["db_conn"].close()


async def init_server() -> aiohttp.web.Application:
    """Initialize the sharing request server."""
    app = aiohttp.web.Application(
        middlewares=[
            add_cors,
            check_db_conn,
            handle_validate_authentication,
            catch_uniqueness_error,
        ]
    )

    app["db_conn"] = DBConn()
    app["tokens"] = []

    app.add_routes([
        aiohttp.web.options("/request/user/{user}/{container}",
                            handle_delete_preflight),
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

    app.add_routes([
        aiohttp.web.options("/token/{project}/{id}",
                            handle_delete_preflight),
        aiohttp.web.post("/token/{project}/{id}", handle_user_add_token),
        aiohttp.web.delete("/token/{project}/{id}", handle_user_delete_token),
        aiohttp.web.get("/token/{project}", handle_user_list_tokens),
    ])

    app.on_startup.append(resume_on_start)
    app.on_startup.append(read_in_keys)
    app.on_shutdown.append(graceful_shutdown)

    return app


def run_server_devel(
        app: aiohttp.web.Application
):
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
