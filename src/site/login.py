# -*- coding: utf-8 -*-


"""
A module for handling the project login sessions and requesting the necessary
tokens.
"""


import aiohttp.web
import oic
import aiohttp_security as sec
import aiohttp_session as ses


async def init_session():
    """
    A function for creating a login session for the user.
    """
    pass


async def init_login():
    """
    A function for initializing the login for a specific user, will begin by
    calling the createSession function, then will parse the required
    redirection for authorization and redirect the user as required.
    """
    initResponse = aiohttp.web.Response()

    return initResponse


async def handle_oidc_response():
    """
    A Function for handling parsing the Oauth2 / OIDC response that's initiated
    from the initLogin function. (checking the authenticity of the session id,
    fetching the OIDC response after checking the authenticity of the session
    and parsing the response)
    """
    pass
