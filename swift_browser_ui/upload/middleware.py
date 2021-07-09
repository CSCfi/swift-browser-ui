"""Middleware for adding CORS headers for API calls."""


import typing

import aiohttp.web


AiohttpHandler = typing.Callable[
    [aiohttp.web.Request],
    typing.Coroutine[typing.Awaitable, typing.Any, aiohttp.web.Response],
]


@aiohttp.web.middleware
async def add_cors(
    request: aiohttp.web.Request, handler: AiohttpHandler
) -> aiohttp.web.Response:
    """Add CORS header for API responses."""
    resp = await handler(request)
    if "origin" in request.headers.keys():
        resp.headers["Access-Control-Allow-Origin"] = request.headers["origin"]
    return resp
