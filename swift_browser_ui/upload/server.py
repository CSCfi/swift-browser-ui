"""Server initialization functions."""


import asyncio
import logging
import os
import sys
import typing

import aiohttp.client
import aiohttp.web
import uvloop

import swift_browser_ui.common.common_middleware
import swift_browser_ui.common.common_util
from swift_browser_ui.common.vault_client import VaultClient
from swift_browser_ui.upload.api import (
    handle_batch_add_sharing_whitelist,
    handle_batch_remove_sharing_whitelist,
    handle_check_sharing_whitelist,
    handle_delete_project_whitelist,
    handle_get_container,
    handle_get_object,
    handle_health_check,
    handle_object_header,
    handle_post_object_chunk,
    handle_post_object_options,
    handle_project_key,
    handle_project_whitelist,
    handle_upload_encrypted_object,
    handle_upload_encrypted_object_options,
    handle_upload_encrypted_object_ws,
    handle_whitelist_options,
)
from swift_browser_ui.upload.auth import (
    handle_login,
    handle_logout,
    handle_validate_authentication,
)
from swift_browser_ui.upload.common import VAULT_CLIENT

# temporarily ignore typecheck from mypy until
# this issue is fixed https://github.com/MagicStack/uvloop/issues/575
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())  # type: ignore


logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))


async def servinit() -> aiohttp.web.Application:
    """Create an aiohttp server for handling the upload runner API."""
    middlewares: typing.List[typing.Any] = [
        swift_browser_ui.common.common_middleware.add_cors,
        swift_browser_ui.common.common_middleware.error_handler,
    ]

    if not os.environ.get("SWIFT_UPLOAD_RUNNER_DISABLE_AUTH", None):
        middlewares.append(handle_validate_authentication)

    app = aiohttp.web.Application(middlewares=middlewares)

    async def on_prepare(
        _: aiohttp.web.Request, response: aiohttp.web.StreamResponse
    ) -> None:
        """Modify Server headers."""
        response.headers["Server"] = "Swift Browser Runner"

    # add custom response headers
    app.on_response_prepare.append(on_prepare)

    app.on_startup.append(swift_browser_ui.common.common_util.read_in_keys)
    app.on_shutdown.append(kill_client)

    # Add client session for aiohttp requests
    http_client = aiohttp.client.ClientSession()
    app["client"] = http_client
    app[VAULT_CLIENT] = VaultClient(http_client)

    app.add_routes([aiohttp.web.get("/health", handle_health_check)])

    # Add auth related routes
    # Can use direct project post for creating a session, as it's intuitive
    # and POST upload against an account doesn't exist
    app.add_routes(
        [
            aiohttp.web.post("/{project}", handle_login),
            aiohttp.web.delete("/{project}", handle_logout),
        ]
    )

    # Add api routes
    app.add_routes(
        [
            aiohttp.web.options(
                "/cryptic/{project}/{container}/{object_name:.*}",
                handle_upload_encrypted_object_options,
            ),
            aiohttp.web.put(
                "/cryptic/{project}/{container}/{object_name:.*}",
                handle_upload_encrypted_object,
            ),
            aiohttp.web.get(
                "/cryptic/{project}/{container}/{object_name:.*}",
                handle_upload_encrypted_object_ws,
            ),
            aiohttp.web.options(
                "/header/{project}/{container}/{object_name:.*}",
                handle_upload_encrypted_object_options,
            ),
            aiohttp.web.get(
                "/header/{project}/{container}/{object_name:.*}",
                handle_object_header,
            ),
            aiohttp.web.get(
                "/cryptic/{project}/keys",
                handle_project_key,
            ),
            aiohttp.web.options(
                "/cryptic/{project}/whitelist",
                handle_whitelist_options,
            ),
            aiohttp.web.put(
                "/cryptic/{project}/whitelist",
                handle_project_whitelist,
            ),
            aiohttp.web.delete(
                "/cryptic/{project}/whitelist",
                handle_delete_project_whitelist,
            ),
            aiohttp.web.put(
                "/cryptic/{project}/{container}",
                handle_batch_add_sharing_whitelist,
            ),
            aiohttp.web.delete(
                "/cryptic/{project}/{container}",
                handle_batch_remove_sharing_whitelist,
            ),
            aiohttp.web.get(
                "/check/{project}/{container}/{receiver}",
                handle_check_sharing_whitelist,
            ),
            aiohttp.web.options(
                "/cryptic/{project}/{container}",
                handle_whitelist_options,
            ),
        ]
    )

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


def run_server(
    app: typing.Coroutine[typing.Any, typing.Any, aiohttp.web.Application]
) -> None:
    """Run the server."""
    aiohttp.web.run_app(
        app,
        access_log=logging.getLogger("aiohttp.access"),
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
