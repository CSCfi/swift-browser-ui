"""Sharing backend API specification and implementation."""


import logging
import os
import aiohttp.web
from asyncpg import InterfaceError

from .db import handle_dropped_connection


MODULE_LOGGER = logging.getLogger("api")
MODULE_LOGGER.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))


async def has_access_handler(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Handle has-access endpoint query."""
    access_list = []
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
    access_details = dict()
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
    shared_list = []
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
    shared_details = dict()
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
    shared: bool = False
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
        "Added following new shared containers: %s",
        str(request.match_info["container"])
    )

    return aiohttp.web.json_response(shared)


async def edit_share_handler(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Handle container shared rights editions."""
    edited: bool = False
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
        "Edited following shared containers: %s",
        str(request.match_info["container"])
    )

    return aiohttp.web.json_response(edited)


async def delete_share_handler(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Handle unshare-container endpoint query."""
    try:
        await request.app["db_conn"].delete_share(
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
        "Deleted following shared containers: %s",
        str(request.match_info["container"])
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
        await request.app["db_conn"].delete_container_shares(
            request.match_info["owner"],
            request.match_info["container"]
        )
    except InterfaceError:
        handle_dropped_connection(request)

    MODULE_LOGGER.log(
        logging.DEBUG,
        "Deleted following shared container: %s",
        str(request.match_info["container"])
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
            token = str(formdata["token"])
        except KeyError:
            MODULE_LOGGER.log(
                logging.ERROR, "No token present"
            )
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
    tokens = []
    try:
        tokens = await request.app["db_conn"].get_tokens(project)
    except InterfaceError:
        handle_dropped_connection(request)

    # Return only the identifiers
    return aiohttp.web.json_response([
        rec["identifier"]
        for rec in tokens
    ])


async def handle_health_check(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Answer a service health check."""
    # Case degraded
    try:
        if request.app["db_conn"].conn.is_closed():
            MODULE_LOGGER.log(
                logging.DEBUG, "Database closed"
            )
            return aiohttp.web.json_response({
                "status": "Degraded",
                "degraded": [
                    "database"
                ]
            })
    except AttributeError:
        MODULE_LOGGER.log(
            logging.ERROR, "Degraded Database"
        )
        return aiohttp.web.json_response({
            "status": "Degraded",
            "degraded": [
                "database"
            ]
        })

    # Case nominal
    return aiohttp.web.json_response({
        "status": "Ok",
    })
