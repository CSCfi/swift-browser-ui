"""swift_browser_ui server related convenience functions."""

# Generic imports
import logging
import sys
import asyncio
import ssl
import typing
import secrets
import base64

import cryptography.fernet

import uvloop
import aiohttp.web

import aiohttp_session
import aiohttp_session.cookie_storage

from swift_browser_ui.ui.front import index, browse, loginpassword
from swift_browser_ui.ui.login import (
    handle_login,
    handle_logout,
    sso_query_begin,
    sso_query_end,
    credentials_login_end,
)
from swift_browser_ui.ui.api import (
    swift_get_metadata_container,
    swift_list_containers,
    swift_list_objects,
    swift_download_object,
    swift_download_shared_object,
    swift_download_container,
    os_list_projects,
    get_os_user,
    get_access_control_metadata,
    remove_container_acl,
    add_project_container_acl,
    get_shared_container_address,
    swift_create_container,
    swift_delete_container,
    swift_replicate_container,
    swift_update_container_metadata,
    swift_get_project_metadata,
    remove_project_container_acl,
    get_upload_session,
)
from swift_browser_ui.ui.health import handle_health_check
from swift_browser_ui.ui.settings import setd
from swift_browser_ui.ui.middlewares import error_middleware
from swift_browser_ui.ui.discover import handle_discover
from swift_browser_ui.ui.signature import (
    handle_signature_request,
    handle_ext_token_create,
    handle_ext_token_list,
    handle_ext_token_remove,
)
from swift_browser_ui.ui.misc_handlers import handle_bounce_direct_access_request


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


async def open_client_to_app(app: aiohttp.web.Application) -> None:
    """Open a client session for download proxies."""
    app["api_client"] = aiohttp.ClientSession()


async def kill_dload_client(app: aiohttp.web.Application) -> None:
    """Kill download proxy client session."""
    await app["api_client"].close()


async def servinit(inject_middleware: typing.List[typing.Any]=[]) -> aiohttp.web.Application:
    """Create an aiohttp server with the correct arguments and routes."""
    middlewares = [error_middleware]
    if inject_middleware:
        middlewares = middlewares + inject_middleware
    app = aiohttp.web.Application(middlewares=middlewares)  # type: ignore

    # Initialize aiohttp_session
    app["seckey"] = base64.urlsafe_b64decode(cryptography.fernet.Fernet.generate_key())
    aiohttp_session.setup(
        app,
        aiohttp_session.cookie_storage.EncryptedCookieStorage(
            app["seckey"],
        ),
    )

    # Create a signature salt to prevent editing the signature on the client
    # side. Hash function doesn't need to be cryptographically secure, it's
    # just a convenient way of getting ascii output from byte values.
    app["Salt"] = secrets.token_hex(64)
    # Set application specific logging
    app["Log"] = logging.getLogger("swift-browser-ui")
    app["Log"].info("Set up logging for the swift-browser-ui application")

    # Setup static folder during development, if it has been specified
    if setd["static_directory"] is not None:
        app.router.add_static(
            "/static/",
            path=str(setd["static_directory"]),
            name="static",
            show_index=True,
        )

    app.add_routes(
        [
            aiohttp.web.get("/", index),
            aiohttp.web.get("/loginpassword", loginpassword),
            aiohttp.web.get("/browse", browse),
            # Route all URLs prefixed by /browse to the browser page, as this is
            # an spa
            aiohttp.web.get("/browse/{tail:.*}", browse),
        ]
    )

    # Add login routes
    app.add_routes(
        [
            aiohttp.web.get("/login", handle_login),
            aiohttp.web.get("/login/kill", handle_logout),
            aiohttp.web.get("/login/front", sso_query_begin),
            aiohttp.web.post("/login/return", sso_query_end),
            aiohttp.web.post("/login/websso", sso_query_end),
            aiohttp.web.post("/login/credentials", credentials_login_end),
        ]
    )

    # Add signature endpoint
    app.add_routes([aiohttp.web.get("/sign/{valid}", handle_signature_request)])

    # Add token functionality
    app.add_routes(
        [
            aiohttp.web.get("/token/{project}/{id}", handle_ext_token_create),
            aiohttp.web.delete("/token/{project}/{id}", handle_ext_token_remove),
            aiohttp.web.get("/token/{project}", handle_ext_token_list),
        ]
    )

    # Add api routes
    app.add_routes(
        [
            aiohttp.web.get("/api/username", get_os_user),
            aiohttp.web.get("/api/projects", os_list_projects),
            aiohttp.web.post(
                "/api/access/{project}/{container}", add_project_container_acl
            ),
            aiohttp.web.delete("/api/access/{project}/{container}", remove_container_acl),
            aiohttp.web.delete(
                "/api/access/{project}/{container}/{receiver}",
                remove_project_container_acl,
            ),
            aiohttp.web.get("/api/meta/{project}", swift_get_project_metadata),
            aiohttp.web.get(
                "/api/meta/{project}/{container}", swift_get_metadata_container
            ),
            aiohttp.web.get("/api/{project}", swift_list_containers),
            aiohttp.web.get("/api/{project}/acl", get_access_control_metadata),
            aiohttp.web.get("/api/{project}/address", get_shared_container_address),
            aiohttp.web.put("/api/{project}/{container}", swift_create_container),
            aiohttp.web.delete("/api/{project}/{container}", swift_delete_container),
            aiohttp.web.get("/api/{project}/{container}", swift_list_objects),
            aiohttp.web.get(
                "/api/{project}/{container}/{object:.*}", swift_download_object
            ),
            aiohttp.web.post(
                "/api/{project}/{container}", swift_update_container_metadata
            ),
        ]
    )

    # Add download routes
    app.add_routes(
        [
            aiohttp.web.get("/download/{project}/{container}", swift_download_container),
            aiohttp.web.get(
                "/download/{project}/{container}/{object:.*}",
                swift_download_shared_object,
            ),
        ]
    )

    # Add upload routes
    app.add_routes(
        [
            aiohttp.web.get("/upload/{project}/{container}", get_upload_session),
        ]
    )

    # Add replication routes
    app.add_routes(
        [
            aiohttp.web.post(
                "/replicate/{project}/{container}", swift_replicate_container
            ),
        ]
    )

    # Add discovery routes
    app.add_routes([aiohttp.web.get("/discover", handle_discover)])

    # Add direct routes
    app.add_routes(
        [aiohttp.web.get("/direct/request", handle_bounce_direct_access_request)]
    )

    # Add health check endpoint
    app.add_routes(
        [
            aiohttp.web.get("/health", handle_health_check),
        ]
    )

    app.on_startup.append(open_client_to_app)

    # Add graceful shutdown handler
    app.on_shutdown.append(kill_dload_client)

    return app


