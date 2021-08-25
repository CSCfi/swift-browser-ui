"""Module containing handlers common to swift_browser_ui services."""


import aiohttp.web
import typing


async def handle_delete_preflight(
    _: typing.Union[aiohttp.web.Request, None]
) -> aiohttp.web.Response:
    """Serve correct response headers to allowed DELETE preflight query."""
    resp = aiohttp.web.Response(
        headers={
            "Access-Control-Allow-Methods": "POST, OPTIONS, DELETE",
            "Access-Control-Max-Age": "84600",
        }
    )
    return resp
