"""
Miscallaneous convenience functions used during the project.

Module contains funcions for e.g. authenticating against openstack v3 identity
API, cache manipulation, cookies etc.
"""


import secrets
from hashlib import sha256
import json
import logging
import urllib.request
import requests
import typing
import time

import aiohttp
import aiohttp.web

from keystoneauth1.identity import v3
import keystoneauth1.session
from cryptography.fernet import InvalidToken

import swiftclient.service
import swiftclient.client

import swift_browser_ui.common.signature

from swift_browser_ui.ui.settings import setd

import ssl
import certifi


ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())


def test_swift_endpoint(endpoint: str) -> None:
    """Test swift endpoint connectivity."""
    try:
        requests.head(endpoint)
    except requests.exceptions.ConnectionError as e:
        logging.debug(f"The {endpoint} couldn't fulfill the request.")
        logging.debug(f"Error code: {e}")
        raise aiohttp.web.HTTPServiceUnavailable(
            reason="Cannot get Swift endpoint connection."
        )
    else:
        logging.info("Swift endpoint accessible.")


async def sign(
    valid_for: int,
    path: str,
) -> dict:
    """Perform a general signature."""
    try:
        key = str(setd["sharing_request_token"]).encode("utf-8")
    except (KeyError, AttributeError):
        raise aiohttp.web.HTTPNotImplemented(
            reason="Server doesn't have signing permissions."
        )

    return swift_browser_ui.common.signature.sign_api_request(
        path, valid_for=valid_for, key=key
    )


def setup_logging() -> None:
    """
    Set up logging for the keystoneauth module.

    The keystoneauth module requires more set-up for logging, since its logger
    doesn't update when the root logger is manipulated for some reason.
    """
    keystonelog = logging.getLogger("keystoneauth")
    keystonelog.addHandler(logging.StreamHandler())
    if setd["debug"]:
        keystonelog.setLevel(logging.DEBUG)
    elif setd["verbose"]:
        keystonelog.setLevel(logging.INFO)
    else:
        keystonelog.setLevel(logging.WARNING)


def disable_cache(
    response: typing.Union[aiohttp.web.Response, aiohttp.web.FileResponse]
) -> typing.Union[aiohttp.web.Response, aiohttp.web.FileResponse]:
    """Add cache disabling headers to an aiohttp response."""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-Cache"
    response.headers["Expires"] = "0"
    return response


def clear_session_info(session: typing.Dict[str, typing.Any]):
    """Properly clear session information."""
    if "OS_sess" in session:
        # invalidate used tokens
        session["OS_sess"].invalidate(session["OS_sess"].auth)
        session["OS_sess"] = None
        # ensure deletion of references to connection info
    if "ST_conn" in session:
        session["ST_conn"] = None
    if "Avail" in session:
        session["Avail"] = None
    if "Token" in session:
        session["Token"] = None
    if "active_project" in session:
        session["active_project"] = None


def decrypt_cookie(request: aiohttp.web.Request) -> dict:
    """Decrypt a cookie using the server instance specific fernet key."""
    if "S3BROW_SESSION" not in request.cookies:
        raise aiohttp.web.HTTPUnauthorized(
            headers={"WWW-Authenticate": 'Bearer realm="/", charset="UTF-8"'}
        )
    try:
        cookie_json = (
            request.app["Crypt"]
            .decrypt(request.cookies["S3BROW_SESSION"].encode("utf-8"))
            .decode("utf-8")
        )
        cookie = json.loads(cookie_json)
        request.app["Log"].debug(f"Decrypted cookie: {cookie}")
        return cookie
    except InvalidToken:
        request.app["Log"].info("Throw due to invalid token.")
        raise aiohttp.web.HTTPUnauthorized(
            headers={"WWW-Authenticate": 'Bearer realm="/", charset="UTF-8"'}
        )


def check_csrf(request: aiohttp.web.Request) -> bool:
    """Check that the signature matches and referrer is correct."""
    cookie = decrypt_cookie(request)
    # Throw if the cookie originates from incorrect referer (meaning the
    # site's wrong)
    if "Referer" in request.headers.keys():
        # Pass referer check if we're returning from the login.
        if request.headers["Referer"] in str(setd["auth_endpoint_url"]):
            request.app["Log"].info(
                "Skipping Referer check due to request coming from OS."
            )
            return True
        if cookie["referer"] not in request.headers["Referer"]:
            request.app["Log"].info(
                f"Throw due to invalid referer: {request.headers['Referer']}"
            )
            raise aiohttp.web.HTTPForbidden()
    else:
        request.app["Log"].debug(
            "Skipping referral validation due to missing Referer-header."
        )
    # Throw if the cookie signature doesn't match (meaning the referer might
    # have been changed without setting the signature)
    if not secrets.compare_digest(
        sha256(
            (cookie["id"] + cookie["referer"] + request.app["Salt"]).encode("utf-8")
        ).hexdigest(),
        cookie["signature"],
    ):
        request.app["Log"].info(
            f"Throw due to invalid referer: {request.headers['Referer']}"
        )
        raise aiohttp.web.HTTPForbidden()
    # If all is well, return True.
    return True


