# -*- coding: utf-8 -*-


# Generic imports
import aiohttp.web
import os
import ssl

import cryptography.fernet

from front import index, browse
from login import handle_login, sso_query_begin, sso_query_end, handle_logout
from api import list_buckets, list_objects, download_object


def servinit():
    PROJECT_ROOT = os.getcwd()

    app = aiohttp.web.Application()

    # Mutable_map handles cookie storage, also stores the object that provides
    # the encryption we use
    app['Crypt'] = cryptography.fernet.Fernet(
        cryptography.fernet.Fernet.generate_key()
    )
    # Session list to quickly validate sessions
    app['Sessions'] = []
    # Cookie keyed dictionary to store session data
    app['Creds'] = {}

    # Setup static folder during developement
    app.router.add_static(
        '/static/',
        path=PROJECT_ROOT + '/static',
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
        aiohttp.web.get('/login/websso', sso_query_begin),
        aiohttp.web.post('/login/websso', sso_query_end),
    ])

    # Add api routes
    app.add_routes([
        aiohttp.web.get('/api/buckets', list_buckets),
        aiohttp.web.get('/api/objects', list_objects),
        aiohttp.web.get('/api/dload', download_object),
    ])

    # Setup ssl context (FUTURE)
    # sslcontext = ssl.create_default_context()
    # sslcontext.set_ciphers(
    #     'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE' +
    #     '-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-' +
    #     'AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-' +
    #     'SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-' +
    #     'RSA-AES128-SHA256'
    # )

    aiohttp.web.run_app(app)

if __name__ == '__main__':
    servinit()
