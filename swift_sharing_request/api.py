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
    # Future authorization check here

    # Check for incorrect client query here

    container = request.match_info("container")
    user = request.match_info("user")
    owner = request.query["owner"]

    try:
        request.app["db_conn"].add_request(
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
    # Future authorization check here

    # Check for incorrect client query here

    user = request.match_info("user")

    try:
        ret = request.app["db_conn"].get_request_owned(user)
    except InterfaceError:
        handle_dropped_connection(request)

    return aiohttp.web.json_response(ret)


async def handle_user_made_request_listing(request):
    """Handle query listing for the requests created by the user."""
    # Future authorization check here

    # Check for incorrect client query here

    user = request.match_info("user")

    try:
        ret = request.app["db_conn"].get_request_made(user)
    except InterfaceError:
        handle_dropped_connection(request)

    return aiohttp.web.json_response(ret)


async def handle_container_request_listing(request):
    """Handle query for listing the container share requests."""
    # Future authorization check here

    # Check for incorrect client query here

    container = request.match_info("container")

    try:
        ret = request.app["db_conn"].get_request_container(container)
    except InterfaceError:
        handle_dropped_connection(request)

    return aiohttp.web.json_response(ret)


async def handle_user_share_request_delete(request):
    """Delete container share request or requests."""
    # Future authorizaion check here

    # Check for incorrect client query here

    container = request.match_info("container")
    user = request.match_info("user")
    owner = request.query["owner"]

    try:
        request.app["db_conn"].delete_request(container, owner, user)
    except InterfaceError:
        handle_dropped_connection(request)

    return aiohttp.web.Response(
        status=200,
        body="OK"
    )
