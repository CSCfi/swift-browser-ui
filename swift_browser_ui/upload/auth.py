"""Authorization handlers for swift-upload-runner."""


import os
import hashlib
import typing
import hmac
import time
import secrets

import aiohttp.web

from swift_browser_ui._convenience import initiate_os_session

AiohttpHandler = typing.Callable[
    [aiohttp.web.Request],
    typing.Coroutine[typing.Awaitable, typing.Any, aiohttp.web.Response],
]


async def handle_login(request: aiohttp.web.Request) -> aiohttp.web.StreamResponse:
    """Begin a new session for the upload process."""
    session_key = hashlib.sha1(os.urandom(128)).hexdigest()  # nosec

    try:
        project = request.match_info["project"]
        login_form = await request.post()
        token = login_form["token"]
        request.app[session_key] = {}
        request.app[session_key]["uploads"] = {}
        request.app[session_key]["auth"] = initiate_os_session(token, project)

        resp = aiohttp.web.Response(status=200, body="OK")
        resp.cookies["RUNNER_SESSION_ID"] = session_key

        return resp

    except KeyError:
        raise aiohttp.web.HTTPUnauthorized(reason="Login token or project missing")


async def read_in_keys(app: aiohttp.web.Application) -> None:
    """Read in keys to the application."""
    keys = os.environ.get("SWIFT_UI_API_AUTH_TOKENS", None)
    app["tokens"] = keys.split(",") if keys is not None else []
    if app["tokens"]:
        app["tokens"] = [token.encode("utf-8") for token in app["tokens"]]


async def test_signature(
    tokens: typing.List[bytes],
    signature: str,
    message: str,
    validity: str,
) -> bool:
    """Validate signature against the given tokens."""
    # Check signature expiration
    if int(validity) < time.time():
        raise aiohttp.web.HTTPUnauthorized(reason="Signature expired")
    byte_message = message.encode("utf-8")
    for token in tokens:
        digest = hmac.new(token, byte_message, digestmod="sha256").hexdigest()
        if secrets.compare_digest(digest, signature):
            return True
    raise aiohttp.web.HTTPUnauthorized(reason="Missing valid query signature")


@aiohttp.web.middleware
async def handle_validate_authentication(
    request: aiohttp.web.Request,
    handler: AiohttpHandler,
) -> aiohttp.web.Response:
    """Handle the authentication of a response as a middleware function."""
    try:
        signature = request.query["signature"]
        validity = request.query["valid"]
        path = request.url.path
    except KeyError:
        raise aiohttp.web.HTTPUnauthorized(
            reason="Query string missing validity or signature"
        )

    await test_signature(request.app["tokens"], signature, validity + path, validity)

    return await handler(request)
