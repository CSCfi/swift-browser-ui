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


async def disable_cache(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-Cache'
    response.headers['Expires'] = '0'
    return response


async def handle_login(request):
    """
    Create new session for the user
    """

    response = aiohttp.web.Response(
        status=303,
        reason="Redirection to the application"
    )

    response = await disable_cache(response)

    ccrypt = request.app['Crypt']
    cookie = hashlib.sha512(os.urandom(1024)).hexdigest()
    cookie_crypted = ccrypt.encrypt(cookie.encode('utf-8')).decode('utf-8')

    response.set_cookie(
        name='S3BROW_SESSION',
        value=cookie_crypted,
        max_age=3600,
    )

    request.app['Sessions'].append(cookie)

    response.headers['Location'] = "/login/websso"

    return response


async def decrypt_cookie(request):
    """
    Decrypt a cookie
    """
    return request.app['Crypt'].decrypt(
        request.cookies['S3BROW_SESSION'].encode('utf-8')
    ).decode('utf-8')


async def sso_query_begin(request):
    """
    Display login page and initiate federated keystone authentication
    """

    if await decrypt_cookie(request) in request.app['Sessions']:
        response = aiohttp.web.FileResponse(
            os.getcwd() + '/static/html/login.html'
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
    Handle the federated authentication return POST by creating the API keys
    for the session in progress. Redirect to /browse
    """
    try:
        if await decrypt_cookie(request) in request.app['Sessions']:
            response = aiohttp.web.Response(
                status=303,
                reason='Start application'
            )
            response.headers['Location'] = '/browse'
            return response
    except KeyError:
        response = aiohttp.web.Response(
            status=401,
            reason="Invalid or no session cookie"
        )
        return response


async def handle_logout(request):
    # TODO: add token revokation upon leaving
    # TODO: add EC2 key pair revocation upon leaving
    cookie_crypted = request.cookies['S3BROW_SESSION']
    cookie = request.app['Crypt'].decrypt(
        cookie_crypted.encode('utf-8')
    ).decode('utf-8')

    request.app['Sessions'].remove(cookie)

    return aiohttp.web.Response(
        status=204
    )
