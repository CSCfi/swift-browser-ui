"""Authorization handlers for swift-upload-runner."""


import os
import hashlib

import aiohttp.web

import swift_browser_ui.common.types
import swift_browser_ui.common.signature
from swift_browser_ui.ui._convenience import initiate_os_session


async def handle_login(request: aiohttp.web.Request) -> aiohttp.web.StreamResponse:
    """Begin a new session for the upload process."""
    session_key = hashlib.sha1(os.urandom(128)).hexdigest()  # nosec

    try:
        project = request.match_info["project"]
        login_form = await request.post()
        token = login_form["token"]
        request.app[session_key] = {}
        request.app[session_key]["uploads"] = {}
        request.app[session_key]["auth"] = initiate_os_session(str(token), str(project))

        resp = aiohttp.web.Response(status=200, body="OK")
        resp.cookies["RUNNER_SESSION_ID"] = session_key

        return resp

    except KeyError:
        raise aiohttp.web.HTTPUnauthorized(reason="Login token or project missing")


@aiohttp.web.middleware
async def handle_validate_authentication(
    request: aiohttp.web.Request,
    handler: swift_browser_ui.common.types.AiohttpHandler,
) -> aiohttp.web.Response:
    """Handle the authentication of a response as a middleware function."""
    if request.path == "/health":
        return await handler(request)

    try:
        signature = request.query["signature"]
        validity = request.query["valid"]
        path = request.url.path
    except KeyError:
        raise aiohttp.web.HTTPUnauthorized(
            reason="Query string missing validity or signature"
        )

    await swift_browser_ui.common.signature.test_signature(
        request.app["tokens"], signature, validity + path, validity
    )

    return await handler(request)
