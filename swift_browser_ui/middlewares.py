"""Middlewares for the swift-browser-ui."""

from aiohttp import web

from .settings import setd


@web.middleware
async def unauthorized_middleware(request, handler):
    """Return a custom page upon an HTTP 401."""
    try:
        response = await handler(request)
        if response.status != 401:
            return response
    except web.HTTPException as ex:
        if ex.status != 401:
            raise
    return web.FileResponse(
        setd["static_directory"] + "/401.html"
    )


@web.middleware
async def forbidden_middleware(request, handler):
    """Return a custom page upon an HTTP 403."""
    try:
        response = await handler(request)
        if response.status != 403:
            return response
    except web.HTTPException as ex:
        if ex.status != 403:
            raise
    return web.FileResponse(
        setd["static_directory"] + "/403.html"
    )


@web.middleware
async def not_found_middleware(request, handler):
    """Return a custom page upon an HTTP 404."""
    try:
        response = await handler(request)
        if response.status != 404:
            return response
    except web.HTTPException as ex:
        if ex.status != 404:
            raise
    return web.FileResponse(
        setd["static_directory"] + "/404.html"
    )
