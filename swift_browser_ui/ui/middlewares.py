"""Middlewares for the swift-browser-ui."""


import typing

from aiohttp import web

from swift_browser_ui.ui.settings import setd

AiohttpHandler = typing.Callable[
    [web.Request], typing.Coroutine[typing.Awaitable, typing.Any, web.Response]
]


def return_error_response(error_code: int) -> web.Response:
    """Return the correct error page with correct status code."""
    with open(str(setd["static_directory"]) + "/" + str(error_code) + ".html") as resp:
        return web.Response(
            body="".join(resp.readlines()),
            status=error_code,
            content_type="text/html",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )


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
            # we forbid all dubios and unauthorized requests
            return return_error_response(403)
        if ex.status > 500:
            return return_error_response(503)
        raise
