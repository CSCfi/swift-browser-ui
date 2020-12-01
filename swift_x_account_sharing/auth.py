"""Authentication module for the swift-sharing-request."""

# The authentication is done via requests signed with a pre-whitelisted token.
# This is done to prevent invalid usage. New tokens can be created either
# manually on the platform that's running the software, or by
# pre-authenticating via Openstack Keystone.

# Authentication engine is written as an aiohttp middleware function.


import os
import typing
import hmac
import time
import logging
import secrets

import aiohttp.web
from asyncpg import InterfaceError

from .db import handle_dropped_connection


AiohttpHandler = typing.Callable[
    [aiohttp.web.Request],
    typing.Coroutine[
        typing.Awaitable,
        typing.Any,
        aiohttp.web.Response
    ]
]


LOGGER = logging.getLogger("swift_x_account_sharing.auth")


async def read_in_keys(
        app: aiohttp.web.Application
) -> None:
    """Read in keys to the application."""
    keys = os.environ.get("SWIFT_UI_API_AUTH_TOKENS", None)
    app["tokens"] = keys.split(",") if keys is not None else []
    if app["tokens"]:
        app["tokens"] = [
            token.encode("utf-8") for token in app["tokens"]
        ]


async def test_signature(
        tokens: typing.List[bytes],
        signature: str,
        message: str,
        validity: str,
) -> None:
    """Validate signature against the given tokens."""
    # Check signature expiration
    if int(validity) < time.time():
        raise aiohttp.web.HTTPUnauthorized(
            reason="Signature expired"
        )
    byte_message = message.encode("utf-8")
    for token in tokens:
        digest = hmac.new(
            token,
            byte_message,
            digestmod="sha256"
        ).hexdigest()
        if secrets.compare_digest(digest, signature):
            return
    raise aiohttp.web.HTTPUnauthorized(
        reason="Missing valid query signature"
    )


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
        raise aiohttp.web.HTTPClientError(
            reason="Query string missing validity or signature."
        )

    project: typing.Union[None, str]
    project_tokens = []
    try:
        project = request.match_info["project"]
    except KeyError:
        try:
            project = request.match_info["owner"]
        except KeyError:
            try:
                project = request.match_info["user"]
            except KeyError:
                project = None
    finally:
        if project:
            try:
                project_tokens = [
                    rec["token"].encode("utf-8")
                    for rec in await request.app["db_conn"].get_tokens(project)
                ]
            except InterfaceError:
                handle_dropped_connection(request)
        else:
            if request.path != "/health":
                LOGGER.debug(f"No project ID found in request {request}")
                raise aiohttp.web.HTTPUnauthorized(
                    reason="No project ID in request"
                )

    await test_signature(
        request.app["tokens"] + project_tokens,
        signature,
        validity + path,
        validity
    )

    return await handler(request)
