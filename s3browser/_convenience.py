# -*- coding: utf-8 -*-


from hashlib import sha256
from os import urandom
import aiohttp
import subprocess
import json

from keystoneauth1.identity import v3
import keystoneauth1.session

import openstack.connection


POUTA_URL = 'https://pouta.csc.fi:5001/v3'


async def disable_cache(response):
    """
    A convenience function for adding all required cache disabling headers
    for web responses, e.g. login window.
    """
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-Cache'
    response.headers['Expires'] = '0'
    return response


async def decrypt_cookie(request):
    """
    Decrypt a cookie using the server instance specific fernet key
    """
    return request.app['Crypt'].decrypt(
        request.cookies['S3BROW_SESSION'].encode('utf-8')
    ).decode('utf-8')


async def session_check(request):
    """
    Check session validity from a request
    """
    return await decrypt_cookie(request) in request.app['Sessions']


async def generate_cookie(request):
    """
    Generate an encrypted and unencrypted cookie, for use as a session cookie
    or API key.
    """
    cookie = sha256(urandom(1024)).hexdigest()
    return cookie, request.app['Crypt'].encrypt(
        cookie.encode('utf-8')
        ).decode('utf-8')


async def get_availability_from_token(token):
    """
    List available domains and projects for the unscoped token specified.

    Params:
        token: str
    Returns:
        Dictionary containing both the available projects and available domains
    Return type:
        dict(keys=('projects', 'domains'))
    """
    # Setup things common to every curl command required
    curl_argv = [
        'curl', '-s', '-X', 'GET', '-H', 'X-Auth-Token: ' + token,
    ]
    # Fetch required information from the API with curl
    output_projects = subprocess.check_output(
        curl_argv + ['https://pouta.csc.fi:5001/v3/OS-FEDERATION/projects']
    )
    output_domains = subprocess.check_output(
        curl_argv + ['https://pouta.csc.fi:5001/v3/OS-FEDERATION/domains']
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


async def initiate_os_session(auth_plugin):
    """
    Initiate new openstack session with the authentication plugin specified in
    the arguments
    """
    ret = keystoneauth1.session.Session(
        auth=auth_plugin,
        verify=False,
    )
    return ret


async def validate_cookie(unscoped, project):
    """
    Validate openstack unscoped token for specified project. Function creates
    an keystoneauth1 authentication plugin for the specific token and project.

    Params:
        request: object(aiohttp.web.Request)
    Returns:
        A usable authentication plugin
    Return type:
        object(keystoneauth1.identity.v3.Token)
    """
    ret = v3.Token(
        auth_url=POUTA_URL,
        token=unscoped,
        project_id=project,
    )
    return ret


async def initiate_os_connection(request):
    """
    Initiate an Opestack sdk connection with a cookie as an authentication
    method.
    """
    pass
