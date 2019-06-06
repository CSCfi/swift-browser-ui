import aiohttp.web
import os
from ._convenience import session_check


WEBROOT = os.getcwd()


async def browse(request):
    try:
        if session_check(request):
            response = aiohttp.web.FileResponse(
                WEBROOT + '/s3browser_frontend/browse.html'
            )
        else:
            response = aiohttp.web.Response(
                status=303,
                reason="Stale session, redirect to login to establish new",
            )
            response.headers['Location'] = '/login'
        return response
    except KeyError:
        response = aiohttp.web.Response(
            status=303,
            reason="No session token present, have you logged in yet?"
        )
        response.headers['Location'] = '/login'
        return response


async def index(request):
    return aiohttp.web.FileResponse(
        WEBROOT + '/s3browser_frontend/index.html'
    )