def session_check(request: aiohttp.web.Request) -> None:
    """Check session validity from a request."""
    try:
        session = decrypt_cookie(request)["id"]
        # Keyerror takes care of checking session id's existence
        try:
            last_used = request.app["Sessions"][session]["last_used"]
            max_lifetime = request.app["Sessions"][session]["max_lifetime"]
        except KeyError:
            request.app["Log"].info("Throw due to nonexistent session")
            raise aiohttp.web.HTTPUnauthorized(
                headers={"WWW-Authenticate": 'Bearer realm="/", charset="UTF-8"'}
            )
        check_csrf(request)
        # Check token expiration
        current_time = time.time()
        if last_used + 3600 < current_time or max_lifetime < current_time:
            request.app["Log"].info("Throw due to expired token")
            clear_session_info(request.app["Sessions"][session])
            request.app["Sessions"].pop(session)
            raise aiohttp.web.HTTPUnauthorized(
                headers={"WWW-Authenticate": 'Bearer realm="/", charset="UTF-8"'}
            )
        # Update token last usage
        request.app["Sessions"][session]["last_used"] = current_time
    except InvalidToken:
        request.app["Log"].info("Throw due to invalid token.")
        raise aiohttp.web.HTTPUnauthorized(
            headers={"WWW-Authenticate": 'Bearer realm="/", charset="UTF-8"'}
        )
    except KeyError:
        request.app["Log"].info("Throw due to nonexistent token.")
        raise aiohttp.web.HTTPUnauthorized(
            headers={"WWW-Authenticate": 'Bearer realm="/", charset="UTF-8"'}
        )


def api_check(request: aiohttp.web.Request) -> str:
    """Do a more thorough session check for the API."""
    session_check(request)
    check_csrf(request)
    session = decrypt_cookie(request)["id"]
    if (
        "ST_conn" not in request.app["Sessions"][session]
        or "OS_sess" not in request.app["Sessions"][session]
        or "Avail" not in request.app["Sessions"][session]
    ):
        raise aiohttp.web.HTTPUnauthorized(
            headers={"WWW-Authenticate": 'Bearer realm="/", charset="UTF-8"'}
        )
    return session


def generate_cookie(request: aiohttp.web.Request) -> typing.Tuple[dict, str]:
    """
    Generate an encrypted and unencrypted cookie.

    Returns a tuple containing both the unencrypted and encrypted cookie.
    """
    cookie = {
        "id": secrets.token_urlsafe(32),
        "referer": None,
        "signature": None,
    }
    # Return a tuple of the session as an encrypted JSON string, and the
    # cookie itself
    return (
        cookie,
        request.app["Crypt"].encrypt(json.dumps(cookie).encode("utf-8")).decode("utf-8"),
    )


def get_availability_from_token(token: str) -> dict:
    """
    List available domains and projects for the unscoped token specified.

    Params:
        token: str
    Returns:
        Dictionary containing both the available projects and available domains
    Return type:
        dict(keys=('projects': List(str), 'domains': List(str)))
    """
    # setup token header
    hdr = {
        "X-Auth-Token": token,
    }

    # Check projects from the API
    prq = urllib.request.Request(
        str(setd["auth_endpoint_url"]) + "/OS-FEDERATION/projects",
        headers=hdr,
    )
    with urllib.request.urlopen(prq, timeout=20) as projects:  # nosec
        output_projects = json.loads(projects.read().decode("utf-8"))

    # Check domains from the API
    drq = urllib.request.Request(
        str(setd["auth_endpoint_url"]) + "/OS-FEDERATION/domains",
        headers=hdr,
    )
    with urllib.request.urlopen(drq, timeout=20) as domains:  # nosec
        output_domains = json.loads(domains.read().decode("utf-8"))

    logging.info(f"{str(output_projects)}\n{str(output_domains)}")

    # we need to take the projects that have been enabled for the
    # user, otherwise if the first project is disabled we will
    # get a 401 response when we do initiate_os_service
    filtered = list(
        filter(lambda d: d.get("enabled") is not False, output_projects["projects"])
    )

    if len(filtered) == 0:
        raise aiohttp.web.HTTPForbidden(
            reason="Thre is no project available for this user."
        )

    # Return all project names and domain names inside a dictionary
    return {
        "projects": [p for p in filtered],
        "domains": [d for d in output_domains["domains"]],
    }


