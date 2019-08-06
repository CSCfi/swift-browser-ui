"""Middlewares for the swift-browser-ui."""

from aiohttp import web

from .settings import setd


@web.middleware
async def error_middleware(request, handler):
    """Return the correct HTTP Error page."""
    try:
        response = await handler(request)
        if response.status == 401:
            return web.FileResponse(
                setd["static_directory"] + "/401.html",
                status=401
            )
        if response.status == 403:
            return web.FileResponse(
                setd["static_directory"] + "/403.html",
                status=403
            )
        if response.status == 404:
            return web.FileResponse(
                setd["static_directory"] + "/404.html",
                status=404
            )
        return response
    except web.HTTPException as ex:
        if ex.status == 401:
            return web.FileResponse(
                setd["static_directory"] + "/401.html",
                status=401
            )
        if ex.status == 403:
            return web.FileResponse(
                setd["static_directory"] + "/403.html",
                status=403
            )
        if ex.status == 404:
            return web.FileResponse(
                setd["static_directory"] + "/404.html",
                status=404
            )
        raise
