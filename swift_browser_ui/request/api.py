"""Module for share request API handlers."""


import logging
import os
import aiohttp.web
from asyncpg import InterfaceError


from swift_browser_ui.request.db import handle_dropped_connection


MODULE_LOGGER = logging.getLogger("api")
MODULE_LOGGER.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))


async def handle_share_request_post(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
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


async def handle_user_owned_request_listing(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Handle query for listing the requests owned by the user."""
    user = request.match_info["user"]
    ret = []
    try:
        ret = await request.app["db_conn"].get_request_owned(user)
    except InterfaceError:
        handle_dropped_connection(request)

    MODULE_LOGGER.log(
        logging.DEBUG,
        f"Returning requests owned by user: {ret}"
    )

    return aiohttp.web.json_response(ret)


async def handle_user_made_request_listing(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Handle query listing for the requests created by the user."""
    user = request.match_info["user"]
    ret = []
    try:
        ret = await request.app["db_conn"].get_request_made(user)
    except InterfaceError:
        handle_dropped_connection(request)

    MODULE_LOGGER.log(
        logging.DEBUG,
        f"Returning requests made by user: {ret}"
    )

    return aiohttp.web.json_response(ret)


async def handle_container_request_listing(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Handle query for listing the container share requests."""
    container = request.match_info["container"]
    ret = []
    try:
        ret = await request.app["db_conn"].get_request_container(container)
    except InterfaceError:
        handle_dropped_connection(request)

    MODULE_LOGGER.log(
        logging.DEBUG,
        f"Returning container shared requests: {ret}"
    )

    return aiohttp.web.json_response(ret)


async def handle_user_share_request_delete(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Delete container share request or requests."""
    container = request.match_info["container"]
    user = request.match_info["user"]
    owner = request.query["owner"]

    try:
        await request.app["db_conn"].delete_request(container, owner, user)
    except InterfaceError:
        handle_dropped_connection(request)

    MODULE_LOGGER.log(
        logging.DEBUG,
        f"Deleted {container} for owner {owner}"
    )

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

    MODULE_LOGGER.log(
        logging.DEBUG,
        f"Deleted {identifier} for project {project}"
    )

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
