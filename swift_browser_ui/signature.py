"""Module for handling queries for a valid Sharing/Request API signature."""


import hmac
import time

import aiohttp.web

from .settings import setd
from ._convenience import session_check


async def handle_signature_request(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Handle call for an API call signature."""
    session_check(request)

    try:
        valid_for = request.match_info["valid"]
        path_to_sign = request.query["path"]
    except KeyError:
        raise aiohttp.web.HTTPClientError(
            reason="Signable path missing from query string."
        )

    valid_until = str(int(time.time() + int(valid_for)))
    to_sign = (valid_until + path_to_sign).encode("utf-8")

    try:
        digest = hmac.new(
            key=setd["sharing_request_token"],
            msg=to_sign,
            digestmod="sha256"
        ).hexdigest()
    except KeyError:
        raise aiohttp.web.HTTPNotImplemented(
            reason="Server doesn't have signing persmissions"
        )

    return aiohttp.web.json_response({
        "signature": digest,
        "valid_until": valid_until,
    })
