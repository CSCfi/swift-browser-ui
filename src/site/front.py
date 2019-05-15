# -*- coding: utf-8 -*-


import aiohttp.web
import os


WEBROOT = os.getcwd()


async def browse(request):
    return aiohttp.web.FileResponse(
        WEBROOT + '/static/html/browse.html'
    )


async def index(request):
    return aiohttp.web.FileResponse(
        WEBROOT + '/static/html/index.html'
    )


async def login(request):
    return aiohttp.web.FileResponse(
        WEBROOT + '/static/html/login.html'
    )
