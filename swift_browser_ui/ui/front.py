"""Web frontend functions for stand-alone running."""

import typing

import aiohttp.web
import aiohttp_session
from cryptography.fernet import InvalidToken

from swift_browser_ui.ui.settings import setd


async def up_swjs(_: aiohttp.web.Request) -> aiohttp.web.FileResponse:
    """Serve worker js in worker scope."""
    return aiohttp.web.FileResponse(
        str(setd["static_directory"]) + "/upworker.js",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "Service-Worker-Allowed": "/",
        },
    )


async def up_swasm(_: aiohttp.web.Request) -> aiohttp.web.FileResponse:
    """Serve worker wasm in worker scope."""
    return aiohttp.web.FileResponse(
        str(setd["static_directory"]) + "/upworker.wasm",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "Service-Worker-Allowed": "/",
        },
    )


async def down_swjs(_: aiohttp.web.Request) -> aiohttp.web.FileResponse:
    """Serve worker js in worker scope."""
    return aiohttp.web.FileResponse(
        str(setd["static_directory"]) + "/downworker.js",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "Service-Worker-Allowed": "/",
        },
    )


async def down_swasm(_: aiohttp.web.Request) -> aiohttp.web.FileResponse:
    """Serve worker wasm in worker scope."""
    return aiohttp.web.FileResponse(
        str(setd["static_directory"]) + "/downworker.wasm",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "Service-Worker-Allowed": "/",
        },
    )


async def map_down_swjs(_: aiohttp.web.Request) -> aiohttp.web.FileResponse:
    """Serve worker js in worker scope."""
    return aiohttp.web.FileResponse(
        str(setd["static_directory"]) + "/downworker-post.js.map",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "Service-Worker-Allowed": "/",
        },
    )


async def map_up_swjs(_: aiohttp.web.Request) -> aiohttp.web.FileResponse:
    """Serve worker js in worker scope."""
    return aiohttp.web.FileResponse(
        str(setd["static_directory"]) + "/upworker-post.js.map",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "Service-Worker-Allowed": "/",
        },
    )


async def agg_swjs(_: aiohttp.web.Request) -> aiohttp.web.FileResponse:
    """Serve worker js in worker scope."""
    return aiohttp.web.FileResponse(
        str(setd["static_directory"]) + "/aggregatorsw.js",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "Service-Worker-Allowed": "/",
        },
    )


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
    request: aiohttp.web.Request | None,
) -> typing.Union[aiohttp.web.Response, aiohttp.web.FileResponse]:
    """Serve the index page when running without a proxy."""
    try:
        if request is not None:
            session = await aiohttp_session.get_session(request)
            if setd["oidc_enabled"]:
                session["oidc"]
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
        if request is not None:
            session = await aiohttp_session.get_session(request)
            if "oidc" in session:
                return aiohttp.web.Response(
                    status=302,
                    headers={
                        "Location": "/login",
                    },
                )
        return aiohttp.web.FileResponse(str(setd["static_directory"]) + "/index.html")


async def loginpassword(
    request: aiohttp.web.Request | None,
) -> typing.Union[aiohttp.web.Response, aiohttp.web.FileResponse]:
    """Serve the username and password login page."""
    try:
        if request is not None:
            session = await aiohttp_session.get_session(request)
            if setd["oidc_enabled"]:
                session["oidc"]
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


async def unauth(_: aiohttp.web.Request) -> aiohttp.web.FileResponse:
    """Serve worker js in worker scope."""
    return aiohttp.web.FileResponse(
        path=str(f"{setd['static_directory']}/401.html"),
        status=401,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "WWW-Authenticate": 'Bearer realm="/", charset="UTF-8"',
        },
    )


async def forbid(_: aiohttp.web.Request) -> aiohttp.web.FileResponse:
    """Serve worker js in worker scope."""
    return aiohttp.web.FileResponse(
        path=str(f"{setd['static_directory']}/403.html"),
        status=403,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


async def uidown(_: aiohttp.web.Request) -> aiohttp.web.FileResponse:
    """Serve worker js in worker scope."""
    return aiohttp.web.FileResponse(
        path=str(f"{setd['static_directory']}/503.html"),
        status=503,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


async def badrequest(_: aiohttp.web.Request) -> aiohttp.web.FileResponse:
    """Serve worker js in worker scope."""
    return aiohttp.web.FileResponse(
        path=str(f"{setd['static_directory']}/400.html"),
        status=400,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


async def notfound(_: aiohttp.web.Request) -> aiohttp.web.FileResponse:
    """Serve worker js in worker scope."""
    return aiohttp.web.FileResponse(
        path=str(f"{setd['static_directory']}/404.html"),
        status=404,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )
