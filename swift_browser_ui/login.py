"""A module for handling the project login related tasks."""


import time
import hashlib
import json
import re

# aiohttp
import aiohttp.web
from multidict import MultiDictProxy

import typing
import urllib.error

from ._convenience import (
    disable_cache,
    decrypt_cookie,
    generate_cookie,
    get_availability_from_token,
    session_check,
    initiate_os_session,
    initiate_os_service,
    test_swift_endpoint,
    clear_session_info,
)
from .settings import setd


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
            f"Got OS token in formdata ::{str(unscoped)}:: "
            f"from address {request.remote} :: {time.ctime()}"
        )
    # Try getting the token id from form
    if "token" in request.query and unscoped is None:
        unscoped = request.query["token"]
        log.debug(
            f"Got OS token in query string ::{unscoped}:: "
            f"from address {request.remote} :: {time.ctime()}"
        )
    # Try getting the token id from headers
    if "X-Auth-Token" in request.headers and unscoped is None:
        unscoped = request.headers["X-Auth-Token"]
        log.debug(
            f"Got OS token in http header ::{unscoped}:: "
            f"from address {request.remote} :: {time.ctime()}"
        )
    if unscoped is None:
        raise aiohttp.web.HTTPClientError(reason="Token missing from query")
    if not (re.match("[a-f0-9]{32}", unscoped) and len(unscoped) == 32):
        raise aiohttp.web.HTTPClientError(reason="Token is malformed")

    log.info("Got OS token in login return")

    return unscoped


async def sso_query_end(
    request: aiohttp.web.Request,
) -> typing.Union[aiohttp.web.Response, aiohttp.web.FileResponse]:
    """Handle the login procedure return from SSO or user from POST."""
    log = request.app["Log"]
    response: typing.Union[aiohttp.web.Response, aiohttp.web.FileResponse]
    formdata = await request.post()
    log.debug(f"Got {formdata} in form.")
    # Declare the unscoped token
    unscoped = test_token(formdata, request)

    # Establish connection and begin session
    response = aiohttp.web.Response(status=303)
    cookie, _ = generate_cookie(request)

    cookie["referer"] = request.url.host
    cookie["signature"] = (
        hashlib.sha256(
            (cookie["id"] + cookie["referer"] + request.app["Salt"]).encode("utf-8")
        )
    ).hexdigest()
    session = cookie["id"]

    cookie_crypted = (
        request.app["Crypt"].encrypt(json.dumps(cookie).encode("utf-8")).decode("utf-8")
    )

    response = disable_cache(response)

    trust = bool(setd["has_trust"]) if "has_trust" in setd else False

    response.set_cookie(
        name="S3BROW_SESSION",
        value=cookie_crypted,
        max_age=str(setd["session_lifetime"]),
        secure=trust,  # type: ignore
        httponly=trust,  # type: ignore
    )
    # Initiate the session dictionary
    request.app["Sessions"][session] = {}

    # Save the unscoped token to the session, as it's needed for re-scoping
    request.app["Sessions"][session]["Token"] = unscoped

    try:
        # Check token availability
        request.app["Sessions"][session]["Avail"] = get_availability_from_token(unscoped)
    except urllib.error.HTTPError:
        raise aiohttp.web.HTTPUnauthorized(
            reason="Token no longer valid",
            headers={"WWW-Authenticate": 'Bearer realm="/", charset="UTF-8"'},
        )
    except urllib.error.URLError:
        raise aiohttp.web.HTTPUnauthorized(
            reason="Cannot fetch project and domains from existing endpoint.",
            headers={"WWW-Authenticate": 'Bearer realm="/", charset="UTF-8"'},
        )

    if "LAST_ACTIVE" in request.cookies:
        if request.cookies["LAST_ACTIVE"] not in [
            p["id"] for p in request.app["Sessions"][session]["Avail"]["projects"]
        ]:
            raise aiohttp.web.HTTPForbidden(
                reason="The project is not available for this token."
            )
        project_id = request.cookies["LAST_ACTIVE"]
    else:
        project_id = request.app["Sessions"][session]["Avail"]["projects"][0]["id"]

    # Open an OS session for the first project that's found for the user.
    request.app["Sessions"][session]["OS_sess"] = initiate_os_session(
        unscoped, project_id
    )

    test_swift_endpoint(
        request.app["Sessions"][session]["OS_sess"].get_endpoint(
            service_type="object-store"
        )
    )

    # Create the swiftclient connection
    request.app["Sessions"][session]["ST_conn"] = initiate_os_service(
        request.app["Sessions"][session]["OS_sess"],
    )

    project_name = None
    for i in request.app["Sessions"][session]["Avail"]["projects"]:
        if i["id"] == project_id:
            project_name = i["name"]
    # Save the current active project
    request.app["Sessions"][session]["active_project"] = {
        "name": project_name,
        "id": project_id,
    }

    # Save time of login to the backend
    created = time.time()
    request.app["Sessions"][session]["last_used"] = created
    request.app["Sessions"][session]["max_lifetime"] = created + int(
        setd["session_lifetime"]  # type: ignore
    )

    # Set the active project to be the last active project
    response.set_cookie(
        "LAST_ACTIVE",
        project_id,
        expires=str(setd["history_lifetime"]),  # type: ignore
        secure=trust,
        httponly=trust,
    )  # type: ignore

    # Redirect to the browse page
    if "NAV_TO" in request.cookies.keys():
        response.headers["Location"] = request.cookies["NAV_TO"]
        response.del_cookie("NAV_TO")
    else:
        response.headers["Location"] = "/browse"

    return response


