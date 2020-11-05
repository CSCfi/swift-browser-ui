"""Web frontend functions for stand-alone running."""

import aiohttp.web

from .settings import setd
from ._convenience import session_check


async def browse(
        request: aiohttp.web.Request
) -> aiohttp.web.FileResponse:
    """Serve the browser SPA when running without a proxy."""
    session_check(request)
    response = aiohttp.web.FileResponse(
        str(setd['static_directory']) + '/browse.html',
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )
    return response


async def index(_: None) -> aiohttp.web.FileResponse:
    """Serve the index page when running without a proxy."""
    return aiohttp.web.FileResponse(
        str(setd['static_directory']) + '/index.html'
    )
