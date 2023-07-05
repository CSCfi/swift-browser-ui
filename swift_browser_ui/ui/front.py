"""Web frontend functions for stand-alone running."""

import typing

import aiohttp.web
import aiohttp_session
from cryptography.fernet import InvalidToken

from swift_browser_ui.ui.settings import setd


async def swjs(_: aiohttp.web.Request) -> aiohttp.web.FileResponse:
    """Serve worker js in worker scope."""
    return aiohttp.web.FileResponse(
        str(setd["static_directory"]) + "/libupload.js",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "Service-Worker-Allowed": "/",
        },
    )


async def swasm(_: aiohttp.web.Request) -> aiohttp.web.FileResponse:
    """Serve worker wasm in worker scope."""
    return aiohttp.web.FileResponse(
        str(setd["static_directory"]) + "/libupload.wasm",
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


async def unauth(_: aiohttp.web.Request) -> aiohttp.web.Response:
    """Serve worker js in worker scope."""
    with open(str(setd["static_directory"]) + "/401.html") as f:
        resp = aiohttp.web.Response(
            body="".join(f.readlines()),
            status=401,
            content_type="text/html",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
                "WWW-Authenticate": 'Bearer realm="/", charset="UTF-8"',
            },
        )
    return resp


async def forbid(_: aiohttp.web.Request) -> aiohttp.web.Response:
    """Serve worker js in worker scope."""
    with open(str(setd["static_directory"]) + "/403.html") as f:
        resp = aiohttp.web.Response(
            body="".join(f.readlines()),
            status=403,
            content_type="text/html",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )
    return resp


async def uidown(_: aiohttp.web.Request) -> aiohttp.web.Response:
    """Serve worker js in worker scope."""
    with open(str(setd["static_directory"]) + "/503.html") as f:
        resp = aiohttp.web.Response(
            body="".join(f.readlines()),
            status=503,
            content_type="text/html",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )
    return resp


async def badrequest(_: aiohttp.web.Request) -> aiohttp.web.Response:
    """Serve worker js in worker scope."""
    with open(str(setd["static_directory"]) + "/400.html") as f:
        resp = aiohttp.web.Response(
            body="".join(f.readlines()),
            status=400,
            content_type="text/html",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )
    return resp


async def notfound(_: aiohttp.web.Request) -> aiohttp.web.Response:
    """Serve worker js in worker scope."""
    with open(str(setd["static_directory"]) + "/404.html") as f:
        resp = aiohttp.web.Response(
            body="".join(f.readlines()),
            status=404,
            content_type="text/html",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )
    return resp
