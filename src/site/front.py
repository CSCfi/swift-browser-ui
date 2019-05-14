# -*- coding: utf-8 -*-


import aiohttp.web


async def browse(request):
    return aiohttp.web.FileResponse(
        '/home/sapenna/s3-object-browser/src/static/html/browse.html'
    )


localroutes = [
    aiohttp.web.get('/browse', browse)
]
