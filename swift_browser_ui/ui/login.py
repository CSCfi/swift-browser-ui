"""A module for handling the project login related tasks."""


import base64
import binascii
import re
import time
import typing

# aiohttp
import aiohttp.web
import aiohttp_session
from multidict import MultiDictProxy
from oidcrp.exception import OidcServiceError

from swift_browser_ui.ui._convenience import (
    disable_cache,
    get_availability_from_token,
)
from swift_browser_ui.ui.settings import setd

HAKA_ENDPOINT = (
    "{endpoint}/auth/OS-FEDERATION/identity_providers"
    "/haka/protocols/saml2/websso?origin={origin}"
).format

HAKA_OIDC_ENDPOINT = (
    "{endpoint}/auth/OS-FEDERATION/identity_providers"
    "/{oidc}/protocols/openid/websso?origin={origin}"
).format


async def oidc_start(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Redirect to OpenID Connect provider."""
    try:
        oidc = request.app["oidc_client"].begin("oidc")
    except Exception as e:
        # This can be caused if config is improperly configured, and
        # oidcrp is unable to fetch oidc configuration from the given URL
        request.app["Log"].error(f"OIDC authorization request failed: {e}")
        raise aiohttp.web.HTTPInternalServerError(
            reason="OIDC authorization request failed."
        )

    response = aiohttp.web.Response(status=302, reason="Redirection to login")
    response.headers["Location"] = oidc["url"]
    return response


async def oidc_end(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Finalize OIDC login and create a new session with the data from the OIDC provicer."""
    # Response from AAI must have the query params `state` and `code`
    if "state" in request.query and "code" in request.query:
        request.app["Log"].debug("AAI response contained the correct params.")
        params = {"state": request.query["state"], "code": request.query["code"]}
    else:
        reason = f"AAI response is missing mandatory params, received: {request.query}"
        raise aiohttp.web.HTTPBadRequest(reason=reason)

    # Verify oidc_state and retrieve auth session
    try:
        oidc_session = request.app["oidc_client"].get_session_information(params["state"])
    except KeyError as e:
        # This exception is raised if the RPHandler doesn't have the supplied "state"
        request.app["Log"].error(f"OIDC not initialised: {e}")
        raise aiohttp.web.HTTPForbidden(reason="Bad OIDC session.")

    oidc_session["auth_request"]["code"] = params["code"]
    # finalize requests id_token and access_token with code, validates them and requests userinfo data
    try:
        oidc_result = request.app["oidc_client"].finalize(
            oidc_session["iss"], oidc_session["auth_request"]
        )
    except KeyError as e:
        request.app["Log"].error(f"Issuer {oidc_session['iss']} not found: {e}.")
        raise aiohttp.web.HTTPBadRequest(reason="Token issuer not found.")
    except OidcServiceError as e:
        # This exception is raised if RPHandler encounters an error due to:
        # 1. "code" is wrong, so token request failed
        # 2. token validation failed
        # 3. userinfo request failed
        request.app["Log"].error(f"OIDC Callback failed with: {e}")
        raise aiohttp.web.HTTPBadRequest(reason="Invalid OIDC callback.")

    session = await aiohttp_session.new_session(request)
    session["at"] = time.time()
    session["referer"] = request.url.host
    session["oidc"] = {
        "userinfo": oidc_result["userinfo"].to_dict(),
        "state": oidc_result["state"],
        "access_token": oidc_result["token"],
    }

    csc_projects: typing.List[typing.Any] | None = _get_projects_from_userinfo(
        session["oidc"]["userinfo"]
    )
    # add entry to session only if the OIDC provider has csc-projects in userinfo
    if csc_projects is not None:
        session["csc-projects"] = csc_projects
    request.app["Log"].debug(session["oidc"])

    response = aiohttp.web.Response(
        status=302, headers={"Location": "/login"}, reason="Redirection to login"
    )

    if session["oidc"]["userinfo"].get("homeFederation", "") == "Haka":
        response.headers["Location"] = HAKA_OIDC_ENDPOINT(
            endpoint=str(setd["auth_endpoint_url"]),
            oidc=str(setd["keystone_oidc_provider"]),
            origin=str(setd["set_origin_address"]),
        )

    session.changed()

    return response


async def handle_login(
    request: aiohttp.web.Request,
) -> typing.Union[aiohttp.web.Response, aiohttp.web.FileResponse]:
    """Create new session cookie for the user."""
    response: typing.Union[aiohttp.web.Response, aiohttp.web.FileResponse]
    response = aiohttp.web.Response(status=302, reason="Redirection to login")

    # Add a cookie for navigating
    if "navto" in request.query.keys():
        response.set_cookie("NAV_TO", request.query["navto"], expires=str(3600))

    if setd["oidc_enabled"]:
        session = await aiohttp_session.get_session(request)
        if session.new or "oidc" not in session:
            session.invalidate()
            response.headers["Location"] = "/"
        else:
            response = aiohttp.web.FileResponse(
                str(setd["static_directory"]) + "/login2step.html"
            )

    else:
        response.headers["Location"] = "/login/front"

    return response


async def sso_query_begin(
    request: typing.Union[aiohttp.web.Request, None]
) -> typing.Union[aiohttp.web.Response, aiohttp.web.FileResponse]:
    """Display login page and initiate federated keystone authentication."""
    # Return the form based login page if the service isn't trusted
    response: typing.Union[aiohttp.web.Response, aiohttp.web.FileResponse]

    if request and setd["oidc_enabled"]:
        session = await aiohttp_session.get_session(request)
        if session.new or "oidc" not in session:
            session.invalidate()
            return aiohttp.web.Response(status=302, headers={"Location": "/"})
    if not setd["has_trust"]:
        response = aiohttp.web.FileResponse(str(setd["static_directory"]) + "/login.html")
        return disable_cache(response)

    response = aiohttp.web.Response(
        status=302,
    )

    response.headers["Location"] = HAKA_ENDPOINT(
        endpoint=str(setd["auth_endpoint_url"]), origin=str(setd["set_origin_address"])
    )

    return response


async def sso_query_begin_oidc(
    request: typing.Union[aiohttp.web.Request, None]
) -> typing.Union[aiohttp.web.Response, aiohttp.web.FileResponse]:
    """Initiate a federated Keystone authentication with OIDC."""
    response: typing.Union[aiohttp.web.Response, aiohttp.web.FileResponse]

    if request and setd["oidc_enabled"]:
        session = await aiohttp_session.get_session(request)
        if session.new or "oidc" not in session:
            session.invalidate()
            return aiohttp.web.Response(status=302, headers={"Location": "/"})
    if not setd["has_trust"]:
        response = aiohttp.web.FileResponse(str(setd["static_directory"]) + "/login.html")
        return disable_cache(response)

    return aiohttp.web.Response(
        status=302,
        headers={
            "Location": HAKA_OIDC_ENDPOINT(
                endpoint=str(setd["auth_endpoint_url"]),
                oidc=str(setd["keystone_oidc_provider"]),
                origin=str(setd["set_origin_address"]),
            ),
        },
    )


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
            text = await resp.text()
            request.app["Log"].debug(text)
            raise aiohttp.web.HTTPBadRequest(reason="No username or password provided.")
        if resp.status == 401:
            text = await resp.text()
            request.app["Log"].debug(text)
            raise aiohttp.web.HTTPUnauthorized(
                reason="Wrong username or password, or no access to the service."
            )
        if resp.status != 201:
            text = await resp.text()
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

    session = (
        await aiohttp_session.get_session(request)
        if setd["oidc_enabled"]
        else await aiohttp_session.new_session(request)
    )

    if setd["oidc_enabled"] and session.new or "oidc" not in session:
        session.invalidate()
        return aiohttp.web.Response(status=302, headers={"Location": "/"})

    session["at"] = time.time()

    session["referer"] = request.url.host
    uname = ""

    taint = True if setd["force_restricted_mode"] else False

    # Check token availability
    avail = await get_availability_from_token(token, client)
    csc_projects = session.get("csc-projects", None)
    session["projects"] = {}
    # Scope a token for all accessible projects
    for project in avail["projects"]:
        # Filter out projects without a declared access if the OIDC provider supports it
        project_without_prefix = project["name"].removeprefix("project_")
        if isinstance(csc_projects, list) and project_without_prefix not in csc_projects:
            request.app["Log"].debug(
                "Project %r is not enabled for sd-connect, skipping",
                project["name"],
            )
            continue
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
                session.invalidate()
                raise aiohttp.web.HTTPUnauthorized(reason="Token is not valid")
            if resp.status == 403:
                session.invalidate()
                raise aiohttp.web.HTTPForbidden(reason="No access to service with token.")
            ret = await resp.json()

            request.app["Log"].debug(f"token output: {ret}")

            obj_role = False
            request.app["Log"].debug(f'roles: {ret["token"]["roles"]}')
            for role in ret["token"]["roles"]:
                if role["name"] in str(setd["os_accepted_roles"]).split(";"):
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
                "tainted": True if setd["force_restricted_mode"] else False,
            }

    session["token"] = token
    session["uname"] = uname

    # the intersection of sdConnectProjects and Allas projects is empty
    # in practice this might happen if there are sd connect projects that
    # don't have Allas enabled
    if not session["projects"]:
        session.invalidate()
        request.app["Log"].debug("possible sdConnectProjects and Allas projects mismatch")
        raise aiohttp.web.HTTPForbidden(
            reason="There are no projects available for this user."
        )

    session["taint"] = True if taint else False

    session.changed()

    if taint:
        response.headers["Location"] = "/select"
        return response

    # Redirect to the browse page
    if "NAV_TO" in request.cookies.keys():
        response.headers["Location"] = request.cookies["NAV_TO"]
        response.del_cookie("NAV_TO")
    else:
        response.headers["Location"] = "/browse"

    return response


