"""Web frontend functions for stand-alone running."""

import os

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


async def darktheme(req):
    """Serve with dark theme if cookie matches."""
    if (
            "ENA_DARK" in req.cookies and
            os.path.exists(setd['static_directory'] + "/css/bulma-custom.css")
    ):
        resp = aiohttp.web.FileResponse(
            setd['static_directory'] + "/css/bulma-custom.css"
        )
        return resp
    return aiohttp.web.Response(
        status=204,
    )
