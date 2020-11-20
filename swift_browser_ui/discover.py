"""Endpoints for different server information discovery."""


from typing import Union
import aiohttp.web

from .settings import setd


async def handle_discover(
        _: Union[aiohttp.web.Request, None]
) -> aiohttp.web.Response:
    """Reply with sharing information if sharing API is available."""
    return aiohttp.web.json_response({
        "sharing_endpoint": setd["sharing_endpoint"],
        "request_endpoint": setd["request_endpoint"],
    })
