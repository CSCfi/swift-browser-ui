"""Middleware for adding CORS headers for API calls."""


import aiohttp.web


@aiohttp.web.middleware
async def add_cors(request, handler):
    """Add CORS header for API responses."""
    resp = await handler(request)
    if "origin" in request.headers.keys():
        resp.headers["Access-Control-Allow-Origin"] = request.headers["origin"]
    return resp
