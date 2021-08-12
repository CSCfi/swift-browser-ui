"""Common API middleware."""


import aiohttp
import asyncpg.exceptions

import swift_browser_ui.common.types


@aiohttp.web.middleware
async def add_cors(
    request: aiohttp.web.Request, handler: swift_browser_ui.common.types.AiohttpHandler
) -> aiohttp.web.Response:
    """Add CORS header for API responses."""
    resp = await handler(request)
    if "origin" in request.headers.keys():
        resp.headers["Access-Control-Allow-Origin"] = request.headers["origin"]
    return resp


@aiohttp.web.middleware
async def catch_uniqueness_error(
    request: aiohttp.web.Request, handler: swift_browser_ui.common.types.AiohttpHandler
) -> aiohttp.web.Response:
    """Catch excepetion arising from a non-unique primary key."""
    try:
        return await handler(request)
    except asyncpg.exceptions.UniqueViolationError:
        raise aiohttp.web.HTTPConflict(reason="Duplicate entries are not allowed.")


@aiohttp.web.middleware
async def check_db_conn(
    request: aiohttp.web.Request, handler: swift_browser_ui.common.types.AiohttpHandler
):
    """Check if an established database connection exists."""
    if request.path == "/health":
        return await handler(request)
    try:
        if request.app["db_conn"].conn is None:
            raise aiohttp.web.HTTPServiceUnavailable(reason="No database connection")
    except AttributeError:
        pass
    return await handler(request)
