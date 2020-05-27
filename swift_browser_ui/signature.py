"""Module for handling queries for a valid Sharing/Request API signature."""


import hmac
import time
import logging
import secrets

import aiohttp.web

from ._convenience import session_check, api_check, get_tempurl_key, sign

from .settings import setd


LOGGER = logging.getLogger("signature")


async def handle_signature_request(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Handle call for an API call signature."""
    session_check(request)

    try:
        valid_for = int(request.match_info["valid"])
        path_to_sign = request.query["path"]
    except KeyError:
        raise aiohttp.web.HTTPClientError(
            reason="Signable path missing from query string."
        )

    return aiohttp.web.json_response(await sign(
        valid_for,
        path_to_sign
    ))


async def handle_ext_token_create(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Handle call for an API token create."""
    session = api_check(request)

    project = request.app["Creds"][session]["active_project"]["id"]

    LOGGER.debug(f"Creating a scoped API token for {project}")

    ident = request.match_info["id"]
    token = secrets.token_hex(64)

    client: aiohttp.ClientSession = request.app["api_client"]

    sharing_api_address = setd["sharing_internal_endpoint"]
    request_api_address = setd["request_internal_endpoint"]

    if not sharing_api_address or not request_api_address:
        raise aiohttp.web.HTTPNotFound(
            reason=("External APIs not configured on server")
        )

    path = f"/token/{project}/{ident}"
    signature = await sign(3600, path)

    resp_sharing = await client.post(
        f"{sharing_api_address}{path}",
        data={"token": token},
        params={
            "valid": signature["valid_until"],
            "signature": signature["signature"],
        }
    )
    resp_request = await client.post(
        f"{request_api_address}{path}",
        data={"token": token},
        params={
            "valid": signature["valid_until"],
            "signature": signature["signature"],
        }
    )

    if resp_sharing.status != 200 or resp_request.status != 200:
        resp_sharing_text = await resp_sharing.text()
        resp_request_text = await resp_request.text()
        LOGGER.debug(f"""\
        Sharing failed with status {resp_sharing.status}
        {resp_sharing_text}{resp_sharing.url}
        Request failed with status {resp_request.status}
        {resp_request_text}{resp_request.url}\
        """)
        raise aiohttp.web.HTTPInternalServerError(
            reason="Token creation failed"
        )

    resp = aiohttp.web.json_response(
        token,
        status=201
    )

    return resp


async def handle_ext_token_remove(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Handle call for an API token delete."""
    session = api_check(request)

    project = request.app["Creds"][session]["active_project"]["id"]

    ident = request.match_info["id"]

    client: aiohttp.ClientSession = request.app["api_client"]

    sharing_api_address = setd["sharing_internal_endpoint"]
    request_api_address = setd["request_internal_endpoint"]

    if not sharing_api_address or not request_api_address:
        raise aiohttp.web.HTTPNotFound(
            reason=("External APIs not configured on server")
        )

    path = f"/token/{project}/{ident}"
    signature = await sign(3600, path)

    await client.delete(
        f"{sharing_api_address}{path}",
        params={
            "signature": signature["signature"],
            "valid": signature["valid_until"],
        }
    )
    await client.delete(
        f"{request_api_address}{path}",
        params={
            "signature": signature["signature"],
            "valid": signature["valid_until"],
        }
    )

    resp = aiohttp.web.Response(status=204)

    return resp


async def handle_ext_token_list(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Handle call for listing API tokens."""
    session = api_check(request)

    project = request.app["Creds"][session]["active_project"]["id"]

    client: aiohttp.ClientSession = request.app["api_client"]

    sharing_api_address = setd["sharing_internal_endpoint"]
    request_api_address = setd["request_internal_endpoint"]

    if not sharing_api_address or not request_api_address:
        raise aiohttp.web.HTTPNotFound(
            reason=("External APIs not configured on server")
        )

    path = f"/token/{project}"
    signature = await sign(3600, path)

    sharing_tokens = await client.get(
        f"{sharing_api_address}{path}",
        params={
            "signature": signature["signature"],
            "valid": signature["valid_until"],
        }
    )
    request_tokens = await client.get(
        f"{request_api_address}{path}",
        params={
            "signature": signature["signature"],
            "valid": signature["valid_until"],
        }
    )
    sharing_tokens_text = await sharing_tokens.text()
    request_tokens_text = await request_tokens.text()

    LOGGER.debug(f"Sharing tokens: {sharing_tokens_text}")
    LOGGER.debug(f"Request tokens: {request_tokens_text}")

    if sharing_tokens_text != request_tokens_text:
        raise aiohttp.web.HTTPConflict(reason="API tokens don't match")

    resp = aiohttp.web.Response(text=sharing_tokens_text)

    return resp


async def handle_form_post_signature(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Handle call for a form signature."""
    session = api_check(request)
    LOGGER.info(
        'API call for download object from %s, sess. %s',
        request.remote,
        session
    )

    serv = request.app['Creds'][session]['ST_conn']
    sess = request.app['Creds'][session]['OS_sess']
    container = request.match_info["container"]

    temp_url_key = await get_tempurl_key(
        serv,
        # container
    )
    LOGGER.debug(
        "Using %s as temporary URL key.", temp_url_key
    )

    host = sess.get_endpoint(service_type="object-store").split("/v1")[0]
    path_begin = sess.get_endpoint(service_type="object-store").replace(
        host, ""
    )

    try:
        object_prefix = request.query["prefix"]
    except KeyError:
        object_prefix = ""
    try:
        redirect = request.query["redirect"]
    except KeyError:
        redirect = ""
    max_file_count = int(request.query["count"])
    max_file_size = 5368709119

    expires = int(time.time() + 84600)
    path = f'{path_begin}/{container}/'
    if object_prefix:
        path = path + object_prefix

    hmac_body = '%s\n%s\n%s\n%s\n%s' % (
        path,
        redirect,
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
        "max_file_size": max_file_size,
        "max_file_count": max_file_count,
        "expires": expires,
        "host": host,
        "path": path,
        "container": container,
        "prefix": object_prefix,
    })