# The Openstack SDK functions will be moved to the login.py module, but will
# be contained here for testing.
def initiate_os_session(unscoped: str, project: str) -> keystoneauth1.session.Session:
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
        auth_url=setd["auth_endpoint_url"], token=unscoped, project_id=project
    )

    return keystoneauth1.session.Session(
        auth=os_auth,
        verify=True,
    )


def os_get_token_from_credentials(
    username: str,
    password: str,
) -> str:
    """Get an unscoped token with provided credentials."""
    os_auth = v3.Password(
        setd["auth_endpoint_url"],
        username=username,
        password=password,
        user_domain_name=setd["os_user_domain"],
        unscoped=True,
    )

    os_session = keystoneauth1.session.Session(
        auth=os_auth,
        verify=True,
    )

    return os_session.get_token()


def initiate_os_service(
    os_session: keystoneauth1.session.Session, url: str = None
) -> swiftclient.service.SwiftService:
    """Create a SwiftService connection to object storage."""
    try:
        # Set up new options for the swift service, since the defaults won't do
        sc_new_options = {
            "os_auth_token": os_session.get_token(),
            "os_storage_url": os_session.get_endpoint(service_type="object-store"),
            "os_auth_url": setd["auth_endpoint_url"],
            "debug": True,
            "info": True,
        }

        if url:
            sc_new_options["os_storage_url"] = url

        os_sc = swiftclient.service.SwiftService(options=sc_new_options)

        return os_sc
    except Exception as e:
        logging.info(f"Throw due to keystoneAPI issue {e}.")
        raise aiohttp.web.HTTPUnauthorized(
            headers={"WWW-Authenticate": 'Bearer realm="/", charset="UTF-8"'}
        )


async def get_tempurl_key(connection: swiftclient.service.SwiftService) -> str:
    """Get the correct temp URL key from Openstack."""
    stats = connection.stat()
    acc_meta_hdr = dict()
    # Check for the existence of the key headers
    try:
        acc_meta_hdr = stats["headers"]
        temp_url_key = acc_meta_hdr["x-account-meta-temp-url-key"]
    except KeyError:
        try:
            temp_url_key = acc_meta_hdr["x-account-meta-temp-url-key-2"]
        # If key headers don't exist, generate a new temporary URL key
        except KeyError:
            temp_url_key = secrets.token_urlsafe(32)
            meta_options = {"meta": [f"Temp-URL-Key-2:{temp_url_key}"]}
            retval = connection.post(options=meta_options)
            if not retval["success"]:
                raise aiohttp.web.HTTPServerError()
    return temp_url_key


async def get_container_tempurl_key(
    connection: swiftclient.service.SwiftService,
    container: str,
) -> str:
    """Get the correct temp URL key for container operations."""
    stats = connection.stat(container=container)
    cont_meta_hdr = dict()
    # Check for the existence of the key headers
    try:
        cont_meta_hdr = stats["headers"]
        temp_cont_key = cont_meta_hdr["x-container-meta-temp-url-key"]
    except KeyError:
        try:
            temp_cont_key = cont_meta_hdr["x-container-meta-temp-url-key-2"]
        # If key headers don't exist generate a new temporary URL key
        except KeyError:
            temp_cont_key = secrets.token_urlsafe(32)
            meta_options = {"meta": [f"Temp-URL-Key-2:{temp_cont_key}"]}
            retval = connection.post(container=container, options=meta_options)
            if not retval["success"]:
                raise aiohttp.web.HTTPServerError()
    return temp_cont_key


async def open_upload_runner_session(
    session_key: str, request: aiohttp.web.Request, project: str, token: str
) -> str:
    """Open an upload session to the token."""
    try:
        return request.app["Sessions"][session_key]["runner"]
    except KeyError:
        session = request.app["api_client"]
        path = f"{setd['upload_internal_endpoint']}/{project}"
        signature = await sign(3600, f"/{project}")
        async with session.post(
            path,
            data={"token": token},
            params={
                "signature": signature["signature"],
                "valid": signature["valid"],
            },
            ssl=ssl_context,
        ) as resp:
            ret = str(resp.cookies["RUNNER_SESSION_ID"].value)
            request.app["Sessions"][session_key]["runner"] = ret
            return ret
