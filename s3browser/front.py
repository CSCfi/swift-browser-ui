"""Web frontend functions for stand-alone running."""

import aiohttp.web
import os
from ._convenience import session_check


WEBROOT = os.getcwd()


async def browse(request):
    """Serve the browser SPA when running without a proxy."""
    session_check(request)
    response = aiohttp.web.FileResponse(
        WEBROOT + '/s3browser_frontend/browse.html'
    )
    return response


async def index(request):
    """Serve the index page when running without a proxy."""
    return aiohttp.web.FileResponse(
        WEBROOT + '/s3browser_frontend/index.html'
    )
