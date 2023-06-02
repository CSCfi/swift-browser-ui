"""Middlewares for the swift-browser-ui."""


import time
import typing

import aiohttp_session
from aiohttp import web

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
async def check_session(
    request: web.Request, handler: aiohttp_session.Handler
) -> web.StreamResponse:
    """Raise on expired or invalid sessions.

    :param request: A request instance
    :param handler: A request handler
    :raises: Reformatted HTTP Exceptions
    :returns: Successful requests unaffected
    """
    try:
        if request.path == "/" or any(
            s in request.path for s in {"login", "static", "health"}
        ):
            return await handler(request)

        session = await aiohttp_session.get_session(request)
        request.app["Log"].info("Identified session: %r", session)

        if session.empty:
            request.app["Log"].debug("Empty session")
            session.invalidate()
            raise _unauthorized("You must provide authentication.")

        if not all(k in session for k in {"projects", "uname", "at"}):
            request.app["Log"].error(
                "Session is invalid %r. This could be a bug or abuse.", session
            )
            session.invalidate()
            raise _unauthorized("Invalid session, authenticate again.")

        if "at" in session and session["at"] + setd["session_lifetime"] < time.time():
            request.app["Log"].debug("Session expired")
            session.invalidate()
            raise _unauthorized("Session expired.")

    except KeyError as error:
        reason = (
            f"No valid session. A session was invalidated due to invalid token. {error}"
        )
        request.app["Log"].exception(reason)
        raise _unauthorized(reason) from error
    except web.HTTPException:
        # HTTPExceptions are processed in the other middleware
        raise
    except Exception as error:
        reason = (
            f"No valid session. A session was invalidated due to another reason: {error}"
        )
        request.app["Log"].exception(reason)
        raise _unauthorized(reason) from error

    return await handler(request)


def _unauthorized(reason: str) -> web.HTTPUnauthorized:
    return web.HTTPUnauthorized(
        headers={"WWW-Authenticate": 'OAuth realm="/", charset="UTF-8"'}, reason=reason
    )


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
    to_process = {400, 401, 403, 404}

    try:
        response = await handler(request)
        if response.status in to_process:
            return return_error_response(response.status)
        if response.status == 409:
            return response
        return response
    except web.HTTPException as ex:
        if ex.status in to_process:
            return return_error_response(ex.status)
        if ex.status == 409:
            raise ex
        if ex.status > 404 and ex.status < 500:
            # we forbid all dubious and unauthorized requests
            return return_error_response(403)
        if ex.status > 500:
            return return_error_response(503)
        raise
