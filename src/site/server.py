# -*- coding: utf-8 -*-


# Generic imports
import aiohttp.web
import os
import ssl

from aiohttp_session import setup as session_setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
import cryptography.fernet

# Project specific imports
from route import routel


def servinit():
    PROJECT_ROOT = os.getcwd()

    app = aiohttp.web.Application()

    session_setup(
        app,
        EncryptedCookieStorage(
            cryptography.fernet.Fernet.generate_key().decode('utf-8')
        )
    )

    # Setup static folder during developement
    app.router.add_static(
        '/static/',
        path=PROJECT_ROOT + '/static',
        name='static',
        show_index=True,
    )

    # Setup all routes from API and frontend modules
    app.add_routes(
        routel
    )

    # Setup ssl context (FUTURE)
    # sslcontext = ssl.create_default_context()
    # sslcontext.set_ciphers(
    #     'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE' +
    #     '-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-' +
    #     'AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-' +
    #     'SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-' +
    #     'RSA-AES128-SHA256'
    # )

    return app

if __name__ == '__main__':
    aiohttp.web.run_app(servinit())
