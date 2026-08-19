"""Module for handling queries for a valid Sharing/Request API signature."""

import logging
import secrets

import aiohttp.web
import aiohttp_session

import swift_browser_ui.ui._convenience

from .settings import setd

LOGGER = logging.getLogger("signature")


async def handle_signature_request(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Handle call for an API call signature."""
    session = await aiohttp_session.get_session(request)
    if not session["projects"]:
        raise aiohttp.web.HTTPUnauthorized(reason="No valid project for session.")
    try:
        valid_for = int(request.match_info["valid"])
        path_to_sign = request.query["path"]
    except KeyError:
        raise aiohttp.web.HTTPBadRequest(
            reason="Signable path missing from query string."
        )

    # Validate that the signed path is accessing content allowed in context
    # by checking the signed path contains one of the allowed projects
    matching_project = False
    for project in session["projects"].keys():
        if project in path_to_sign:
            matching_project = True

        # Also check against the project name
        if session["projects"][project]["name"] in path_to_sign:
            matching_project = True

    # Allow ids to be queried for any project
    if path_to_sign.startswith("/ids") and request.method == "GET":
        matching_project = True

    if matching_project:
        return aiohttp.web.json_response(
            await swift_browser_ui.ui._convenience.sign(valid_for, path_to_sign)
        )
    else:
        # Raise in case user tries accessing project beyond verified scope
        LOGGER.info(f"Could not find a valid project in {path_to_sign}")
        LOGGER.info(f"Valid projects were {list(session['projects'].keys())}")
        raise aiohttp.web.HTTPForbidden(
            reason="Path contains a project not accessible in login scope."
        )


async def handle_ext_token_create(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Handle call for an API token create."""
    session = await aiohttp_session.get_session(request)
    project = request.match_info["project"]

    if project not in session["projects"]:
        raise aiohttp.web.HTTPForbidden(reason="No access to the project.")

    LOGGER.debug(f"Creating a scoped API token for {project}")

    ident = request.match_info["id"]
    token = secrets.token_hex(64)

    client: aiohttp.ClientSession = request.app["api_client"]

    sharing_api_address = setd["sharing_internal_endpoint"]

    if not sharing_api_address:
        raise aiohttp.web.HTTPNotFound(reason="External APIs not configured on server")

    path = f"/token/{project}/{ident}"
    signature = await swift_browser_ui.ui._convenience.sign(3600, path)
    signature["name"] = session["projects"][project]["name"]

    async with client.post(
        f"{sharing_api_address}{path}",
        data={"token": token},
        params=signature,
    ) as id_resp:
        if id_resp.status != 200:
            raise aiohttp.web.HTTPInternalServerError(reason="Token creation failed")

    resp = aiohttp.web.json_response(token, status=201)

    return resp


async def handle_ext_token_remove(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Handle call for an API token delete."""
    session = await aiohttp_session.get_session(request)

    project = request.match_info["project"]
    if project not in session["projects"]:
        raise aiohttp.web.HTTPForbidden(reason="No access to the project.")

    ident = request.match_info["id"]

    client: aiohttp.ClientSession = request.app["api_client"]

    sharing_api_address = setd["sharing_internal_endpoint"]

    if not sharing_api_address:
        raise aiohttp.web.HTTPNotFound(reason=("External APIs not configured on server"))

    path = f"/token/{project}/{ident}"
    signature = await swift_browser_ui.ui._convenience.sign(3600, path)

    await client.delete(
        f"{sharing_api_address}{path}",
        params=signature,
    )

    resp = aiohttp.web.Response(status=204)

    return resp


async def handle_ext_token_list(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Handle call for listing API tokens."""
    session = await aiohttp_session.get_session(request)

    project = request.match_info["project"]
    if project not in session["projects"]:
        raise aiohttp.web.HTTPForbidden(reason="No access to the project.")

    client: aiohttp.ClientSession = request.app["api_client"]

    sharing_api_address = setd["sharing_internal_endpoint"]

    if not sharing_api_address:
        raise aiohttp.web.HTTPNotFound(reason=("External APIs not configured on server"))

    path = f"/token/{project}"
    signature = await swift_browser_ui.ui._convenience.sign(3600, path)

    async with client.get(
        f"{sharing_api_address}{path}",
        params={
            "signature": signature["signature"],
            "valid": signature["valid"],
        },
    ) as a_resp:
        sharing_tokens_text = await a_resp.text()

    LOGGER.debug(f"Sharing tokens: {sharing_tokens_text}")

    resp = aiohttp.web.Response(text=sharing_tokens_text)

    return resp
