"""Middlewares for the swift-browser-ui."""


import time
import typing

from aiohttp import web
import aiohttp_session

from swift_browser_ui.ui.settings import setd


AiohttpHandler = typing.Callable[
    [web.Request], typing.Coroutine[typing.Awaitable, typing.Any, web.Response]
]


def return_error_response(error_code: int) -> web.Response:
    """Return the correct error page with correct status code."""
    with open(str(setd["static_directory"]) + "/" + str(error_code) + ".html") as f:
        resp = web.Response(
            body="".join(f.readlines()),
            status=error_code,
            content_type="text/html",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )
    if error_code == 401:
        resp.headers["WWW-Authenticate"] = 'Bearer realm="/", charset="UTF-8"'
    return resp


@web.middleware
async def check_session_at(
    request: web.Request,
    handler: AiohttpHandler,
) -> web.Response:
    """Raise on expired sessions."""
    session = await aiohttp_session.get_session(request)
    if "at" in session and session["at"] + setd["session_lifetime"] < time.time():
        session.invalidate()
        if not ("login" in request.path or request.path == "/"):
            raise web.HTTPUnauthorized(reason="Token expired.")
    return await handler(request)


@web.middleware
async def check_session_taintness(
    request: web.Request,
    handler: AiohttpHandler,
) -> web.StreamResponse:
    """Override tainted sessions with project selection until scoped."""
    session = await aiohttp_session.get_session(request)
    if (
        "taint" in session
        and session["taint"]
        and "select" not in request.path
        and "projects" not in request.path
        and "lock" not in request.path
        and "static" not in request.path
    ):
        return web.Response(
            status=303,
            headers={
                "Location": "/select",
            },
        )
    return await handler(request)


@web.middleware
async def error_middleware(request: web.Request, handler: AiohttpHandler) -> web.Response:
    """Return the correct HTTP Error page."""
    try:
        response = await handler(request)
        if response.status == 400:
            return return_error_response(400)
        if response.status == 401:
            return return_error_response(401)
        if response.status == 403:
            return return_error_response(403)
        if response.status == 404:
            return return_error_response(404)
        if response.status == 409:
            return response
        return response
    except web.HTTPException as ex:
        if ex.status == 400:
            return return_error_response(400)
        if ex.status == 401:
            return return_error_response(401)
        if ex.status == 403:
            return return_error_response(403)
        if ex.status == 404:
            return return_error_response(404)
        if ex.status == 409:
            raise ex
        if ex.status > 404 and ex.status < 500:
            # we forbid all dubious and unauthorized requests
            return return_error_response(403)
        if ex.status > 500:
            return return_error_response(503)
        raise
