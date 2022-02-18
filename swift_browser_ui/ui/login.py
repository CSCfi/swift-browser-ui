"""A module for handling the project login related tasks."""


import time
import re
import base64
import binascii

# aiohttp
import aiohttp.web
import aiohttp_session
from multidict import MultiDictProxy

import typing

from swift_browser_ui.ui._convenience import (
    disable_cache,
    get_availability_from_token,
)
from swift_browser_ui.ui.settings import setd


async def handle_login(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Create new session cookie for the user."""
    response = aiohttp.web.Response(status=302, reason="Redirection to login")

    # Add a cookie for navigating
    if "navto" in request.query.keys():
        response.set_cookie("NAV_TO", request.query["navto"], expires=str(3600))

    response.headers["Location"] = "/login/front"

    return response


async def sso_query_begin(
    _: typing.Union[aiohttp.web.Request, None]
) -> typing.Union[aiohttp.web.Response, aiohttp.web.FileResponse]:
    """Display login page and initiate federated keystone authentication."""
    # Return the form based login page if the service isn't trusted
    response: typing.Union[aiohttp.web.Response, aiohttp.web.FileResponse]
    if not setd["has_trust"]:
        response = aiohttp.web.FileResponse(str(setd["static_directory"]) + "/login.html")
        return disable_cache(response)

    response = aiohttp.web.Response(
        status=302,
    )

    response.headers["Location"] = (
        f"{str(setd['auth_endpoint_url'])}/auth/OS-FEDERATION/identity_providers"
        f"/haka/protocols/saml2/websso?origin={str(setd['set_origin_address'])}"
    )

    return response


def test_token(
    formdata: MultiDictProxy[typing.Union[str, bytes, aiohttp.web.FileField]],
    request: aiohttp.web.Request,
) -> str:
    """Validate unscoped token."""
    unscoped: typing.Union[str, None] = None
    log = request.app["Log"]
    if "token" in formdata:
        unscoped = str(formdata["token"])
        log.debug(
            f"Got OS token in formdata from address {request.remote} :: {time.ctime()}"
        )
    # Try getting the token id from form
    if "token" in request.query and unscoped is None:
        unscoped = request.query["token"]
        log.debug(
            "Got OS token in query string "
            f"from address {request.remote} :: {time.ctime()}"
        )
    # Try getting the token id from headers
    if "X-Auth-Token" in request.headers and unscoped is None:
        unscoped = request.headers["X-Auth-Token"]
        log.debug(
            "Got OS token in http header "
            f"from address {request.remote} :: {time.ctime()}"
        )
    if unscoped is None:
        raise aiohttp.web.HTTPBadRequest(reason="Token missing from query")
    if not (re.match("[a-f0-9]{32}", unscoped) and len(unscoped) == 32):
        try:
            # Check the magic byte matches a fernet token
            if not base64.urlsafe_b64decode(unscoped.encode("utf-8"))[:1] == b"\x80":
                raise aiohttp.web.HTTPBadRequest(reason="Token is malformed")
        # Handle failures in base64decode
        except (binascii.Error, UnicodeDecodeError):
            raise aiohttp.web.HTTPBadRequest(reason="Token is malformed")

    log.info("Got OS token in login return")

    return unscoped


async def credentials_login_end(
    request: aiohttp.web.Request,
) -> typing.Union[aiohttp.web.Response, aiohttp.web.FileResponse]:
    """Handle the login procedure with classic POST."""
    log = request.app["Log"]
    client = request.app["api_client"]
    log.info("Got login request with username, password")

    form = await request.post()

    try:
        username = str(form["username"])
        password = str(form["password"])
    except KeyError:
        raise aiohttp.web.HTTPBadRequest(reason="Username or password not provided")

    # Get an unscoped token with credentials
    async with client.post(
        f"{setd['auth_endpoint_url']}/auth/tokens",
        json={
            "auth": {
                "identity": {
                    "methods": [
                        "password",
                    ],
                    "password": {
                        "user": {
                            "name": username,
                            "domain": {
                                "name": "Default",
                            },
                            "password": password,
                        },
                    },
                },
                "scope": "unscoped",
            },
        },
    ) as resp:
        if resp.status == 400:
            text = await (resp.text())
            request.app["Log"].debug(text)
            raise aiohttp.web.HTTPBadRequest(reason="No username or password provided.")
        if resp.status == 401:
            text = await (resp.text())
            request.app["Log"].debug(text)
            raise aiohttp.web.HTTPUnauthorized(
                reason="Wrong username or password, or no access to the service."
            )
        if resp.status != 201:
            text = await (resp.text())
            request.app["Log"].debug(text)
            raise aiohttp.web.HTTPUnauthorized

        unscoped = resp.headers["X-Subject-Token"]
        log.debug("Got token in password auth")
        return await login_with_token(request, unscoped)


async def sso_query_end(
    request: aiohttp.web.Request,
) -> typing.Union[aiohttp.web.Response, aiohttp.web.FileResponse]:
    """Handle the login procedure return from SSO or user from POST."""
    formdata = await request.post()
    # Declare the unscoped token
    unscoped = test_token(formdata, request)

    return await login_with_token(request, unscoped)


async def login_with_token(
    request: aiohttp.web.Request,
    token: str,
) -> typing.Union[aiohttp.web.Response, aiohttp.web.FileResponse]:
    """Log in a session with token."""
    # Establish connection and begin user session
    response: typing.Union[aiohttp.web.Response, aiohttp.web.FileResponse]
    response = aiohttp.web.Response(
        status=303,
        body=None,
    )
    client = request.app["api_client"]
    session = await aiohttp_session.new_session(request)

    session["at"] = time.time()

    session["referer"] = request.url.host
    uname = ""

    # Check token availability
    avail = await get_availability_from_token(token, client)
    session["projects"] = {}
    # Scope a token for all accessible projects
    for project in avail["projects"]:
        async with client.post(
            f"{setd['auth_endpoint_url']}/auth/tokens",
            json={
                "auth": {
                    "identity": {
                        "methods": [
                            "token",
                        ],
                        "token": {
                            "id": token,
                        },
                    },
                    "scope": {"project": {"id": project["id"]}},
                }
            },
        ) as resp:
            if resp.status == 401:
                raise aiohttp.web.HTTPUnauthorized(reason="Token is not valid")
            if resp.status == 403:
                raise aiohttp.web.HTTPForbidden(reason="No access to service with token.")
            ret = await resp.json()

            request.app["Log"].debug(f"token output: {ret}")

            obj_role = False
            request.app["Log"].debug(f'roles: {ret["token"]["roles"]}')
            for role in ret["token"]["roles"]:
                if role["name"] in {"object_store_user", "admin"}:
                    obj_role = True
            if not obj_role:
                continue

            scoped = resp.headers["X-Subject-Token"]
            # Use the first available public endpoint
            endpoint = [
                list(filter(lambda i: i["interface"] == "public", i["endpoints"]))[0]
                for i in filter(
                    lambda i: i["type"] == "object-store", ret["token"]["catalog"]
                )
            ][0]

            request.app["Log"].debug(endpoint)

            if not uname:
                uname = ret["token"]["user"]["name"]

            session["projects"][project["id"]] = {
                "id": project["id"],
                "name": project["name"],
                "endpoint": endpoint["url"],
                "token": scoped,
            }

    session["token"] = token
    session["uname"] = uname

    session.changed()
    # Redirect to the browse page
    if "NAV_TO" in request.cookies.keys():
        response.headers["Location"] = request.cookies["NAV_TO"]
        response.del_cookie("NAV_TO")
    else:
        response.headers["Location"] = "/browse"

    return response


async def handle_logout(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Properly kill the session for the user."""
    log = request.app["Log"]
    client = request.app["api_client"]
    if not setd["set_session_devmode"]:
        try:
            session = await aiohttp_session.get_session(request)
            log.info(f"Killing session {session.identity}")
            for project in session["projects"]:
                async with client.delete(
                    f"{setd['auth_endpoint_url']}/auth/tokens",
                    headers={
                        "X-Auth-Token": session["token"],
                        "X-Subject-Token": session["projects"][project]["token"],
                    },
                ):
                    pass
            session.invalidate()
        except aiohttp.web.HTTPUnauthorized:
            log.info("Trying to log our an invalidated session")
            raise aiohttp.web.HTTPUnauthorized
    response = aiohttp.web.Response(status=303)
    response.headers["Location"] = "/"
    return response
