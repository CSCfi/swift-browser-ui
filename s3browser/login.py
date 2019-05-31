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
    if session_check(request):
        response = aiohttp.web.FileResponse(
            os.getcwd() + '/s3browser_frontend/login.html'
        )
        return disable_cache(response)
    else:
        response = aiohttp.web.Response(
            status=401,
            reason="Invalid or no session cookie"
        )
        return response


async def sso_query_end(request):
    """
    Function for handling login token POST, to fetch the scoped token
    from the keystone api.
    """
    # Check for established session
    if session_check(request):
        session = decrypt_cookie(request)
        request.app['Log'].info(
            'Received SSO login from {0} with session {1} :: {2}'.format(
                request.remote,
                session,
                time.ctime()
            )
        )
    else:
        return aiohttp.web.Response(
            status=401,
            reason="Invalid or no session cookie"
        )
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
    else:
        response = aiohttp.web.Response(
            status=400,
            reason="No Token ID was specified, token id is required"
        )
        return response

    # Initiate the credential dictionary
    request.app['Creds'][session] = {}

    # Save the unscoped token to the session, as it may be needed for token
    # re-scoping?
    request.app['Creds'][session]['Token'] = unscoped

    # Check project availability with a list of domains, save the information
    # inside the app mapping
    request.app['Creds'][session]['Avail'] =\
        get_availability_from_token(unscoped)

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


async def handle_logout(request):
    if session_check(request):
        cookie = decrypt_cookie(request)
        request.app['Creds'][cookie]['OS_sess'].invalidate
        request.app['Sessions'].remove(cookie)
    return aiohttp.web.Response(
        status=204
    )
