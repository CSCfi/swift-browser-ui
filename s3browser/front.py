import aiohttp.web
import os
from ._convenience import session_check


WEBROOT = os.getcwd()


async def browse(request):
    session_check(request)
    response = aiohttp.web.FileResponse(
        WEBROOT + '/s3browser_frontend/browse.html'
    )
    return response


async def index(request):
    return aiohttp.web.FileResponse(
        WEBROOT + '/s3browser_frontend/index.html'
    )
