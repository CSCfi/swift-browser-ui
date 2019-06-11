"""
Miscellaneous convenience functions for authenticating against openstack v3
identity API, cache manipulation, cookies and such. Also the necessary
project constants will be kept here, e.g. the authentication endpoint
URL.
"""


from hashlib import sha256
from os import urandom
import subprocess
import json
import logging
import aiohttp.web

from keystoneauth1.identity import v3
import keystoneauth1.session

import swiftclient.service
import swiftclient.client

from cryptography.fernet import InvalidToken

POUTA_URL = 'https://pouta.csc.fi:5001/v3'
SWIFT_URL_PREFIX = 'https://object.pouta.csc.fi:443/swift/v1'


keystonelog = logging.getLogger('keystoneauth')
keystonelog.addHandler(logging.StreamHandler())
keystonelog.setLevel(logging.DEBUG)


def disable_cache(response):
    """
    A convenience function for adding all required cache disabling headers
    for web responses, e.g. login window.
    """
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-Cache'
    response.headers['Expires'] = '0'
    return response


def decrypt_cookie(request):
    """
    Decrypt a cookie using the server instance specific fernet key
    """
    return request.app['Crypt'].decrypt(
        request.cookies['S3BROW_SESSION'].encode('utf-8')
    ).decode('utf-8')


def session_check(request):
    """
    Check session validity from a request
    """
    try:
        if decrypt_cookie(request) in request.app['Sessions']:
            return True
        else:
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
    Separate session check for API

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
    Generate an encrypted and unencrypted cookie, for use as a session cookie
    or API key.
    """
    cookie = sha256(urandom(1024)).hexdigest()
    return cookie, request.app['Crypt'].encrypt(
        cookie.encode('utf-8')
        ).decode('utf-8')


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
    # Setup things common to every curl command required
    curl_argv = [
        'curl', '-s', '-X', 'GET', '-H', 'X-Auth-Token: ' + token,
    ]
    # Fetch required information from the API with curl
    output_projects = subprocess.check_output(
        curl_argv + ['https://pouta.csc.fi:5001/v3/OS-FEDERATION/projects'],
        shell=False,
    )
    output_domains = subprocess.check_output(
        curl_argv + ['https://pouta.csc.fi:5001/v3/OS-FEDERATION/domains'],
        shell=False,
    )
    # Decode and serialize said output to a usable format
    output_projects = json.loads(output_projects.decode('utf-8'))
    output_domains = json.loads(output_domains.decode('utf-8'))
    # For now print debug information
    print('--PROJECT AND DOMAIN INFORMATION FROM KEYSTONE--')
    print(output_projects)
    print(output_domains)
    print('--END INFORMATION--')
    # Return all project names and domain names inside a dictionary
    return {
        "projects": [
            p['id'] for p in output_projects['projects']
        ],
        "domains": [
            d['name'] for d in output_domains['domains']
        ]
    }


# The Openstack SDK functions will be moved to the login.py module, but will
# be contained here for testing.
def initiate_os_session(unscoped, project):
    """
    Initiate new openstack session with the unscoped token and the specified
    project id

    Params:
        unscoped: str
        project: str
    Returns:
        A usable keystone session object for OS client connections
    Return type:
        object(keystoneauth1.session.Session)
    """
    os_auth = v3.Token(
        auth_url=POUTA_URL,
        token=unscoped,
        project_id=project
    )

    return keystoneauth1.session.Session(
        auth=os_auth,
        verify=False,
    )


def initiate_os_service(os_session, project):
    """
    Initiate an Opestack sdk connection with a session as an authentication
    method. Also add the object storage service.

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
        'os_storage_url': SWIFT_URL_PREFIX + '/AUTH_' + project,
        'os_auth_url': POUTA_URL,
        'insecure': True,
        'debug': True,
        'info': True,
    }

    os_sc = swiftclient.service.SwiftService(
        options=sc_new_options
    )

    return os_sc
