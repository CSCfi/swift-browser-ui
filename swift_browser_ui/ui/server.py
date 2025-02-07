"""swift_browser_ui server related convenience functions."""

# Generic imports
import asyncio
import base64
import logging
import secrets
import ssl
import sys
import typing

import aiohttp.web
import aiohttp_session
import aiohttp_session.redis_storage
import cryptography.fernet
import uvloop
from oidcrp.rp_handler import RPHandler

import swift_browser_ui.ui.middlewares
from swift_browser_ui.ui._convenience import get_redis_client
from swift_browser_ui.ui.api import (
    add_project_container_acl,
    close_upload_session,
    get_access_control_metadata,
    get_crypted_upload_session,
    get_crypted_upload_socket_info,
    get_os_user,
    get_shared_container_address,
    get_upload_session,
    modify_container_write_acl,
    os_list_projects,
    remove_container_acl,
    remove_project_container_acl,
    swift_create_container,
    swift_delete_container,
    swift_download_container,
    swift_download_object,
    swift_download_shared_object,
    swift_get_metadata_container,
    swift_get_project_metadata,
    swift_list_containers,
    swift_list_objects,
    swift_replicate_container,
    swift_update_container_metadata,
)
from swift_browser_ui.ui.discover import handle_discover
from swift_browser_ui.ui.front import (
    accessibility,
    agg_swjs,
    badrequest,
    browse,
    down_swasm,
    down_swjs,
    forbid,
    index,
    loginpassword,
    map_down_swjs,
    map_up_swjs,
    notfound,
    select,
    uidown,
    unauth,
    up_swasm,
    up_swjs,
)
from swift_browser_ui.ui.health import handle_health_check
from swift_browser_ui.ui.login import (
    credentials_login_end,
    handle_login,
    handle_logout,
    handle_project_lock,
    oidc_end,
    oidc_start,
    sso_query_begin,
    sso_query_begin_oidc,
    sso_query_end,
)
from swift_browser_ui.ui.misc_handlers import handle_bounce_direct_access_request
from swift_browser_ui.ui.settings import setd
from swift_browser_ui.ui.signature import (
    handle_ext_token_create,
    handle_ext_token_list,
    handle_ext_token_remove,
    handle_signature_request,
)

# temporarily ignore typecheck from mypy until
# this issue is fixed https://github.com/MagicStack/uvloop/issues/575
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())  # type: ignore


async def open_client_to_app(app: aiohttp.web.Application) -> None:
    """Open a client session for download proxies."""
    app["api_client"] = aiohttp.ClientSession()


async def kill_dload_client(app: aiohttp.web.Application) -> None:
    """Kill download proxy client session."""
    await app["api_client"].close()


