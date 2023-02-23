"""Authorization handlers for swift-upload-runner."""


import logging
import os
import secrets

import aiohttp
import aiohttp.web

import swift_browser_ui.common.signature
import swift_browser_ui.common.types
import swift_browser_ui.upload.common

LOGGER = logging.getLogger(__name__)


async def handle_login(request: aiohttp.web.Request) -> aiohttp.web.StreamResponse:
    """Begin a new session for the upload process."""
    session_key = secrets.token_urlsafe(32)
    client: aiohttp.ClientSession = request.app["client"]

    try:
        project = request.match_info["project"]
        login_form = await request.post()
        request.app[session_key] = {}
        request.app[session_key]["uploads"] = {}
        request.app[session_key]["enuploads"] = {}
        request.app[session_key]["token"] = login_form["token"]

        async with client.post(
            f"{os.environ.get('OS_AUTH_URL')}/auth/tokens",
            json={
                "auth": {
                    "identity": {
                        "methods": [
                            "token",
                        ],
                        "token": {
                            "id": request.app[session_key]["token"],
                        },
                    },
                    "scope": {"project": {"id": project}},
                },
            },
        ) as ret:
            if ret.status == 401:
                LOGGER.info(f"Could not log in session {session_key} with invalid token.")
                raise aiohttp.web.HTTPUnauthorized(reason="Token is not valid")
            if ret.status == 403:
                LOGGER.info(
                    f"Could not log in session {session_key} due to no service access with token."
                )
                raise aiohttp.web.HTTPForbidden(reason="No access to service with token.")
            request.app[session_key]["token"] = ret.headers["X-Subject-Token"]
            token = await ret.json()
            LOGGER.debug(token)
            # Use the first available public endpoint
            request.app[session_key]["endpoint"] = [
                list(filter(lambda i: i["interface"] == "public", i["endpoints"]))[0][
                    "url"
                ]
                for i in filter(
                    lambda i: i["type"] == "object-store", token["token"]["catalog"]
                )
            ][0]
            LOGGER.debug(f"Using endpoint {request.app[session_key]['endpoint']}")
            print(request.app[session_key])
        resp = aiohttp.web.Response(
            status=200,
            body="OK",
        )
        resp.cookies["RUNNER_SESSION_ID"] = session_key
        LOGGER.info(f"Opened an upload runner session for {session_key}")
        return resp
    except KeyError:
        raise aiohttp.web.HTTPUnauthorized(reason="Login token or project missing")


async def handle_logout(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Close the specified upload session."""
    try:
        # We can safely ignore any errors in keys, since that just means the session
        # doesn't exist
        session_key: str = swift_browser_ui.upload.common.get_session_id(request)
        request.app.pop(session_key)
    except KeyError:
        pass

    return aiohttp.web.Response(status=204)


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
