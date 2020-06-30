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
    handle_user_add_token,
    handle_user_delete_token,
    handle_user_list_tokens,
    handle_health_check,
)
from .db import DBConn
from .middleware import (
    add_cors,
    check_db_conn,
    catch_uniqueness_error
)
from .auth import (
    read_in_keys,
    handle_validate_authentication,
)
from .preflight import handle_delete_preflight


logging.basicConfig(level=logging.DEBUG)


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


async def resume_on_start(
        app: aiohttp.web.Application
):
    """Resume old instance from start."""
    await app["db_conn"].open()


async def save_on_shutdown(
        app: aiohttp.web.Application
):
    """Flush the database on shutdown."""
    if app["db_conn"] is not None:
        await app["db_conn"].close()


async def init_server() -> aiohttp.web.Application:
    """Initialize the server."""
    app = aiohttp.web.Application(
        middlewares=[
            add_cors,
            check_db_conn,
            handle_validate_authentication,
            catch_uniqueness_error,
        ]
    )

    app["db_conn"] = DBConn()

    app.add_routes([
        aiohttp.web.get("/health", handle_health_check),
    ])

    app.add_routes([
        aiohttp.web.get("/access/{user}", has_access_handler),
        aiohttp.web.get("/access/{user}/{container}", access_details_handler),
        aiohttp.web.get("/share/{owner}", gave_access_handler),
        aiohttp.web.get("/share/{owner}/{container}", shared_details_handler),
        aiohttp.web.post("/share/{owner}/{container}",
                         share_container_handler),
        aiohttp.web.patch("/share/{owner}/{contanier}", edit_share_handler),
        aiohttp.web.delete("/share/{owner}/{container}",
                           delete_share_handler),
        aiohttp.web.options("/share/{owner}/{container}",
                            handle_delete_preflight),
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
    app.on_shutdown.append(save_on_shutdown)

    return app


def run_server_devel(
        app: aiohttp.web.Application
):
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
