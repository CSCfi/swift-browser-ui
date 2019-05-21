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
from ._convenience import fetch_unscoped_projects, fetch_scoped_token


async def handle_login(request):
    """
    Create new session cookie for the user.
    """
    # TODO: Change session cookie to HTTP only after separating cookies
    response = aiohttp.web.Response(
        status=303,
        reason="Redirection to the application"
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

    try:
        if await decrypt_cookie(request) in request.app['Sessions']:
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
    except KeyError:
        return await aiohttp.web.Response(
            status=401,
            reason="No session cookie"
        )


async def sso_query_end(request):
    """
    Function for handling login token POST, to fetch the scoped token
    from the keystone api.
    """
    # Check for established session
    try:
        session = await decrypt_cookie(request)
        if session not in request.app['Sessions']:
            raise KeyError
    except KeyError:
        return await aiohttp.web.Response(
            status=401,
            reason="Invalid or no session cookie"
        )
    # Try getting the token id from form
    try:
        print("Got token {token}".format(request.query['tokenid']))
        unscoped = request.query['tokenid']
    except KeyError:
        response = await aiohttp.web.Response(
            status=400,
            reason="No Token ID was specified, token id is required"
        )
    # Initiate an aiohttp session to be used in fetching the token
    async with aiohttp.ClientSession() as token_session:
        # Fetch the project to scope the token for
        project = await fetch_unscoped_projects(unscoped, token_session)
        # Fetch the scoped token from the unscoped token
        scoped = await fetch_scoped_token(unscoped, project, token_session)
        request.app['Creds'][session] = {
            'token': scoped,
            'token_session': token_session
        }

    # Redirect to the browse page with the correct credentials
    response = await aiohttp.web.Response(
        status=302,
        reason="Start application"
    )

    response.headers['Location'] = "/browse"

    return response


async def handle_logout(request):
    # TODO: add token revokation upon leaving
    # TODO: add EC2 key pair revocation upon leaving
    cookie = decrypt_cookie(request)

    request.app['Sessions'].remove(cookie)

    return aiohttp.web.Response(
        status=204
    )
