import aiohttp.web
import os


WEBROOT = os.getcwd()


async def browse(request):
    try:
        session = request.cookies['S3BROW_SESSION']
        session = session.encode('utf-8')
        session = request.app['Crypt'].decrypt(session).decode('utf-8')
        response = aiohttp.web.FileResponse(
            WEBROOT + '/s3browser_frontend/browse.html'
        )
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
