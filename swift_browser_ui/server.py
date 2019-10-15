"""swift_browser_ui server related convenience functions."""

# Generic imports
import logging
import time
import sys
import asyncio
import hashlib
import os
import ssl

import uvloop
import cryptography.fernet
import aiohttp.web

from .front import index, browse
from .login import handle_login, sso_query_begin, handle_logout
from .login import sso_query_end
from .login import token_rescope
from .api import list_buckets, list_objects, download_object, os_list_projects
from .api import get_os_user, get_os_active_project
from .api import get_metadata, get_project_metadata
from .settings import setd
from .middlewares import error_middleware


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


async def kill_sess_on_shutdown(app):
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


async def servinit():
    """Create an aiohttp server with the correct arguments and routes."""
    app = aiohttp.web.Application(
        middlewares=[error_middleware]
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
            path=setd['static_directory'],
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

    # Add api routes
    app.add_routes([
        aiohttp.web.get('/buckets', list_buckets),
        aiohttp.web.get('/bucket/objects', list_objects),
        aiohttp.web.get('/object/dload', download_object),
        aiohttp.web.get('/username', get_os_user),
        aiohttp.web.get('/projects', os_list_projects),
        aiohttp.web.get('/project/active', get_os_active_project),
        aiohttp.web.get('/bucket/meta', get_metadata),
        aiohttp.web.get('/project/meta', get_project_metadata),
    ])

    # Add graceful shutdown handler
    app.on_shutdown.append(kill_sess_on_shutdown)

    return app


def run_server_secure(app, cert_file, cert_key):
    """
    Run the server securely with a given ssl context.

    While this function is incomplete, the project is safe to run in
    production only via a TLS termination proxy with e.g. NGINX.
    """
    # The chiphers are from the Mozilla project wiki, as a recommendation for
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
        port=setd['port'],
        ssl_context=sslcontext,
    )


def run_server_insecure(app):
    """Run the server without https enabled."""
    aiohttp.web.run_app(
        app,
        access_log=aiohttp.web.logging.getLogger('aiohttp.access'),
        port=setd['port']
    )


if __name__ == '__main__':
    if sys.version_info < (3, 6):
        logging.error("swift-browser-ui requires >= python3.6")
        sys.exit(1)
    run_server_insecure(servinit())
