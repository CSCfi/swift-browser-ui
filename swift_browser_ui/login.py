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

from ._convenience import disable_cache, decrypt_cookie, generate_cookie
from ._convenience import get_availability_from_token, session_check
from ._convenience import initiate_os_session, initiate_os_service
from ._convenience import test_swift_endpoint
from .settings import setd


async def handle_login(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Create new session cookie for the user."""
    response = aiohttp.web.Response(
        status=302,
        reason="Redirection to login"
    )

    # Add a cookie for navigating
    if "navto" in request.query.keys():
        response.set_cookie(
            "NAV_TO",
            request.query["navto"],
            expires=str(3600)
        )

    response.headers['Location'] = "/login/front"

    return response


async def sso_query_begin(
        _: typing.Union[aiohttp.web.Request, None]
) -> typing.Union[aiohttp.web.Response, aiohttp.web.FileResponse]:
    """Display login page and initiate federated keystone authentication."""
    # Return the form based login page if the service isn't trusted
    response: typing.Union[aiohttp.web.Response, aiohttp.web.FileResponse]
    if not setd['has_trust']:
        response = aiohttp.web.FileResponse(
            str(setd['static_directory']) + '/login.html'
        )
        return disable_cache(response)

    response = aiohttp.web.Response(
        status=302,
    )

    response.headers['Location'] = (
        str(setd['auth_endpoint_url']) +
        "/auth"
        "/OS-FEDERATION" +
        "/identity_providers" +
        "/haka" +
        "/protocols" +
        "/saml2" +
        "/websso" +
        "?origin={origin}".format(
            origin=setd['set_origin_address']
        )
    )

    return response


def test_token(
        formdata: MultiDictProxy[
            typing.Union[str, bytes, aiohttp.web.FileField]],
        request: aiohttp.web.Request
) -> str:
    """Validate unscoped token."""
    unscoped: typing.Union[str, None] = None
    log = request.app['Log']
    if 'token' in formdata:
        unscoped = str(formdata['token'])
        log.info(
            'Got OS token finvis ::{0}:: from address {1} :: {2}'.format(
                str(unscoped),
                request.remote,
                time.ctime()
            )
        )
    # Try getting the token id from form
    if 'token' in request.query and unscoped is None:
        unscoped = request.query['token']
        log.info(
            'Got OS token qstr ::{0}:: from address {1} :: {2}'.format(
                unscoped,
                request.remote,
                time.ctime()
            )
        )
    # Try getting the token id from headers
    if 'X-Auth-Token' in request.headers and unscoped is None:
        unscoped = request.headers['X-Auth-Token']
        log.info(
            'Got OS token hdr ::{0}:: from address {1} :: {2}'.format(
                unscoped,
                request.remote,
                time.ctime()
            )
        )
    if unscoped is None:
        raise aiohttp.web.HTTPClientError(
            reason="Token missing from query"
        )
    if not (
            re.match("[a-f0-9]{32}", unscoped) and
            len(unscoped) == 32
    ):
        raise aiohttp.web.HTTPClientError(
            reason="Token is malformed"
        )

    return unscoped


async def sso_query_end(
        request: aiohttp.web.Request
) -> typing.Union[aiohttp.web.Response, aiohttp.web.FileResponse]:
    """Handle the login procedure return from SSO or user from POST."""
    log = request.app['Log']
    response: typing.Union[aiohttp.web.Response, aiohttp.web.FileResponse]
    formdata = await request.post()
    log.info(
        "Got %s in form.", formdata
    )
    # Declare the unscoped token
    unscoped = test_token(formdata, request)

    # Establish connection and begin session
    response = aiohttp.web.Response(
        status=303
    )
    cookie, _ = generate_cookie(request)

    cookie["referer"] = request.url.host
    cookie["signature"] = (hashlib.sha256((cookie["id"] +
                                           cookie["referer"] +
                                           request.app["Salt"])
                                          .encode('utf-8'))).hexdigest()
    session = cookie["id"]

    cookie_crypted = \
        request.app['Crypt'].encrypt(
            json.dumps(cookie).encode('utf-8')
        ).decode('utf-8')

    response = disable_cache(response)

    trust = bool(setd['has_trust']) if 'has_trust' in setd else False

    response.set_cookie(
        name='S3BROW_SESSION',
        value=cookie_crypted,
        max_age=3600,
        secure=trust,  # type: ignore
        httponly=trust,  # type: ignore
    )
    request.app['Sessions'].add(session)
    # Initiate the credential dictionary
    request.app['Creds'][session] = {}

    # Save the unscoped token to the session, as it's needed for re-scoping
    request.app['Creds'][session]['Token'] = unscoped

    try:
        # Check token availability
        request.app['Creds'][session]['Avail'] =\
            get_availability_from_token(unscoped)
    except urllib.error.HTTPError:
        raise aiohttp.web.HTTPUnauthorized(
            reason="Token no longer valid"
        )
    except urllib.error.URLError:
        raise aiohttp.web.HTTPUnauthorized(
            reason="Cannot fetch project and domains from existing endpoint."
        )

    if "LAST_ACTIVE" in request.cookies:
        if (request.cookies["LAST_ACTIVE"] not in [
                p['id']
                for p in request.app['Creds'][session]['Avail']['projects']
        ]):
            raise aiohttp.web.HTTPForbidden(
                reason="The project is not available for this token."
            )
        project_id = request.cookies["LAST_ACTIVE"]
    else:
        project_id = \
            request.app['Creds'][session]['Avail']['projects'][0]['id']

    # Open an OS session for the first project that's found for the user.
    request.app['Creds'][session]['OS_sess'] = initiate_os_session(
        unscoped,
        project_id
    )

    test_swift_endpoint(
        request.app['Creds'][session]['OS_sess'].get_endpoint(
            service_type='object-store')
    )

    # Create the swiftclient connection
    request.app['Creds'][session]['ST_conn'] = initiate_os_service(
        request.app['Creds'][session]['OS_sess'],
    )

    project_name = None
    for i in request.app['Creds'][session]['Avail']['projects']:
        if i['id'] == project_id:
            project_name = i['name']
    # Save the current active project
    request.app['Creds'][session]['active_project'] = {
        "name": project_name,
        "id": project_id
    }

    # Set the active project to be the last active project
    response.set_cookie("LAST_ACTIVE", project_id,
                        expires=2592000,  # type: ignore
                        secure=trust, httponly=trust)  # type: ignore

    # Redirect to the browse page
    if "NAV_TO" in request.cookies.keys():
        response.headers['Location'] = request.cookies["NAV_TO"]
        response.del_cookie("NAV_TO")
    else:
        response.headers['Location'] = "/browse"

    return response


async def token_rescope(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Rescope the requesting session's token to the new project."""
    session_check(request)
    session = decrypt_cookie(request)["id"]
    request.app['Log'].info(
        "Call to rescope token from {0}, sess: {1} :: {2}".format(
            request.remote,
            session,
            time.ctime(),
        )
    )

    if (request.query['project'] not in [
            p['id'] for p in request.app['Creds'][session]['Avail']['projects']
    ]):
        raise aiohttp.web.HTTPForbidden(
            reason="The project is not available for this token."
        )

    # Invalidate the old scoped token
    request.app['Creds'][session]['OS_sess'].invalidate(
        request.app['Creds'][session]['OS_sess'].auth
    )
    # Overwrite the old session with a new one, with the updated project id
    request.app['Creds'][session]['OS_sess'] = initiate_os_session(
        request.app['Creds'][session]['Token'],
        request.query['project'],
    )
    # Overwrite the old connection with a new one, with the updated keystone
    # session
    request.app['Creds'][session]['ST_conn'] = initiate_os_service(
        request.app['Creds'][session]['OS_sess'],
    )

    # Ditch the session download proxy if that exists
    if 'runner' in request.app['Creds'][session].keys():
        request.app['Creds'][session].pop('runner')

    # Save the new project as the active project in session
    new_project_name = [
        i['name'] for i in request.app['Creds'][session]['Avail']['projects']
        if i['id'] == request.query['project']
    ][0]
    request.app['Creds'][session]['active_project'] = {
        "name": new_project_name,
        "id": request.query['project'],
    }

    response = aiohttp.web.Response(
        status=303,
        reason="Successfully rescoped token."
    )
    response.headers["Location"] = "/browse"
    if "Referer" in request.headers:
        if len(request.headers["Referer"].split("/")) == 5:
            response.headers["Location"] = request.headers["Referer"]
    response.set_cookie(
        "LAST_ACTIVE",
        request.app['Creds'][session]['active_project']['id'],
        expires=2592000  # type: ignore
    )

    return response


async def handle_logout(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Properly kill the session for the user."""
    cookie = ""
    log = request.app['Log']
    if not setd['set_session_devmode']:
        try:
            cookie = decrypt_cookie(request)["id"]
            log.info("Killing session for %s :: %s",
                     cookie, time.ctime())
            # Invalidate the tokens that are in use
            request.app['Creds'][cookie]['OS_sess'].invalidate(
                request.app['Creds'][cookie]['OS_sess'].auth
            )
            log.debug("Invalidated token for session %s :: %s",
                      cookie, time.ctime())
            # Purge everything related to the former openstack connection
            request.app['Creds'][cookie]['OS_sess'] = None
            request.app['Creds'][cookie]['ST_conn'] = None
            request.app['Creds'][cookie]['Avail'] = None
            request.app['Creds'][cookie]['Token'] = None
            request.app['Creds'][cookie]['active_project'] = None
            # Purge the openstack connection from the server
            request.app['Creds'].pop(cookie)
            log.debug("Purged connection information for %s :: %s",
                      cookie, time.ctime())
            # Purge the sessino from the session list
            request.app['Sessions'].remove(cookie)
            log.debug("Removed session %s from session list :: %s",
                      cookie, time.ctime())
        except aiohttp.web.HTTPUnauthorized:
            log.info(
                "Trying to log out an invalidated session: {0}".format(
                    cookie
                )
            )
    response = aiohttp.web.Response(
        status=303
    )
    response.headers["Location"] = "/"
    return response
