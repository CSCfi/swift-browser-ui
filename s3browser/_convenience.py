"""
Miscallaneous convenience functions used during the project.

Module contains funcions for e.g. authenticating agains openstack v3 identity
API, cache manipulation, cookies etc.
"""


from hashlib import sha256
from os import urandom
import json
import logging
import re
import urllib.request


import aiohttp.web

from keystoneauth1.identity import v3
import keystoneauth1.session
from cryptography.fernet import InvalidToken

import swiftclient.service
import swiftclient.client


from .settings import setd


def setup_logging():
    """
    Set up logging for the keystoneauth module.

    The keystoneauth module requires more set-up for logging, since its logger
    doesn't update when the root logger is manipulated for some reason.
    """
    keystonelog = logging.getLogger('keystoneauth')
    keystonelog.addHandler(logging.StreamHandler())
    if setd['debug']:
        keystonelog.setLevel(logging.DEBUG)
    elif setd['verbose']:
        keystonelog.setLevel(logging.INFO)
    else:
        keystonelog.setLevel(logging.WARNING)


def disable_cache(response):
    """Add cache disabling headers to an aiohttp response."""
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-Cache'
    response.headers['Expires'] = '0'
    return response


def decrypt_cookie(request):
    """Decrypt a cookie using the server instance specific fernet key."""
    return request.app['Crypt'].decrypt(
        request.cookies['S3BROW_SESSION'].encode('utf-8')
    ).decode('utf-8')


def session_check(request):
    """Check session validity from a request."""
    try:
        if decrypt_cookie(request) in request.app['Sessions']:
            return True
        raise aiohttp.web.HTTPUnauthorized(
            headers={
                "WWW-Authenticate": 'Bearer realm="/", charset="UTF-8"'
            }
        )
    except InvalidToken:
        raise aiohttp.web.HTTPUnauthorized(
            headers={
                "WWW-Authenticate": 'Bearer realm="/", charset="UTF-8"'
            }
        )
    except KeyError:
        raise aiohttp.web.HTTPUnauthorized(
            headers={
                "WWW-Authenticate": 'Bearer realm="/", charset="UTF-8"'
            }
        )


def api_check(request):
    """
    Do a session check for the API.

    The API requires a more comprehensive check for session validity, since
    there is the possibility of the openstack connection not being valid,
    despite the session existing.
    Params:
        request: object(aiohttp.web.Request)
    Returns:
        The correct check failure response, the session cookie otherwise
    Return type:
        object(aiohttp.web.Response) or str

    """
    try:
        if decrypt_cookie(request) in request.app['Sessions']:
            session = decrypt_cookie(request)
            ret = session
            if 'ST_conn' not in request.app['Creds'][session].keys():
                raise aiohttp.web.HTTPUnauthorized(
                    headers={
                        "WWW-Authenticate": 'Bearer realm="/", charset="UTF-8"'
                    }
                )
            if 'OS_sess' not in request.app['Creds'][session].keys():
                raise aiohttp.web.HTTPUnauthorized(
                    headers={
                        "WWW-Authenticate": 'Bearer realm="/", charset="UTF-8"'
                    }
                )
            if 'Avail' not in request.app['Creds'][session].keys():
                raise aiohttp.web.HTTPUnauthorized(
                    headers={
                        "WWW-Authenticate": 'Bearer realm="/", charset="UTF-8"'
                    }
                )
        else:
            raise aiohttp.web.HTTPUnauthorized(
                headers={
                    "WWW-Authenticate": 'Bearer realm="/", charset="UTF-8"'
                }
            )
        return ret
    except InvalidToken:
        raise aiohttp.web.HTTPUnauthorized(
            headers={
                "WWW-Authenticate": 'Bearer realm="/", charset="UTF-8"'
            }
        )


def generate_cookie(request):
    """
    Generate an encrypted and unencrypted cookie.

    Returns a tuple containing both the unencrypted and encrypted cookie.
    """
    cookie = sha256(urandom(1024)).hexdigest()
    return cookie, request.app['Crypt'].encrypt(
        cookie.encode('utf-8')).decode('utf-8')


def get_availability_from_token(token):
    """
    List available domains and projects for the unscoped token specified.

    Params:
        token: str
    Returns:
        Dictionary containing both the available projects and available domains
    Return type:
        dict(keys=('projects': List(str), 'domains': List(str)))
    """
    # Check that the token is an actual token
    if not re.match("^[a-f0-9]*$", token):
        return "INVALID"

    # setup token header
    hdr = {
        "X-Auth-Token": token,
    }

    # Check projects from the API
    prq = urllib.request.Request(
        setd['auth_endpoint_url'] + "/OS-FEDERATION/projects",
        headers=hdr,
    )
    with urllib.request.urlopen(prq) as projects:  # nosec
        output_projects = json.loads(projects.read().decode('utf-8'))

    # Check domains from the API
    drq = urllib.request.Request(
        setd['auth_endpoint_url'] + "/OS-FEDERATION/domains",
        headers=hdr,
    )
    with urllib.request.urlopen(drq) as domains:  # nosec
        output_domains = json.loads(domains.read().decode('utf-8'))

    logging.info("%s\n%s\n%s\n%s",
                 '--PROJECT AND DOMAIN INFORMATION FROM KEYSTONE--',
                 str(output_projects),
                 str(output_domains),
                 '--END INFORMATION--')

    # Return all project names and domain names inside a dictionary
    return {
        "projects": [
            p for p in output_projects['projects']
        ],
        "domains": [
            d for d in output_domains['domains']
        ]
    }


# The Openstack SDK functions will be moved to the login.py module, but will
# be contained here for testing.
def initiate_os_session(unscoped, project):
    """
    Create a new openstack session with the unscoped token and project id.

    Params:
        unscoped: str
        project: str
    Returns:
        A usable keystone session object for OS client connections
    Return type:
        object(keystoneauth1.session.Session)
    """
    os_auth = v3.Token(
        auth_url=setd['auth_endpoint_url'],
        token=unscoped,
        project_id=project
    )

    return keystoneauth1.session.Session(
        auth=os_auth,
        verify=False,
    )


def initiate_os_service(os_session, project):
    """
    Create a swiftclient SwiftService connection to object storage.

    Params:
        os_session: object(keystoneauth1.session.Session)
    Returns:
        A connection object to Openstack Object store service
    Return type:
        object(swiftclient.service.SwiftService)

    """
    # Set up new options for the swift service, since the defaults won't do
    sc_new_options = {
        'os_auth_token': os_session.get_token(),
        'os_storage_url': (setd['swift_endpoint_url'] +
                           '/v1' + '/AUTH_' + project),
        'os_auth_url': setd['auth_endpoint_url'],
        'debug': True,
        'info': True,
    }

    os_sc = swiftclient.service.SwiftService(
        options=sc_new_options
    )

    return os_sc