async def token_rescope(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Rescope the requesting session's token to the new project."""
    session_check(request)
    session = decrypt_cookie(request)["id"]
    request.app["Log"].info(
        f"Call to rescope token from {request.remote}, sess: {session} :: {time.ctime()}"
    )

    if request.query["project"] not in [
        p["id"] for p in request.app["Sessions"][session]["Avail"]["projects"]
    ]:
        raise aiohttp.web.HTTPForbidden(
            reason="The project is not available for this token."
        )

    # Invalidate the old scoped token
    request.app["Sessions"][session]["OS_sess"].invalidate(
        request.app["Sessions"][session]["OS_sess"].auth
    )
    # Overwrite the old session with a new one, with the updated project id
    request.app["Sessions"][session]["OS_sess"] = initiate_os_session(
        request.app["Sessions"][session]["Token"],
        request.query["project"],
    )
    # Overwrite the old connection with a new one, with the updated keystone
    # session
    request.app["Sessions"][session]["ST_conn"] = initiate_os_service(
        request.app["Sessions"][session]["OS_sess"],
    )

    # Ditch the session download proxy if that exists
    if "runner" in request.app["Sessions"][session].keys():
        request.app["Sessions"][session].pop("runner")

    # Save the new project as the active project in session
    new_project_name = [
        i["name"]
        for i in request.app["Sessions"][session]["Avail"]["projects"]
        if i["id"] == request.query["project"]
    ][0]
    request.app["Sessions"][session]["active_project"] = {
        "name": new_project_name,
        "id": request.query["project"],
    }

    response = aiohttp.web.Response(status=303, reason="Successfully rescoped token.")
    response.headers["Location"] = "/browse"
    if "Referer" in request.headers:
        if len(request.headers["Referer"].split("/")) == 5:
            response.headers["Location"] = request.headers["Referer"]
    response.set_cookie(
        "LAST_ACTIVE",
        request.app["Sessions"][session]["active_project"]["id"],
        expires=str(setd["history_lifetime"]),  # type: ignore
    )

    return response


async def handle_logout(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Properly kill the session for the user."""
    session = ""
    log = request.app["Log"]
    if not setd["set_session_devmode"]:
        try:
            session = decrypt_cookie(request)["id"]
            log.info("Killing session for %s :: %s", session, time.ctime())
            clear_session_info(request.app["Sessions"])
            # Purge the openstack connection from the server
            request.app["Sessions"].pop(session)
            log.debug(f"Removed session {session} from session list :: {time.ctime()}")
        except aiohttp.web.HTTPUnauthorized:
            log.info("Trying to log out an invalidated session: {0}".format(session))
    response = aiohttp.web.Response(status=303)
    response.headers["Location"] = "/"
    return response
