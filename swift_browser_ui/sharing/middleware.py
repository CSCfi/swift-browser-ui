"""Middleware for adding CORS headers for API calls."""


import typing

import aiohttp.web
from asyncpg import UniqueViolationError

from swift_browser_ui.sharing.db import DBConn


AiohttpHandler = typing.Callable[
    [aiohttp.web.Request],
    typing.Coroutine[
        typing.Awaitable,
        typing.Any,
        aiohttp.web.Response
    ]
]


@aiohttp.web.middleware
async def add_cors(
        request: aiohttp.web.Request,
        handler: AiohttpHandler
) -> aiohttp.web.Response:
    """Add CORS header for API responses."""
    resp = await handler(request)
    if "origin" in request.headers.keys():
        resp.headers["Access-Control-Allow-Origin"] = request.headers["origin"]
    return resp


@aiohttp.web.middleware
async def check_db_conn(
        request: aiohttp.web.Request,
        handler: AiohttpHandler
) -> aiohttp.web.Response:
    """Check if an established database connection exists."""
    if request.path == "/health":
        return await handler(request)

    if (
            isinstance(request.app["db_conn"], DBConn)
            and request.app["db_conn"].conn is None
    ):
        raise aiohttp.web.HTTPServiceUnavailable(
            reason="No database connection."
        )
    return await handler(request)


@aiohttp.web.middleware
async def catch_uniqueness_error(
        request: aiohttp.web.Request,
        handler: AiohttpHandler
) -> aiohttp.web.Response:
    """Catch excepetion arising from a non-unique primary key."""
    try:
        return await handler(request)
    except UniqueViolationError:
        raise aiohttp.web.HTTPConflict(
            reason="Duplicate entries are not allowed."
        )
