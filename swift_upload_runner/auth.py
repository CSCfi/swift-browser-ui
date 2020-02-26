"""Authorization handlers for swift-upload-runner."""


import os
import hashlib

import aiohttp.web

from swift_browser_ui._convenience import (
    initiate_os_session
)


async def handle_login(
        request: aiohttp.web.Request
) -> aiohttp.web.Request:
    """Begin a new session for the upload process."""
    session_key = hashlib.sha1(os.urandom(128)).hexdigest()  # nosec

    try:
        project = request.match_info["project"]
        login_form = await request.post()
        token = login_form["token"]
        request.app[session_key] = initiate_os_session(
            token,
            project
        )

        resp = aiohttp.web.Response(
            status=200,
            body='OK'
        )
        resp.cookies["RUNNER_SESSION_ID"] = session_key

        return resp

    except KeyError:
        raise aiohttp.web.HTTPUnauthorized(
            reason="Login token or project missing"
        )
