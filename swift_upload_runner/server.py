"""Server initialization functions."""


import os
import sys
import logging
import asyncio

import aiohttp.web

import uvloop

from .middleware import add_cors
from .auth import handle_login, read_in_keys, handle_validate_authentication
from .api import handle_get_object


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


async def servinit() -> aiohttp.web.Application:
    """Create an aiohttp server for handling the upload runner API."""
    app = aiohttp.web.Application(middlewares=[
        add_cors,
        handle_validate_authentication
    ])

    app.on_startup.append(read_in_keys)

    # Add auth related routes
    # Can use direct project post for creating a session, as it's intuitive
    # and POST upload against an account doesn't exist
    app.add_routes([
        aiohttp.web.post("/{project}", handle_login)
    ])

    # Add api routes
    app.add_routes([
        aiohttp.web.get("/{project}/{container}/{object_name}",
                        handle_get_object),
    ])

    return app


def run_server(
        app: aiohttp.web.Application
):
    """Run the server."""
    aiohttp.web.run_app(
        app,
        access_log=aiohttp.web.logging.getLogger("aiohttp.access"),
        port=os.environ.get("SWIFT_UPLOAD_RUNNER_PORT", 9092)
    )


if __name__ == '__main__':
    if sys.version_info < (3, 6):
        logging.error("swift-upload-runner requires >= python3.6")
        sys.exit(1)
    run_server(servinit())
