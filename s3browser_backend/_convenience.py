# -*- coding: utf-8 -*-


from hashlib import sha256
from os import urandom


async def disable_cache(response):
    """
    A convenience function for adding all required cache disabling headers
    for web responses, e.g. login window.
    """
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-Cache'
    response.headers['Expires'] = '0'
    return response


async def decrypt_cookie(request):
    """
    Decrypt a cookie using the server instance specific fernet key
    """
    return request.app['Crypt'].decrypt(
        request.cookies['S3BROW_SESSION'].encode('utf-8')
    ).decode('utf-8')


async def generate_cookie(request):
    """
    Generate an encrypted and unencrypted cookie, for use as a session cookie
    or API key.
    """
    cookie = sha256(urandom(1024)).hexdigest()
    return cookie, request.app['Crypt'].encrypt(
        cookie.encode('utf-8')
        ).decode('utf-8')
