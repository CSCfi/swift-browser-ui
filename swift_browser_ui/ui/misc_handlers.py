"""Handlers that can't easily be categorized."""


import aiohttp.web
import aiohttp_session

from swift_browser_ui.ui.settings import setd


async def handle_bounce_direct_access_request(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Redirect user to a correct access request page."""
    session = await aiohttp_session.get_session(request)
    try:
        if setd["oidc_enabled"]:
            session["oidc"]
        session["projects"]
        session["token"]
    except KeyError:
        raise aiohttp.web.HTTPUnauthorized(reason="No valid session.")

    try:
        container = request.query["container"]
        owner = request.query["owner"]
        resp = aiohttp.web.Response(status=307)
        resp.headers[
            "Location"
        ] = f"/browse/sharing/requestdirect?container={container}&owner={owner}"
        return resp
    except KeyError:
        raise aiohttp.web.HTTPBadRequest(reason="Query string missing parameters")