async def handle_project_lock(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Lock down to a specific project."""
    log = request.app["Log"]
    log.info("Call for locking down the project.")

    session = await aiohttp_session.get_session(request)

    project = request.match_info["project"]

    # Ditch all projects that aren't the one specified if project is defined
    if project in session["projects"]:
        session["projects"] = dict(
            filter(
                lambda val: val[0] == project,
                session["projects"].items(),
            )
        )
    # If the project doesn't exist, allow all untainted projects
    else:
        session["projects"] = dict(
            filter(lambda val: not val[1]["tainted"], session["projects"].items())
        )

    if not session["projects"]:
        session.invalidate()
        raise aiohttp.web.HTTPForbidden(reason="No untainted projects available.")

    # The session is no longer tainted if it's been locked
    session["taint"] = False

    session.changed()
    return aiohttp.web.Response(
        status=303,
        body=None,
        headers={
            "Location": "/browse",
        },
    )


async def handle_logout(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Properly kill the session for the user."""
    log = request.app["Log"]
    client = request.app["api_client"]
    if not setd["set_session_devmode"]:
        try:
            session = await aiohttp_session.get_session(request)
            log.info(f"Killing session {session.identity}")
            for project in session["projects"]:
                # the test client only supports `async with`
                async with client.delete(
                    f"{setd['auth_endpoint_url']}/auth/tokens",
                    headers={
                        "X-Auth-Token": session["token"],
                        "X-Subject-Token": session["projects"][project]["token"],
                    },
                ):
                    pass
            session.invalidate()
        except aiohttp.web.HTTPError:
            log.info("Trying to log out an invalidated session")
    response = aiohttp.web.Response(status=303)
    response.headers["Location"] = "/"
    return response


def _get_projects_from_userinfo(
    userinfo: typing.Dict[str, typing.Any],
) -> typing.List[typing.Any] | None:
    """Parse projects from userinfo.

    :param userinfo: dict from userinfo containing user profile
    :returns: None if userinfo doesn't contain csc-projects, or a list with "project_name"s
    :raises HTTPUnauthorized in case no projects are available
    """
    if "sdConnectProjects" in userinfo:
        # Remove the possibly existing "project_" prefix
        projects = [
            p.removeprefix("project_") for p in userinfo["sdConnectProjects"].split(" ")
        ]
    # we add this check in case the claim `sdConnectProjects does not exist`
    # and we want to enforce this at deployment
    elif setd["sdconnect_enabled"] and "sdConnectProjects" not in userinfo:
        projects = []
    else:
        return None

    if len(projects) == 0:
        # No project group information received, aborting
        raise aiohttp.web.HTTPUnauthorized(reason="User is not a member of any project.")

    return projects