async def servinit(
    inject_middleware: typing.List[typing.Any] | None = None,
) -> aiohttp.web.Application:
    """Create an aiohttp server with the correct arguments and routes."""
    middlewares = [
        swift_browser_ui.ui.middlewares.error_middleware,
        swift_browser_ui.ui.middlewares.check_session,
        swift_browser_ui.ui.middlewares.check_session_taintness,
    ]
    if inject_middleware:
        middlewares = middlewares + inject_middleware
    app = aiohttp.web.Application()

    async def on_prepare(
        _: aiohttp.web.Request, response: aiohttp.web.StreamResponse
    ) -> None:
        """Modify Server headers."""
        response.headers["Server"] = "Swift Browser"

    # add custom response headers
    app.on_response_prepare.append(on_prepare)

    # Initialize aiohttp_session
    redis_client = await get_redis_client()
    storage = aiohttp_session.redis_storage.RedisStorage(
        redis_client,
        cookie_name="SWIFT_UI_SESSION",
    )
    app["seckey"] = base64.urlsafe_b64decode(cryptography.fernet.Fernet.generate_key())
    aiohttp_session.setup(
        app,
        storage,
    )

    # Add the rest of the middlewares
    [app.middlewares.append(i) for i in middlewares]  # type: ignore

    # Create a signature salt to prevent editing the signature on the client
    # side. Hash function doesn't need to be cryptographically secure, it's
    # just a convenient way of getting ascii output from byte values.
    app["Salt"] = secrets.token_hex(64)
    # Set application specific logging
    app["Log"] = logging.getLogger("swift-browser-ui")
    app["Log"].info("Set up logging for the swift-browser-ui application")

    if setd["oidc_enabled"]:
        oidc_url = "{}/.well-known/openid-configuration".format(setd["oidc_url"])
        oidc_conf = {
            "oidc": {
                "issuer": setd["oidc_url"],
                "client_id": setd["oidc_client_id"],
                "client_secret": setd["oidc_client_secret"],
                "redirect_uris": str(setd["oidc_redirect_uris"]).split(" "),
                "behaviour": {
                    "response_types": ["code"],
                    "scope": ["openid", "profile", "email"],
                },
            },
        }
        app["oidc_client"] = RPHandler(oidc_url, client_configs=oidc_conf)

    # Setup static folder during development, if it has been specified
    if setd["static_directory"] is not None:
        app.router.add_static(
            "/static/",
            path=str(setd["static_directory"]),
            name="static",
            show_index=False,
        )

    app.add_routes(
        [
            aiohttp.web.get("/", index),
            # Worker routes
            aiohttp.web.get("/upworker.js", up_swjs),
            aiohttp.web.get("/upworker.wasm", up_swasm),
            aiohttp.web.get("/downworker.js", down_swjs),
            aiohttp.web.get("/downworker.wasm", down_swasm),
            aiohttp.web.get("/upworker-post.js.map", map_up_swjs),
            aiohttp.web.get("/downworker-post.js.map", map_down_swjs),
            aiohttp.web.get("/aggregatorsw.js", agg_swjs),
            aiohttp.web.get("/loginpassword", loginpassword),
            aiohttp.web.get("/browse", browse),
            # Route all URLs prefixed by /browse to the browser page, as this is
            # an spa
            aiohttp.web.get("/browse/{tail:.*}", browse),
            aiohttp.web.get("/select", select),
            aiohttp.web.get("/unauth", unauth),
            aiohttp.web.get("/forbid", forbid),
            aiohttp.web.get("/uidown", uidown),
            aiohttp.web.get("/badrequest", badrequest),
            aiohttp.web.get("/notfound", notfound),
            aiohttp.web.get("/accessibility", accessibility),
        ]
    )

    # Add lock routes
    app.add_routes(
        [
            aiohttp.web.get("/lock/{project}", handle_project_lock),
        ]
    )

    # Add login routes
    app.add_routes(
        [
            aiohttp.web.get("/login", handle_login),
            aiohttp.web.get("/login/kill", handle_logout),
            aiohttp.web.get("/login/front", sso_query_begin),
            aiohttp.web.get("/login/oidc_front", sso_query_begin_oidc),
            aiohttp.web.post("/login/return", sso_query_end),
            aiohttp.web.post("/login/websso", sso_query_end),
            aiohttp.web.post("/login/credentials", credentials_login_end),
        ]
    )
    if setd["oidc_enabled"]:
        app.add_routes(
            [
                aiohttp.web.get("/login/oidc", oidc_start),
                aiohttp.web.get("/login/oidc-redirect", oidc_end),
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
            aiohttp.web.put(
                "/api/access/{project}/{container}", modify_container_write_acl
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
            aiohttp.web.delete("/upload/{project}", close_upload_session),
            aiohttp.web.get("/upload/{project}/{container}", get_upload_session),
            aiohttp.web.get(
                "/enupload/{project}/{container}/{object_name:.*}",
                get_crypted_upload_session,
            ),
            aiohttp.web.get(
                "/enupload/{project}",
                get_crypted_upload_socket_info,
            ),
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
    """Run the server securely with a given ssl context.

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
        access_log=logging.getLogger("aiohttp.access"),
        port=setd["port"],  # type: ignore
        ssl_context=sslcontext,
    )


def run_server_insecure(
    app: typing.Coroutine[typing.Any, typing.Any, aiohttp.web.Application]
) -> None:
    """Run the server without https enabled."""
    aiohttp.web.run_app(
        app,
        access_log=logging.getLogger("aiohttp.access"),
        port=(setd["port"]),  # type: ignore
    )


if __name__ == "__main__":
    if sys.version_info < (3, 12):
        logging.error("swift-browser-ui requires >= python3.12")
        sys.exit(1)
    run_server_insecure(servinit())
