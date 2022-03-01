"""Web frontend functions for stand-alone running."""

import typing

import aiohttp.web
import aiohttp_session

from cryptography.fernet import InvalidToken

from swift_browser_ui.ui.settings import setd


async def browse(_: aiohttp.web.Request) -> aiohttp.web.FileResponse:
    """Serve the browser SPA when running without a proxy."""
    return aiohttp.web.FileResponse(
        str(setd["static_directory"]) + "/browse.html",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


async def select(_: aiohttp.web.Request) -> aiohttp.web.FileResponse:
    """Serve a project selection for users with tainted projects."""
    return aiohttp.web.FileResponse(
        str(setd["static_directory"]) + "/select.html",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


async def index(
    request: typing.Optional[aiohttp.web.Request],
) -> typing.Union[aiohttp.web.Response, aiohttp.web.FileResponse]:
    """Serve the index page when running without a proxy."""
    try:
        if request is not None:
            session = await aiohttp_session.get_session(request)
            session["projects"]
            session["token"]
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
            session = await aiohttp_session.get_session(request)
            session["projects"]
            session["token"]
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
