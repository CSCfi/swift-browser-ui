# -*- coding: utf-8 -*-


"""
A module for handling the project login sessions and requesting the necessary
tokens.
"""

# aiohttp
import aiohttp.web
# Openstack
import keystoneclient
import keystoneauth1

import cryptography.fernet
import hashlib
import os

from ._convenience import disable_cache, decrypt_cookie, generate_cookie
from ._convenience import session_check


async def handle_login(request):
    """
    Create new session cookie for the user.
    """
    # TODO: Change session cookie to HTTP only after separating cookies
    response = aiohttp.web.Response(
        status=303,
        reason="Redirection to login"
    )

    cookie, cookie_crypted = await generate_cookie(request)
    response = await disable_cache(response)

    response.set_cookie(
        name='S3BROW_SESSION',
        value=cookie_crypted,
        max_age=3600,
    )

    request.app['Sessions'].append(cookie)

    response.headers['Location'] = "/login/front"

    return response


async def sso_query_begin(request):
    """
    Display login page and initiate federated keystone authentication
    """
    if await session_check(request):
        response = aiohttp.web.FileResponse(
            os.getcwd() + '/s3browser_frontend/login.html'
        )
        return await disable_cache(response)
    else:
        response = aiohttp.web.Response(
            status=401,
            reason="Invalid or no session cookie"
        )
        return response


async def sso_query_end(request):
    """
    Function for handling login token POST, to fetch the scoped token
    from the keystone api.
    """
    # Check for established session
    if await session_check(request):
        session = await decrypt_cookie(request)
        print(session)
        print(request.app['Sessions'])
    else:
        return aiohttp.web.Response(
            status=401,
            reason="Invalid or no session cookie"
        )
    # Try getting the token id from form
    if 'token' in request.query:
        unscoped = request.query['token']
        print("Got token {0}".format(unscoped))
    else:
        print("\n {0}".format(request.query))
        response = aiohttp.web.Response(
            status=400,
            reason="No Token ID was specified, token id is required"
        )
        return response

    # Redirect to the browse page with the correct credentials
    response = aiohttp.web.Response(
        status=302,
        reason="Start application"
    )

    response.headers['Location'] = "/browse"

    return response


async def handle_logout(request):
    # TODO: add token revokation upon leaving
    # TODO: add EC2 key pair revocation upon leaving
    if session_check(request):
        cookie = await decrypt_cookie(request)
        request.app['Sessions'].remove(cookie)
    return aiohttp.web.Response(
        status=204
    )
