"""Sharing backend API specification and implementation."""


import logging
import asyncio

import aiohttp.web
from asyncpg import InterfaceError


MODULE_LOGGER = logging.getLogger("api")


def handle_dropped_connection(
        request: aiohttp.web.Request
):
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


async def has_access_handler(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Handle has-access endpoint query."""
    try:
        access_list = await request.app["db_conn"].get_access_list(
            request.match_info["user"]
        )
    except InterfaceError:
        handle_dropped_connection(request)

    MODULE_LOGGER.log(
        logging.DEBUG,
        "Returning following access list: %s", str(access_list)
    )

    return aiohttp.web.json_response(access_list)


async def access_details_handler(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Handle access-details endpoint query."""
    try:
        access_details = \
            await request.app["db_conn"].get_access_container_details(
                request.match_info["user"],
                request.query["owner"],
                request.match_info["container"])
    except InterfaceError:
        handle_dropped_connection(request)

    MODULE_LOGGER.log(
        logging.DEBUG,
        "Returning following access details: %s", str(access_details)
    )

    return aiohttp.web.json_response(access_details)


async def gave_access_handler(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Handle gave-access endpoint query."""
    try:
        shared_list = await request.app["db_conn"].get_shared_list(
            request.match_info["owner"]
        )
    except InterfaceError:
        handle_dropped_connection(request)

    MODULE_LOGGER.log(
        logging.DEBUG,
        "Returning following shared container listing: %s",
        str(shared_list)
    )

    return aiohttp.web.json_response(shared_list)


async def shared_details_handler(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Handle shared-details endpoint query."""
    try:
        shared_details = \
            await request.app["db_conn"].get_shared_container_details(
                request.match_info["owner"],
                request.match_info["container"])
    except InterfaceError:
        handle_dropped_connection(request)

    MODULE_LOGGER.log(
        logging.DEBUG,
        "Returning following shared container details: %s",
        str(shared_details)
    )

    return aiohttp.web.json_response(shared_details)


async def share_container_handler(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Handle share-container endpoint query."""
    try:
        shared = await request.app["db_conn"].add_share(
            request.match_info["owner"],
            request.match_info["container"],
            request.query["user"].split(","),
            request.query["access"].split(","),
            request.query["address"]
        )
    except InterfaceError:
        handle_dropped_connection(request)

    MODULE_LOGGER.log(
        logging.DEBUG,
        "Added following new shares: %s", str(shared)
    )

    return aiohttp.web.json_response(shared)


async def edit_share_handler(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Handle container shared rights editions."""
    try:
        edited = await request.app["db_conn"].edit_share(
            request.match_info["owner"],
            request.match_info["container"],
            request.query["user"].split(","),
            request.query["access"].split(",")
        )
    except InterfaceError:
        handle_dropped_connection(request)

    MODULE_LOGGER.log(
        logging.DEBUG,
        "Edited following shares: %s", str(edited)
    )

    return aiohttp.web.json_response(edited)


async def delete_share_handler(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Handle unshare-container endpoint query."""
    try:
        deleted = await request.app["db_conn"].delete_share(
            request.match_info["owner"],
            request.match_info["container"],
            request.query["user"].split(",")
        )
    except InterfaceError:
        handle_dropped_connection(request)
    except KeyError:
        # If can't find user from query, the client wants a bulk unshare
        return await delete_container_shares_handler(
            request
        )

    MODULE_LOGGER.log(
        logging.DEBUG,
        "Deleted following shares: %s", str(deleted)
    )

    return aiohttp.web.Response(
        status=204,
        body="OK"
    )


async def delete_container_shares_handler(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Delete all shares from a container."""
    try:
        deleted = await request.app["db_conn"].delete_container_shares(
            request.match_info["owner"],
            request.match_info["container"]
        )
    except InterfaceError:
        handle_dropped_connection(request)

    MODULE_LOGGER.log(
        logging.DEBUG,
        "Deleted following shares: %s", str(deleted)
    )

    return aiohttp.web.Response(
        status=204,
        body="OK"
    )


async def handle_user_add_token(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Add a token to the user."""
    project = request.match_info["project"]
    identifier = request.match_info["id"]

    try:
        token = request.query["token"]
    except KeyError:
        try:
            formdata = await request.post()
            token = formdata["token"]
        except KeyError:
            raise aiohttp.web.HTTPBadRequest(
                reason="No token present"
            )

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
