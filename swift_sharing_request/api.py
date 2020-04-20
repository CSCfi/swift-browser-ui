"""Module for share request API handlers."""


import logging
import asyncio

import aiohttp.web
from asyncpg import InterfaceError


MODULE_LOGGER = logging.getLogger("api")


def handle_dropped_connection(request):
    """Handle dropped database connection."""
    MODULE_LOGGER.log(
        logging.ERROR,
        "Lost database connection, reconnecting..."
    )
    request.app["db_conn"].erase()
    asyncio.ensure_future(
        request.app["db_conn"].open()
    )
    raise aiohttp.web.HTTPServiceUnavailable(
        reason="No database connection."
    )


async def handle_share_request_post(request):
    """Handle query for posting a new share request."""
    container = request.match_info["container"]
    user = request.match_info["user"]
    owner = request.query["owner"]

    try:
        await request.app["db_conn"].add_request(
            user,
            container,
            owner
        )
    except InterfaceError:
        handle_dropped_connection(request)

    return aiohttp.web.json_response({
        "container": container,
        "user": user,
        "owner": owner,
        "date": None
    })


async def handle_user_owned_request_listing(request):
    """Handle query for listing the requests owned by the user."""
    user = request.match_info["user"]

    try:
        ret = await request.app["db_conn"].get_request_owned(user)
    except InterfaceError:
        handle_dropped_connection(request)

    return aiohttp.web.json_response(ret)


async def handle_user_made_request_listing(request):
    """Handle query listing for the requests created by the user."""
    user = request.match_info["user"]

    try:
        ret = await request.app["db_conn"].get_request_made(user)
    except InterfaceError:
        handle_dropped_connection(request)

    return aiohttp.web.json_response(ret)


async def handle_container_request_listing(request):
    """Handle query for listing the container share requests."""
    container = request.match_info["container"]

    try:
        ret = await request.app["db_conn"].get_request_container(container)
    except InterfaceError:
        handle_dropped_connection(request)

    return aiohttp.web.json_response(ret)


async def handle_user_share_request_delete(request):
    """Delete container share request or requests."""
    container = request.match_info["container"]
    user = request.match_info["user"]
    owner = request.query["owner"]

    try:
        await request.app["db_conn"].delete_request(container, owner, user)
    except InterfaceError:
        handle_dropped_connection(request)

    return aiohttp.web.Response(
        status=200,
        body="OK"
    )


async def handle_user_add_token(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Add a token to the user."""
    project = request.match_info["project"]
    identifier = request.match_info["id"]

    token = request.query["token"]

    try:
        await request.app["db_conn"].add_token(
            project,
            token,
            identifier
        )
    except InterfaceError:
        handle_dropped_connection(request)

    return aiohttp.web.Response(status=200)


async def handle_user_delete_token(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Delete a token from the user."""
    project = request.match_info["project"]
    identifier = request.match_info["id"]

    try:
        await request.app["db_conn"].revoke_token(
            project,
            identifier
        )
    except InterfaceError:
        handle_dropped_connection(request)

    return aiohttp.web.Response(status=200)


async def handle_user_list_tokens(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Get project token listing."""
    project = request.match_info["project"]

    try:
        tokens = await request.app["db_conn"].get_tokens(project)
    except InterfaceError:
        handle_dropped_connection(request)

    # Return only the identifiers
    return aiohttp.web.json_response([
        rec["identifier"]
        for rec in tokens
    ])
