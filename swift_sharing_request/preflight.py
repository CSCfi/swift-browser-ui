"""Module containing preflight OPTIONS handlers."""


import aiohttp.web


async def handle_delete_preflight(_):
    """Serve correct response headers to allowed DELETE preflight query."""
    resp = aiohttp.web.Response(
        headers={
            "Access-Control-Allow-Methods": "POST, OPTIONS, DELETE",
            "Access-Control-Max-Age": 84600,
        }
    )
    return resp
