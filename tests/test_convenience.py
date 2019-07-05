"""
Module for testing s3browser._convenience
"""


import pytest
from aiohttp.web import HTTPUnauthorized, Response
import cryptography.fernet
import hashlib
import os
from swiftclient.service import SwiftService
from keystoneauth1.session import Session


from .creation import get_request_with_fernet
from .mockups import mock_token_output, urlopen
from s3browser._convenience import api_check, generate_cookie
from s3browser._convenience import disable_cache, decrypt_cookie
from s3browser._convenience import session_check, setup_logging
from s3browser._convenience import get_availability_from_token
from s3browser._convenience import initiate_os_service, initiate_os_session
from s3browser.settings import setd


def test_setup_logging():
    """Test that the logging setup function works."""
    setup_logging()
    setd['verbose'] = True
    setup_logging()
    setd['debug'] = True
    setup_logging()


def test_disable_cache():
    """Test that the disable_cache function correctly disables cache."""
    response = Response(
        status=200,
        body=b'OK'
    )
    response = disable_cache(response)
    assert response.headers['Cache-Control'] == (  # nosec
        "no-cache, no-store, must-revalidate"
    )
    assert response.headers['Pragma'] == 'no-Cache'  # nosec
    assert response.headers['Expires'] == '0'  # nosec


def test_generate_cookie():
    """Test that the cookie generation works."""
    testreq = get_request_with_fernet()
    assert generate_cookie(testreq) is not None  # nosec


def test_decrypt_cookie():
    """Test that the cookie decrypt function works."""
    testreq = get_request_with_fernet()
    # Generate cookie is tested separately, it can be used for testing the
    # rest of the functions without mockups
    c, testreq.cookies['S3BROW_SESSION'] = generate_cookie(testreq)
    assert c == decrypt_cookie(testreq)  # nosec


def test_session_check_nocookie():
    """Test session check raise 401 on non-existing cookie"""
    req = get_request_with_fernet()
    with pytest.raises(HTTPUnauthorized):
        session_check(req)


def test_session_check_invtoken():
    """Test session check raise 401 on a stale cookie."""
    req = get_request_with_fernet()
    _, req.cookies['S3BROW_SESSION'] = generate_cookie(req)
    req.app['Crypt'] = cryptography.fernet.Fernet(
        cryptography.fernet.Fernet.generate_key()
    )
    with pytest.raises(HTTPUnauthorized):
        session_check(req)


def test_session_check_nosession():
    """
    Test session check function raise 401 on invalid session cookie.
    (i.e. it cannot be found in the open session list)
    """
    req = get_request_with_fernet()
    _, req.cookies['S3BROW_SESSION'] = generate_cookie(req)
    req.app['Sessions'] = []
    with pytest.raises(HTTPUnauthorized):
        session_check(req)


def test_session_check_correct():
    """
    Test that the ordinary session check function result is True.
    Test condition when the request is formed correctly.
    """
    req = get_request_with_fernet()
    c, req.cookies['S3BROW_SESSION'] = generate_cookie(req)
    req.app['Sessions'].append(c)
    assert session_check(req) is True  # nosec


# The api_check session check function testing – Might seem unnecessary, but
# are required since e.g. token rescoping can fail the sessions before the
# next API call, also might try to use the API while rescoping -> 401
def test_api_check_raise_on_no_cookie():
    """Test raise if there's no session cookie."""
    testreq = get_request_with_fernet()
    _, testreq.cookies['S3BROW_SESSION'] = generate_cookie(testreq)
    testreq.app['Sessions'] = []
    with pytest.raises(HTTPUnauthorized):
        api_check(testreq)


def test_api_check_raise_on_invalid_cookie():
    """Test raise if there's an invalid session cookie."""
    testreq = get_request_with_fernet()
    _, testreq.cookies['S3BROW_SESSION'] = generate_cookie(testreq)
    testreq.app['Sessions'] = []
    with pytest.raises(HTTPUnauthorized):
        api_check(testreq)


