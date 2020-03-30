"""swift_browser_ui server related convenience functions."""

# Generic imports
import logging
import time
import sys
import asyncio
import hashlib
import os
import ssl
import typing

import uvloop
import cryptography.fernet
import aiohttp.web

from .front import (
    index,
    browse
)
from .login import (
    handle_login,
    handle_logout,
    sso_query_begin,
    sso_query_end,
    token_rescope,
)
from .api import (
    swift_list_buckets,
    swift_list_objects,
    swift_download_object,
    swift_download_shared_object,
    swift_download_container,
    os_list_projects,
    get_os_user,
    get_os_active_project,
    get_metadata_object,
    get_metadata_bucket,
    get_project_metadata,
    swift_list_shared_objects,
    get_access_control_metadata,
    remove_container_acl,
    add_project_container_acl,
    get_shared_container_address,
    swift_create_container,
    swift_upload_object_chunk,
    swift_check_object_chunk,
    swift_replicate_container,
)
from .settings import setd
from .middlewares import error_middleware
from .discover import handle_discover
from .signature import handle_signature_request
from .misc_handlers import handle_bounce_direct_access_request


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


async def kill_sess_on_shutdown(
        app: aiohttp.web.Application
):
    """Kill all open sessions and purge their data when killed."""
    logging.info("Gracefully shutting down the program at %s",
                 time.ctime())
    while app['Creds'].keys():
        key = list(app['Creds'].keys())[0]
        logging.info("Purging session for %s", key)
        # Invalidate the tokens that are in use
        app['Creds'][key]['OS_sess'].invalidate(
            app['Creds'][key]['OS_sess'].auth
        )
        logging.debug("Invalidated token for session %s :: %s",
                      key, time.ctime())
        # Purge everything related to the former openstack connection
        app['Creds'][key]['OS_sess'] = None
        app['Creds'][key]['ST_conn'] = None
        app['Creds'][key]['Avail'] = None
        app['Creds'][key]['Token'] = None
        app['Creds'][key]['active_project'] = None
        # Purge the openstack connection from the server
        app['Creds'].pop(key)
        logging.debug("Purged connection information for %s :: %s",
                      key, time.ctime())
        # Purge the session from the session list
        app['Sessions'].remove(key)
        logging.debug("Removed session %s from session list :: %s",
                      key, time.ctime())


async def open_client_to_app(
        app: aiohttp.web.Application
):
    """Open a client session for download proxies."""
    app['dload_session'] = aiohttp.ClientSession()


async def kill_dload_client(
        app: aiohttp.web.Application
):
    """Kill download proxy client session."""
    app['dload_session'].close()


