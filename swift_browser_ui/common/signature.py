"""Authentication support module."""


import hmac
import logging
import os
import secrets
import time
import typing

import aiohttp.web

LOGGER = logging.getLogger("swift_browser_ui.common.signature")
LOGGER.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


def sign_api_request(
    path: str, valid_for: int = 3600, key: bytes = b""
) -> typing.Dict[str, typing.Any]:
    """Handle authentication with a signature."""
    valid_until = str(int(time.time() + valid_for))
    to_sign = (valid_until + path).encode("utf-8")

    digest = hmac.new(
        key=(key if key else os.environ.get("SWIFT_UI_API_KEY", "").encode("utf-8")),
        msg=to_sign,
        digestmod="sha256",
    ).hexdigest()

    return {
        "valid": valid_until,
        "signature": digest,
    }


async def test_signature(
    tokens: typing.List[bytes],
    signature: str,
    message: str,
    validity: str,
) -> None:
    """Validate signature against the given tokens."""
    # Check signature expiration
    if int(validity) < time.time():
        LOGGER.debug(f"Signature validity expired: {validity}")
        raise aiohttp.web.HTTPUnauthorized(reason="Signature validity expired")
    byte_message = message.encode("utf-8")
    for token in tokens:
        digest = hmac.new(token, byte_message, digestmod="sha256").hexdigest()
        if secrets.compare_digest(digest, signature):
            return
    LOGGER.debug(f"Missing valid query signature for signature {signature}")
    raise aiohttp.web.HTTPUnauthorized(reason="Missing valid query signature")
