"""Endpoints for different server information discovery."""


import aiohttp.web

from .settings import setd


async def handle_discover(_):
    """Reply with sharing information if sharing API is available."""
    return aiohttp.web.json_response({
        "sharing_endpoint": setd["sharing_endpoint"]
    })
