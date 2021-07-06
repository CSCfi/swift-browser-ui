"""Web frontend functions for stand-alone running."""

import typing

import aiohttp.web
from aiohttp.web_routedef import head

from cryptography.fernet import InvalidToken

from .settings import setd
from ._convenience import session_check


async def browse(request: aiohttp.web.Request) -> aiohttp.web.FileResponse:
    """Serve the browser SPA when running without a proxy."""
    session_check(request)
    response = aiohttp.web.FileResponse(
        str(setd["static_directory"]) + "/browse.html",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )
    return response


async def index(
    request: typing.Optional[aiohttp.web.Request],
) -> typing.Union[aiohttp.web.Response, aiohttp.web.FileResponse]:
    """Serve the index page when running without a proxy."""
    try:
        if request is not None:
            session_check(request)
            request.app["Log"].info("Redirecting an existing session to app")
            return aiohttp.web.Response(
                status=303,
                headers={
                    "Location": "/browse",
                },
            )
        else:
            raise AttributeError
    except (AttributeError, InvalidToken, KeyError, aiohttp.web.HTTPUnauthorized):
        return aiohttp.web.FileResponse(str(setd["static_directory"]) + "/index.html")


async def loginpassword(
    request: typing.Optional[aiohttp.web.Request],
) -> typing.Union[aiohttp.web.Response, aiohttp.web.FileResponse]:
    """Serve the username and password login page."""
    try:
        if request is not None:
            session_check(request)
            request.app["Log"].info("Redirecting an existing session to app")
            return aiohttp.web.Response(
                status=303,
                headers={
                    "Location": "/browse",
                },
            )
        else:
            raise AttributeError
    except (AttributeError, InvalidToken, KeyError, aiohttp.web.HTTPUnauthorized):
        return aiohttp.web.FileResponse(
            str(setd["static_directory"]) + "/loginpassword.html"
        )