async def servinit() -> aiohttp.web.Application:
    """Create an aiohttp server with the correct arguments and routes."""
    app = aiohttp.web.Application(
        middlewares=[error_middleware]  # type: ignore
    )

    # Mutable_map handles cookie storage, also stores the object that provides
    # the encryption we use
    app['Crypt'] = cryptography.fernet.Fernet(
        cryptography.fernet.Fernet.generate_key()
    )
    # Create a signature salt to prevent editing the signature on the client
    # side. Hash function doesn't need to be cryptographically secure, it's
    # just a convenient way of getting ascii output from byte values.
    app['Salt'] = hashlib.md5(os.urandom(128)).hexdigest()  # nosec
    # Set application specific logging
    app['Log'] = logging.getLogger('swift-browser-ui')
    app['Log'].info('Set up logging for the swift-browser-ui application')
    # Session list to quickly validate sessions
    app['Sessions'] = []
    # Cookie keyed dictionary to store session data
    app['Creds'] = {}

    # Setup static folder during developement, if it has been specified
    if setd['static_directory'] is not None:
        app.router.add_static(
            '/static/',
            path=setd['static_directory'],  # type: ignore
            name='static',
            show_index=True,
        )

    app.add_routes([
        aiohttp.web.get('/', index),
        aiohttp.web.get('/browse', browse),
        # Route all URLs prefixed by /browse to the browser page, as this is
        # an spa
        aiohttp.web.get('/browse/{tail:.*}', browse),
    ])

    # Add login routes
    app.add_routes([
        aiohttp.web.get('/login', handle_login),
        aiohttp.web.get('/login/kill', handle_logout),
        aiohttp.web.get('/login/front', sso_query_begin),
        aiohttp.web.post('/login/return', sso_query_end),
        aiohttp.web.post('/login/websso', sso_query_end),
        aiohttp.web.get('/login/rescope', token_rescope),
    ])

    # Add signature endpoint
    app.add_routes([
        aiohttp.web.get('/sign/{valid}', handle_signature_request)
    ])

    # Add api routes
    app.add_routes([
        aiohttp.web.get('/api/buckets', swift_list_buckets),
        aiohttp.web.put('/api/containers/{container}', swift_create_container),
        aiohttp.web.get('/api/bucket/objects', swift_list_objects),
        aiohttp.web.get('/api/object/dload', swift_download_object),
        aiohttp.web.get('/api/shared/objects', swift_list_shared_objects),
        aiohttp.web.get('/api/username', get_os_user),
        aiohttp.web.get('/api/projects', os_list_projects),
        aiohttp.web.get('/api/project/active', get_os_active_project),
        aiohttp.web.get('/api/bucket/meta', get_metadata_bucket),
        aiohttp.web.get('/api/bucket/object/meta', get_metadata_object),
        aiohttp.web.get('/api/project/meta', get_project_metadata),
        aiohttp.web.get('/api/project/acl', get_access_control_metadata),
        aiohttp.web.post('/api/access/{container}',
                         add_project_container_acl),
        aiohttp.web.delete('/api/access/{container}', remove_container_acl),
        aiohttp.web.get('/api/project/address', get_shared_container_address),
    ])

    # Add download routes
    app.add_routes([
        aiohttp.web.get('/download/{project}/{container}',
                        swift_download_container),
        aiohttp.web.get('/download/{project}/{container}/{object}',
                        swift_download_shared_object),
    ])

    # Add upload routes
    app.add_routes([
        aiohttp.web.post('/upload/{project}/{container}',
                         swift_upload_object_chunk),
        aiohttp.web.get('/upload/{project}/{container}',
                        swift_check_object_chunk),
    ])

    # Add replication routes
    app.add_routes([
        aiohttp.web.post('/replicate/{project}/{container}',
                         swift_replicate_container),
    ])

    # Add discovery routes
    app.add_routes([
        aiohttp.web.get('/discover', handle_discover)
    ])

    # Add direct routes
    app.add_routes([
        aiohttp.web.get('/direct/request',
                        handle_bounce_direct_access_request)
    ])

    app.on_startup.append(open_client_to_app)

    # Add graceful shutdown handler
    app.on_shutdown.append(kill_sess_on_shutdown)
    app.on_shutdown.append(kill_dload_client)

    return app


def run_server_secure(
        app: typing.Coroutine[typing.Any, typing.Any, aiohttp.web.Application],
        cert_file: str,
        cert_key: str
):
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
        "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE" +
        "-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA" +
        "-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM" +
        "-SHA256:DHE-RSA-AES256-GCM-SHA384"
    )
    logger.debug(
        "Setting following ciphers for SSL context: \n%s",
        cipher_str
    )
    sslcontext.set_ciphers(cipher_str)
    sslcontext.options |= ssl.OP_NO_TLSv1
    sslcontext.options |= ssl.OP_NO_TLSv1_1
    logger.debug("Loading cert chain.")
    sslcontext.load_cert_chain(cert_file, cert_key)
    aiohttp.web.run_app(
        app,
        access_log=aiohttp.web.logging.getLogger('aiohttp.access'),
        port=setd['port'],  # type: ignore
        ssl_context=sslcontext,
    )


def run_server_insecure(
        app: typing.Coroutine[typing.Any, typing.Any, aiohttp.web.Application]
):
    """Run the server without https enabled."""
    aiohttp.web.run_app(
        app,
        access_log=aiohttp.web.logging.getLogger('aiohttp.access'),
        port=(setd['port'])  # type: ignore
    )


if __name__ == '__main__':
    if sys.version_info < (3, 6):
        logging.error("swift-browser-ui requires >= python3.6")
        sys.exit(1)
    run_server_insecure(servinit())
