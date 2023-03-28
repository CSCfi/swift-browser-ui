"""Miscallaneous convenience functions used during the project.

Module contains funcions for e.g. authenticating against openstack v3 identity
API, cache manipulation, cookies etc.
"""


import logging
import secrets
import ssl
import typing

import aiohttp
import aiohttp.web
import aiohttp_session
import certifi
import requests

import swift_browser_ui.common.signature
from swift_browser_ui.ui.settings import setd

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())


def test_swift_endpoint(endpoint: str) -> None:
    """Test swift endpoint connectivity."""
    try:
        requests.head(endpoint, timeout=5)
    except requests.exceptions.ConnectionError as e:
        logging.debug(f"The {endpoint} couldn't fulfill the request.")
        logging.debug(f"Error code: {e}")
        raise aiohttp.web.HTTPServiceUnavailable(
            reason="Cannot get Swift endpoint connection."
        )
    else:
        logging.info("Swift endpoint accessible.")


async def sign(
    valid_for: int,
    path: str,
) -> dict:
    """Perform a general signature."""
    try:
        key = str(setd["sharing_request_token"]).encode("utf-8")
    except (KeyError, AttributeError):
        raise aiohttp.web.HTTPNotImplemented(
            reason="Server doesn't have signing permissions."
        )

    return swift_browser_ui.common.signature.sign_api_request(
        path, valid_for=valid_for, key=key
    )


def disable_cache(
    response: typing.Union[aiohttp.web.Response, aiohttp.web.FileResponse]
) -> typing.Union[aiohttp.web.Response, aiohttp.web.FileResponse]:
    """Add cache disabling headers to an aiohttp response."""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-Cache"
    response.headers["Expires"] = "0"
    return response


async def get_availability_from_token(token: str, client: aiohttp.ClientSession) -> dict:
    """List available domains and projects for the unscoped token specified.

    Params:
        token: str
    Returns:
        Dictionary containing both the available projects and available domains
    Return type:
        dict(keys=('projects': List(str), 'domains': List(str)))
    """
    # setup token header
    hdr = {
        "X-Auth-Token": token,
    }

    output_projects = None
    output_domains = None
    # Check projects from the API
    async with client.get(
        f"{setd['auth_endpoint_url']}/OS-FEDERATION/projects",
        headers=hdr,
    ) as resp:
        if resp.status == 401:
            raise aiohttp.web.HTTPUnauthorized(
                reason="Invalid token.",
                headers={"WWW-Authenticate": 'Bearer realm="/", charset="UTF-8"'},
            )
        if resp.status == 200:
            output_projects = await resp.json()

    # Check domains from the API
    async with client.get(
        f"{setd['auth_endpoint_url']}/OS-FEDERATION/domains",
        headers=hdr,
    ) as resp:
        if resp.status == 401:
            raise aiohttp.web.HTTPUnauthorized(
                reason="Invalid token.",
                headers={"WWW-Authenticate": 'Bearer realm="/", charset="UTF-8"'},
            )
        if resp.status == 200:
            output_domains = await resp.json()

    logging.info(f"{str(output_projects)}\n{str(output_domains)}")

    # we need to take the projects that have been enabled for the
    # user, otherwise if the first project is disabled we will
    # get a 401 response when we do initiate_os_service
    def filter_enabled(project) -> bool:
        if "enabled" in project:
            return project["enabled"]
        return False

    filtered_projects = list(filter(filter_enabled, output_projects["projects"]))  # type: ignore
    filtered_domains = output_domains["domains"]  # type: ignore

    if len(filtered_projects) == 0:
        raise aiohttp.web.HTTPForbidden(
            reason="Thre is no project available for this user.",
            headers={"WWW-Authenticate": 'Bearer realm="/", charset="UTF-8"'},
        )

    # Return all project names and domain names inside a dictionary
    return {
        "projects": filtered_projects,
        "domains": filtered_domains,
    }


async def get_tempurl_key(request: aiohttp.web.Request) -> str:
    """Get the correct temp URL key from Openstack."""
    session = await aiohttp_session.get_session(request)
    client = request.app["api_client"]
    project = request.match_info["project"]

    try:
        async with client.head(
            session["projects"][project]["endpoint"],
            headers={
                "X-Auth-Token": session["projects"][project]["token"],
            },
        ) as ret:
            try:
                temp_url_key = ret.headers["X-Account-Meta-Temp-Url-Key"]
            except KeyError:
                temp_url_key = ret.headers["X-Account-Meta-Temp-Url-Key-2"]
    except KeyError:
        temp_url_key = secrets.token_urlsafe(32)
        async with client.post(
            session["projects"][project]["endpoint"],
            headers={
                "X-Auth-Token": session["projects"][project]["token"],
                "X-Account-Meta-Temp-Url-Key-2": temp_url_key,
            },
        ) as ret:
            if ret.status != 204:
                raise aiohttp.web.HTTPServerError(reason="TempURL key creation failure.")
    return temp_url_key


async def open_upload_runner_session(
    request: aiohttp.web.Request,
    project: str = "",
) -> str:
    """Open an upload session to the token."""
    session = await aiohttp_session.get_session(request)
    if not project:
        project = request.match_info["project"]
    try:
        return session["projects"][project]["runner"]
    except KeyError:
        client = request.app["api_client"]
        path = f"{setd['upload_internal_endpoint']}/{project}"
        signature = await sign(3600, f"/{project}")
        async with client.post(
            path,
            data={"token": session["token"]},
            params=signature,
            ssl=ssl_context,
        ) as resp:
            ret = str(resp.cookies["RUNNER_SESSION_ID"].value)
            session["projects"][project]["runner"] = ret
            session.changed()
        return ret
