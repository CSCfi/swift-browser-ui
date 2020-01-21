"""Module for handling queries for a valid Sharing/Request API signature."""


import hmac
import time

import aiohttp.web

from .settings import setd
from ._convenience import session_check, api_check, get_tempurl_key


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
            key=setd["sharing_request_token"].encode("utf-8"),
            msg=to_sign,
            digestmod="sha256"
        ).hexdigest()
    except KeyError:
        raise aiohttp.web.HTTPNotImplemented(
            reason="Server doesn't have signing permissions"
        )
    except AttributeError:
        raise aiohttp.web.HTTPNotImplemented(
            reason="Server doesn't have signing permissions"
        )

    return aiohttp.web.json_response({
        "signature": digest,
        "valid_until": valid_until,
    })


async def handle_form_post_signature(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Handle call for a form signature."""
    session = api_check(request)
    request.app['Log'].info(
        'API call for download object from %s, sess. %s',
        request.remote,
        session
    )

    serv = request.app['Creds'][session]['ST_conn']
    sess = request.app['Creds'][session]['OS_sess']

    temp_url_key = await get_tempurl_key(serv)
    request.app['Log'].debug(
        "Using %s as temporary URL key.", temp_url_key
    )

    host = sess.get_endpoint(service_type="object-store").split("/v1")[0]
    path_begin = sess.get_endpoint(service_type="object-store").replace(
        host, ""
    )

    container = request.match_info["container"]
    object_prefix = request.match_info["prefix"]
    max_file_count = request.query["count"]
    max_file_size = "5368709120"

    expires = int(time.time() + 60 * 15)
    path = f'{path_begin}/{container}/{object_prefix}'

    hmac_body = '%s\n%s\n%s\n%s\n%s' % (
        path,
        "",
        max_file_size,
        max_file_count,
        expires
    )

    signature = hmac.new(
        temp_url_key.encode('utf-8'),
        hmac_body.encode('utf-8'),
        digestmod="sha1"
    ).hexdigest()

    return aiohttp.web.json_response({
        "signature": signature,
        "max_file_size": str(max_file_size),
        "max_file_count": max_file_count,
        "expires": expires,
        "path": path,
        "container": container,
        "prefix": object_prefix,
    })
