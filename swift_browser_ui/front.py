"""Web frontend functions for stand-alone running."""

import aiohttp.web

from .settings import setd
from ._convenience import session_check


async def browse(request):
    """Serve the browser SPA when running without a proxy."""
    session_check(request)
    response = aiohttp.web.FileResponse(
        setd['static_directory'] + '/browse.html',
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )
    return response


async def index(_):
    """Serve the index page when running without a proxy."""
    return aiohttp.web.FileResponse(
        setd['static_directory'] + '/index.html'
    )
