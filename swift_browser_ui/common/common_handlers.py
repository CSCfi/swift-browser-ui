"""Module containing handlers common to swift_browser_ui services."""


import typing

import aiohttp.web


async def handle_delete_preflight(
    _: typing.Union[aiohttp.web.Request, None]
) -> aiohttp.web.Response:
    """Serve correct response headers to allowed DELETE preflight query."""
    resp = aiohttp.web.Response(
        headers={
            "Access-Control-Allow-Methods": "POST, OPTIONS, DELETE, PATCH",
            "Access-Control-Max-Age": "84600",
        }
    )
    return resp


async def handle_put_get_preflight(
    _: typing.Union[aiohttp.web.Request, None]
) -> aiohttp.web.Response:
    """Serve correct response headers to an allowed PUT preflight query."""
    resp = aiohttp.web.Response(
        headers={
            "Access-Control-Allow-Methods": "PUT, GET, OPTIONS",
            "Access-Control-Max-Age": "84600",
        }
    )
    return resp
