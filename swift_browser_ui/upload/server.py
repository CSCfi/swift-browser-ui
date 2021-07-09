"""Server initialization functions."""


import os
import sys
import logging
import asyncio
import typing

import aiohttp.web
import aiohttp.client

import uvloop

from .middleware import add_cors
from .auth import handle_login, read_in_keys, handle_validate_authentication
from .api import handle_get_object, handle_get_container
from .api import handle_post_object_chunk, handle_post_object_options
from .api import handle_health_check


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))


async def servinit() -> aiohttp.web.Application:
    """Create an aiohttp server for handling the upload runner API."""
    middlewares: typing.List[typing.Coroutine] = [add_cors]  # type: ignore

    if not os.environ.get("SWIFT_UPLOAD_RUNNER_DISABLE_AUTH", None):
        middlewares.append(handle_validate_authentication)  # type: ignore

    app = aiohttp.web.Application(middlewares=middlewares)  # type: ignore

    app.on_startup.append(read_in_keys)
    app.on_shutdown.append(kill_client)

    # Add client session for aiohttp requests
    app["client"] = aiohttp.client.ClientSession()

    # Add auth related routes
    # Can use direct project post for creating a session, as it's intuitive
    # and POST upload against an account doesn't exist
    app.add_routes([aiohttp.web.post("/{project}", handle_login)])

    app.add_routes([aiohttp.web.get("/health", handle_health_check)])

    # Add api routes
    app.add_routes(
        [
            aiohttp.web.get("/{project}/{container}/{object_name:.*}", handle_get_object),
            aiohttp.web.get("/{project}/{container}", handle_get_container),
            aiohttp.web.post("/{project}/{container}", handle_post_object_chunk),
            aiohttp.web.options("/{project}/{container}", handle_post_object_options),
        ]
    )

    return app


async def kill_client(app: aiohttp.web.Application) -> None:
    """Kill the app client session."""
    await app["client"].close()


def run_server(app: typing.Union[typing.Coroutine, aiohttp.web.Application]) -> None:
    """Run the server."""
    aiohttp.web.run_app(
        app,
        access_log=aiohttp.web.logging.getLogger("aiohttp.access"),
        port=int(os.environ.get("SWIFT_UPLOAD_RUNNER_PORT", 9092)),
    )


def main() -> None:
    """."""
    run_server(servinit())


if __name__ == "__main__":
    if sys.version_info < (3, 6):
        logging.error("swift-upload-runner requires >= python3.6")
        sys.exit(1)
    run_server(servinit())
