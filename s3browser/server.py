# Generic imports
import aiohttp.web
import ssl
import logging

import cryptography.fernet

from .front import index, browse
from .login import handle_login, sso_query_begin, sso_query_end, handle_logout
from .login import token_rescope
from .api import list_buckets, list_objects, download_object, os_list_projects
from .api import get_os_user
from .settings import setd


def servinit():
    app = aiohttp.web.Application()

    # Mutable_map handles cookie storage, also stores the object that provides
    # the encryption we use
    app['Crypt'] = cryptography.fernet.Fernet(
        cryptography.fernet.Fernet.generate_key()
    )
    # Set application specific logging
    app['Log'] = logging.getLogger('s3browser')
    app['Log'].info('Set up logging for the s3browser application')
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
    ])

    # Add login routes
    app.add_routes([
        aiohttp.web.get('/login', handle_login),
        aiohttp.web.get('/login/kill', handle_logout),
        aiohttp.web.get('/login/front', sso_query_begin),
        aiohttp.web.get('/login/return', sso_query_end),
        aiohttp.web.post('/login/return', sso_query_end),
        aiohttp.web.get('/login/rescope', token_rescope)
    ])

    # Add api routes
    app.add_routes([
        aiohttp.web.get('/api/buckets', list_buckets),
        aiohttp.web.get('/api/objects', list_objects),
        aiohttp.web.get('/api/dload', download_object),
        aiohttp.web.get('/api/username', get_os_user),
        aiohttp.web.get('/api/projects', os_list_projects),
    ])

    return app


def run_server_secure(app):
    # Setup ssl context
    sslcontext = ssl.create_default_context()
    # sslcontext.set_ciphers(
    #     'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE' +
    #     '-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-' +
    #     'AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-' +
    #     'SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-' +
    #     'RSA-AES128-SHA256'
    # )
    # sslcontext.load_cert_chain(
    #     'new.cert.cert', 'new.cert.key', 'Summers3'
    # )
    aiohttp.web.run_app(
        app,
        ssl_context=sslcontext
    )


def run_server_insecure(app):
    aiohttp.web.run_app(
        app,
        access_log=aiohttp.web.logging.getLogger('aiohttp.access')
    )


if __name__ == '__main__':
    run_server_insecure(servinit())
