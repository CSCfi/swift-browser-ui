"""Miscallaneous convenience functions used during the project.

Module contains funcions for e.g. authenticating against openstack v3 identity
API, cache manipulation, cookies etc.
"""


import logging
import os
import secrets
import ssl
import typing

import aiohttp
import aiohttp.web
import aiohttp_session
import certifi
import redis.asyncio as redis
from redis.asyncio.sentinel import Sentinel

import swift_browser_ui.common.signature
from swift_browser_ui.ui.settings import setd

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())


async def sign(
    valid_for: int,
    path: str,
) -> typing.Dict[str, typing.Any]:
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


async def get_availability_from_token(
    token: str, client: aiohttp.ClientSession
) -> typing.Dict[str, typing.Any]:
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

    output_projects: typing.Dict[typing.Any, typing.Any] = {}
    output_domains: typing.Dict[typing.Any, typing.Any] = {}
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
    def filter_enabled(project: typing.Dict[str, typing.Any]) -> bool:
        if "enabled" in project:
            return bool(project["enabled"])
        return False

    filtered_projects: typing.List[typing.Dict[str, typing.Any]] = list(
        filter(filter_enabled, output_projects["projects"])
    )
    filtered_domains = output_domains["domains"]

    if len(filtered_projects) == 0:
        raise aiohttp.web.HTTPForbidden(
            reason="There are no projects available for this user.",
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
    return str(temp_url_key)


async def open_upload_runner_session(
    request: aiohttp.web.Request,
    project: str = "",
) -> str:
    """Open an upload session to the token."""
    session = await aiohttp_session.get_session(request)
    if not project:
        project = request.match_info["project"]
    try:
        return str(session["projects"][project]["runner"])
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


async def get_redis_client() -> redis.Redis:
    """Initialize and return a Python Redis client."""
    sentinel_url = str(os.environ.get("SWIFT_UI_REDIS_SENTINEL_HOST", ""))
    sentinel_port = str(os.environ.get("SWIFT_UI_REDIS_SENTINEL_PORT", ""))
    sentinel_master = os.environ.get("SWIFT_UI_REDIS_SENTINEL_MASTER", "mymaster")

    redis_user = str(os.environ.get("SWIFT_UI_REDIS_USER", ""))
    redis_password = str(os.environ.get("SWIFT_UI_REDIS_PASSWORD", ""))

    if sentinel_url and sentinel_port:
        # Auth is forwarded to redis so no need for auth on sentinel
        sentinel = Sentinel([(str(sentinel_url), int(sentinel_port))])

        redis_client = sentinel.master_for(
            service_name=sentinel_master,
            redis_class=redis.Redis,
            password=redis_password,
            username=redis_user,
        )
    else:
        redis_port = str(os.environ.get("SWIFT_UI_REDIS_PORT", ""))
        redis_host = str(os.environ.get("SWIFT_UI_REDIS_HOST", "localhost"))

        redis_creds = ""
        if redis_user and redis_password:
            redis_creds = f"{redis_user}:{redis_password}@"
        redis_client = redis.from_url(f"redis://{redis_creds}{redis_host}:{redis_port}")
    return redis_client