# NOTE: The order of operations for these tests is significant (i.e. there is
# a reason some of the placeholders are missing in the test functions, to
# enable testing correct raising order in the same time)
def test_api_check_raise_on_no_connection():
    """Test raise if there's no existing OS connection during an API call."""
    testreq = get_request_with_fernet()
    cookie, testreq.cookies['S3BROW_SESSION'] = generate_cookie(testreq)
    testreq.app['Sessions'] = [cookie]
    testreq.app['Creds'][cookie] = {}
    testreq.app['Creds'][cookie]['Avail'] = "placeholder"
    testreq.app['Creds'][cookie]['OS_sess'] = "placeholder"
    with pytest.raises(HTTPUnauthorized):
        api_check(testreq)


def test_api_check_raise_on_no_session():
    """Test raise if there's no established OS session during an API call."""
    testreq = get_request_with_fernet()
    cookie, testreq.cookies['S3BROW_SESSION'] = generate_cookie(testreq)
    testreq.app['Sessions'] = [cookie]
    testreq.app['Creds'][cookie] = {}
    testreq.app['Creds'][cookie]['Avail'] = "placeholder"
    with pytest.raises(HTTPUnauthorized):
        api_check(testreq)


def test_api_check_raise_on_no_avail():
    """Test raise if the availability wasn't checked before an API call."""
    testreq = get_request_with_fernet()
    cookie, testreq.cookies['S3BROW_SESSION'] = generate_cookie(testreq)
    testreq.app['Creds'][cookie] = {}
    testreq.app['Sessions'] = [cookie]
    with pytest.raises(HTTPUnauthorized):
        api_check(testreq)


def test_api_check_success():
    """Test that the api_check function runs with correct input."""
    testreq = get_request_with_fernet()
    cookie, testreq.cookies['S3BROW_SESSION'] = generate_cookie(testreq)
    testreq.app['Sessions'] = [cookie]
    testreq.app['Creds'][cookie] = {}
    testreq.app['Creds'][cookie]['Avail'] = "placeholder"
    testreq.app['Creds'][cookie]['OS_sess'] = "placeholder"
    testreq.app['Creds'][cookie]['ST_conn'] = "placeholder"
    ret = api_check(testreq)
    assert ret == cookie  # nosec


def test_get_availability_from_token(mocker):
    """Test the get_availability_from_token function"""
    mocker.patch("s3browser._convenience.setd", new={
        "auth_endpoint_url": "http://example.osexampleserver.com:5001/v3"
    })
    # Test with an invalid token
    assert get_availability_from_token("awefjoiooivo") == "INVALID"  # nosec

    # Make the required patches to urllib.request to test the function
    mocker.patch("urllib.request.urlopen", new=urlopen)

    # Test with a valid token
    token = hashlib.md5(os.urandom(64)).hexdigest()  # nosec
    avail = get_availability_from_token(token)

    assert (  # nosec
        avail['projects'] == mock_token_output['projects']
    )
    assert (  # nosec
        avail['domains'] == mock_token_output['domains']
    )


def test_initiate_os_session(mocker):
    """Test initiate_os_session function"""
    mocker.patch("s3browser.settings.setd", new={
        "auth_endpoint_url": "http://example-auth.exampleosep.com:5001/v3"
    })
    ret = initiate_os_session(
        hashlib.md5(os.urandom(64)).hexdigest(),  # nosec
        "testproject"
    )
    assert type(ret) is Session  # nosec


def test_initiate_os_service(mocker):
    """Test initiate_os_servce function"""
    mocker.patch("s3browser.settings.setd", new={
        "auth_endpoint_url": "http://example-auth.exampleosep.com:5001/v3",
        "swift_endpoint_url": "http://obj.exampleosep.com:443/v1",
    })
    sess_mock = mocker.MagicMock(Session)
    ret = initiate_os_service(sess_mock(), 'testprojct')
    assert type(ret) is SwiftService  # nosec
