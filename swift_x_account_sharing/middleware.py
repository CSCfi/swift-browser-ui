"""Middleware for adding CORS headers for API calls."""


import aiohttp.web

from .db import DBConn


@aiohttp.web.middleware
async def add_cors(request, handler):
    """Add CORS header for API responses."""
    resp = await handler(request)
    if "origin" in request.headers.keys():
        resp.headers["Access-Control-Allow-Origin"] = request.headers["origin"]
    return resp


@aiohttp.web.middleware
async def check_db_conn(request, handler):
    """Check if an established database connection exists."""
    if (
            isinstance(request.app["db_conn"], DBConn) and
            request.app["db_conn"].conn is None
    ):
        raise aiohttp.web.HTTPServiceUnavailable(
            reason="No database connection."
        )
    return await handler(request)
