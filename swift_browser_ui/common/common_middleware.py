"""Common API middleware."""


import logging
import os
import typing

import aiohttp.web
import asyncpg.exceptions

import swift_browser_ui.common.signature
import swift_browser_ui.common.types

LOGGER = logging.getLogger("swift_browser_ui.common.common_middleware")
LOGGER.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


@aiohttp.web.middleware
async def add_cors(
    request: aiohttp.web.Request, handler: swift_browser_ui.common.types.AiohttpHandler
) -> aiohttp.web.Response:
    """Add CORS header for API responses."""
    try:
        resp = await handler(request)
        if "origin" in request.headers.keys():
            resp.headers["Access-Control-Allow-Origin"] = request.headers["origin"]
        return resp
    except aiohttp.web.HTTPError as error:
        if "origin" in request.headers.keys():
            error.headers["Access-Control-Allow-Origin"] = request.headers["origin"]
        raise error


@aiohttp.web.middleware
async def catch_uniqueness_error(
    request: aiohttp.web.Request, handler: swift_browser_ui.common.types.AiohttpHandler
) -> aiohttp.web.Response:
    """Catch excepetion arising from a non-unique primary key."""
    try:
        return await handler(request)
    except asyncpg.exceptions.UniqueViolationError:
        raise aiohttp.web.HTTPConflict(reason="Duplicate entries are not allowed.")


@aiohttp.web.middleware
async def check_db_conn(
    request: aiohttp.web.Request, handler: swift_browser_ui.common.types.AiohttpHandler
):
    """Check if an established database connection exists."""
    if request.path == "/health":
        return await handler(request)
    if request.app["db_conn"] is None:
        return await handler(request)
    if request.app["db_conn"].pool is None:
        raise aiohttp.web.HTTPServiceUnavailable(
            reason="Database connection not established."
        )
    try:
        return await handler(request)
    except asyncpg.exceptions.InterfaceError:
        raise aiohttp.web.HTTPServiceUnavailable(reason="Database connection error")


@aiohttp.web.middleware
async def handle_validate_authentication(
    request: aiohttp.web.Request,
    handler: swift_browser_ui.common.types.AiohttpHandler,
) -> aiohttp.web.Response:
    """Handle the authentication of a response as a middleware function."""
    if request.path == "/health":
        return await handler(request)

    try:
        signature = request.query["signature"]
        validity = request.query["valid"]
        path = request.url.path
    except KeyError:
        LOGGER.debug("Query string missing validity or signature")
        raise aiohttp.web.HTTPBadRequest(
            reason="Query string missing validity or signature"
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
            except asyncpg.exceptions.InterfaceError:
                pass
        else:
            if request.path != "/health":
                LOGGER.debug(f"No project ID found in request {request}")
                raise aiohttp.web.HTTPUnauthorized(reason="No project ID in request")

    await swift_browser_ui.common.signature.test_signature(
        request.app["tokens"] + project_tokens, signature, validity + path, validity
    )

    return await handler(request)
