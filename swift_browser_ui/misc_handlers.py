"""Handlers that can't easily be categorized."""


import aiohttp.web

from ._convenience import session_check


async def handle_bounce_direct_access_request(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Redirect user to a correct access request page."""
    session_check(request)

    try:
        container = request.query["container"]
        owner = request.query["owner"]
        resp = aiohttp.web.Response(status=307)
        resp.headers[
            "Location"
        ] = f"/browse/sharing/requestdirect?container={container}&owner={owner}"
        return resp
    except KeyError:
        raise aiohttp.web.HTTPClientError(reason="Query string missing parameters")
