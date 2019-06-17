"""
A module for handling the project login sessions and requesting the necessary
tokens.
"""

# aiohttp
import aiohttp.web
# Openstack
import os
import time

from ._convenience import disable_cache, decrypt_cookie, generate_cookie
from ._convenience import get_availability_from_token, session_check
from ._convenience import initiate_os_session, initiate_os_service
from .settings import setd


async def handle_login(request):
    """
    Create new session cookie for the user.
    """
    # TODO: Change session cookie to HTTP only after separating cookies
    response = aiohttp.web.Response(
        status=303,
        reason="Redirection to login"
    )

    cookie, cookie_crypted = generate_cookie(request)
    response = disable_cache(response)

    response.set_cookie(
        name='S3BROW_SESSION',
        value=cookie_crypted,
        max_age=3600,
    )

    request.app['Sessions'].append(cookie)

    response.headers['Location'] = "/login/front"

    request.app['Log'].info(
        'Established new session for {0} - cookie:{1} - time:{2}'.format(
            request.remote,
            cookie,
            time.ctime()
        )
    )

    return response


async def sso_query_begin(request):
    """
    Display login page and initiate federated keystone authentication
    """
    session_check(request)
    # Return the form based login page if the service isn't trusted on the
    # endpoint
    if not setd['has_trust']:
        response = aiohttp.web.FileResponse(
            os.getcwd() + '/s3browser_frontend/login.html'
        )
        return disable_cache(response)

    response = aiohttp.web.Response(
        status=302,
    )

    response.headers['Location'] = (
        setd['auth_endpoint_url'] +
        "/OS-FEDERATION" +
        "/identity_providers" +
        "/haka" +
        "/protocols" +
        "/saml2" +
        "/auth" +
        "/websso" +
        "?origin={origin}".format(
            origin=setd['origin_address']
        )
    )

    return response


async def sso_query_end(request):
    """
    Function for handling login token POST, to fetch the scoped token
    from the keystone api.
    """
    # Check for established session
    session_check(request)
    session = decrypt_cookie(request)
    request.app['Log'].info(
        'Received SSO login from {0} with session {1} :: {2}'.format(
            request.remote,
            session,
            time.ctime()
        )
    )
    # Declare the unscoped token
    unscoped = None
    # Try getting the token id from form
    if 'token' in request.query:
        unscoped = request.query['token']
        request.app['Log'].info(
            'Got OS token ::{0}:: from address {1} :: {2}'.format(
                unscoped,
                request.remote,
                time.ctime()
            )
        )
    # Try getting the token id from headers
    if 'X-Auth-Token' in request.headers:
        unscoped = request.headers['X-Auth-Token']
        request.app['Log'].info(
            'Got OS token ::{0}:: from addres {1} :: {2}'.format(
                unscoped,
                request.remote,
                time.ctime()
            )
        )
    # Is there actually a token present?
    if unscoped is None:
        raise aiohttp.web.HTTPClientError(
            reason="No Token ID was specified, token id is required"
        )

    # Initiate the credential dictionary
    request.app['Creds'][session] = {}

    # Save the unscoped token to the session, as it may be needed for token
    # re-scoping?
    request.app['Creds'][session]['Token'] = unscoped

    # Check project availability with a list of domains, save the information
    # inside the app mapping
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

    # Open an OS session for the first project that's found for the user.
    request.app['Creds'][session]['OS_sess'] = initiate_os_session(
        unscoped,
        request.app['Creds'][session]['Avail']['projects'][0]
    )

    # Create the swiftclient connection
    request.app['Creds'][session]['ST_conn'] = initiate_os_service(
        request.app['Creds'][session]['OS_sess'],
        request.app['Creds'][session]['Avail']['projects'][0],
    )

    # Log information from the connection to make sure that the connetion was
    # actually established
    request.app['Log'].info(
        'The following was gotten as reponse to the new session for ' +
        '{0}, session: {1} :: {2}\n'.format(
            request.remote,
            session,
            time.ctime(),
        ) + str(request.app['Creds'][session]['ST_conn'].stat())
    )

    # Redirect to the browse page with the correct credentials
    response = aiohttp.web.Response(
        status=302,
        reason="Start application"
    )
    response.headers['Location'] = "/browse"

    return response


async def token_rescope(request):
    """
    Rescope the requesting session's token to the new specified project
    """
    session_check(request)
    session = decrypt_cookie(request)
    request.app['Log'].info(
        "Call to rescope token from {0}, sess: {1} :: {2}".format(
            request.remote,
            session,
            time.ctime(),
        )
    )

    if (request.query['project'] not in
            request.app['Creds'][session]['Avail']['projects']):
        raise aiohttp.web.HTTPForbidden(
            reason="The project is not available for this token."
        )

    # Invalidate the old scoped token
    request.app['Creds'][session]['OS_sess'].invalidate()
    # Overwrite the old session with a new one, with the updated project id
    request.app['Creds'][session]['OS_sess'] = initiate_os_session(
        request.app['Creds'][session]['Token'],
        request.query['project'],
    )
    # Overwrite the old connection with a new one, with the updated keystone
    # session
    request.app['Creds'][session]['ST_conn'] = initiate_os_service(
        request.app['Creds'][session]['OS_sess'],
        request.query['project'],
    )

    return aiohttp.web.Response(
        status=204,
        reason="Successfully rescoped token."
    )


async def handle_logout(request):
    if session_check(request):
        cookie = decrypt_cookie(request)
        request.app['Creds'][cookie]['OS_sess'].invalidate()
        request.app['Sessions'].remove(cookie)
    return aiohttp.web.Response(
        status=204
    )