def run_server_secure(
    app: typing.Coroutine[typing.Any, typing.Any, aiohttp.web.Application],
    cert_file: str,
    cert_key: str,
) -> None:
    """
    Run the server securely with a given ssl context.

    While this function is incomplete, the project is safe to run in
    production only via a TLS termination proxy with e.g. NGINX.
    """
    # The ciphers are from the Mozilla project wiki, as a recommendation for
    # the most secure and up-to-date build.
    # https://wiki.mozilla.org/Security/Server_Side_TLS
    logger = logging.getLogger("swift-browser-ui")
    logger.debug("Running server securely.")
    logger.debug("Setting up SSL context for the server.")
    sslcontext = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
    cipher_str = (
        "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE"
        + "-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA"
        + "-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM"
        + "-SHA256:DHE-RSA-AES256-GCM-SHA384"
    )
    logger.debug(f"Setting following ciphers for SSL context: \n{cipher_str}")
    sslcontext.set_ciphers(cipher_str)
    sslcontext.options |= ssl.OP_NO_TLSv1
    sslcontext.options |= ssl.OP_NO_TLSv1_1
    logger.debug("Loading cert chain.")
    sslcontext.load_cert_chain(cert_file, cert_key)
    aiohttp.web.run_app(
        app,
        access_log=aiohttp.web.logging.getLogger("aiohttp.access"),
        port=setd["port"],  # type: ignore
        ssl_context=sslcontext,
    )


def run_server_insecure(
    app: typing.Coroutine[typing.Any, typing.Any, aiohttp.web.Application]
) -> None:
    """Run the server without https enabled."""
    aiohttp.web.run_app(
        app,
        access_log=aiohttp.web.logging.getLogger("aiohttp.access"),
        port=(setd["port"]),  # type: ignore
    )


if __name__ == "__main__":
    if sys.version_info < (3, 6):
        logging.error("swift-browser-ui requires >= python3.6")
        sys.exit(1)
    run_server_insecure(servinit())
