"""A module for handling the project login related tasks."""


import time
import hashlib
import json

# aiohttp
import aiohttp.web

from ._convenience import disable_cache, decrypt_cookie, generate_cookie
from ._convenience import get_availability_from_token, session_check
from ._convenience import initiate_os_session, initiate_os_service
from .settings import setd


async def handle_login(_):
    """Create new session cookie for the user."""
    response = aiohttp.web.Response(
        status=302,
        reason="Redirection to login"
    )

    response.headers['Location'] = "/login/front"

    return response


async def sso_query_begin(_):
    """Display login page and initiate federated keystone authentication."""
    # Return the form based login page if the service isn't trusted on the
    # endpoint
    if not setd['has_trust']:
        response = aiohttp.web.FileResponse(
            setd['static_directory'] + '/login.html'
        )
        return disable_cache(response)

    response = aiohttp.web.Response(
        status=302,
    )

    response.headers['Location'] = (
        setd['auth_endpoint_url'] +
        "/auth"
        "/OS-FEDERATION" +
        "/identity_providers" +
        "/haka" +
        "/protocols" +
        "/saml2" +
        "/websso" +
        "?origin={origin}".format(
            origin=setd['origin_address']
        )
    )

    return response


async def sso_query_end(request):
    """Handle the login procedure return from SSO or user from POST."""
    log = request.app['Log']
    # Declare the unscoped token
    unscoped = None
    formdata = await request.post()
    log.info(
        "Got %s in form.", formdata
    )
    if 'token' in formdata:
        unscoped = formdata['token']
        log.info(
            'Got OS token finvis ::{0}:: from address {1} :: {2}'.format(
                unscoped,
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
            reason="No Token ID was specified, token id is required"
        )

    # Now as we have a confirmation of having the token, we can establish
    # connection and begin the session
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

    response.set_cookie(
        name='S3BROW_SESSION',
        value=cookie_crypted,
        max_age=3600,
    )
    request.app['Sessions'].append(session)
    # Initiate the credential dictionary
    request.app['Creds'][session] = {}

    # Save the unscoped token to the session, as it may be needed for token
    # re-scoping?
    request.app['Creds'][session]['Token'] = unscoped

    # If the user didn't specify an existing project when logging in (in the
    # last active -header), check project availability with a list of domains,
    # save the information inside the app mapping.
    request.app['Creds'][session]['Avail'] =\
        get_availability_from_token(unscoped)

    # If we're using the non-WebSSO login, check token validity
    if (
            request.app['Creds'][session]['Avail'] == "INVALID" and
            not setd['has_trust']
    ):
        response = aiohttp.web.Response(
            status=302
        )
        response.headers['Location'] = "/login"
        response.set_cookie(
            name="INVALID_TOKEN",
            value="true",
            max_age=120,
        )
        return response

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
    response.set_cookie("LAST_ACTIVE", project_id, expires=2592000)

    # Redirect to the browse page with the correct credentials
    response.headers['Location'] = "/browse"

    return response


async def token_rescope(request):
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
        expires=2592000
    )

    return response


async def handle_logout(request):
    """Properly kill the session for the user."""
    if not setd['set_session_devmode']:
        try:
            log = request.app['Log']
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
