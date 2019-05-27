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
import time

from ._convenience import disable_cache, decrypt_cookie, generate_cookie
from ._convenience import session_check, validate_cookie
from ._convenience import get_availability_from_token
from ._convenience import initiate_os_connection


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

    request.app['Log'].info(
        'Established new session for {0} - cookie:{1} - time:{2}'.format(
            request.remote,
            cookie,
            time.ctime()
        )
    )

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
        request.app['Log'].info(
            'Received SSO login from {0} with session {1} :: {2}'.format(
                request.remote,
                session,
                time.ctime()
            )
        )
    else:
        return aiohttp.web.Response(
            status=401,
            reason="Invalid or no session cookie"
        )
    # Try getting the token id from form
    if 'token' in request.query:
        unscoped = request.query['token']
        request.app['Log'].info(
            'Got OS token ::{0}:: from address {1} at {2}'.format(
                unscoped,
                request.remote,
                time.ctime()
            )
        )
    else:
        response = aiohttp.web.Response(
            status=400,
            reason="No Token ID was specified, token id is required"
        )
        return response

    # Check project availability with a list of domains, save the information
    # inside the app mapping
    request.app['Avail'] = await get_availability_from_token(unscoped)

    # Create an auth plugin with first project that was found for the user
    # (for now)
    request.app['Auth'] = await validate_cookie(
        request,
        request.app['Avail']['projects'][0]
    )

    # Open an openstack session with the auth plugin we just created
    # No need to pass auth plugin separately, it's contained inside the
    # request's app
    request.app['OS_Session'] = initiate_os_connection(request)

    # Redirect to the browse page with the correct credentials
    response = aiohttp.web.Response(
        status=302,
        reason="Start application"
    )
    response.headers['Location'] = "/browse"

    return response


async def handle_logout(request):
    # TODO: add token revokation upon leaving
    if session_check(request):
        cookie = await decrypt_cookie(request)
        request.app['Sessions'].remove(cookie)
    return aiohttp.web.Response(
        status=204
    )
