"""
Module for testing s3browser._convenience
"""


import pytest
from creation import get_request_with_fernet
from aiohttp.web import HTTPUnauthorized
from s3browser._convenience import api_check, generate_cookie

# NOTE: disable_cache, decrypt_cookie, generate_cookie shouldn't need testing
# as the functions are simple and self-explanatory. session_check -function
# will be re-written soon, so the test shouldn't be implemented yet.


# The api_check session check function testing – Might seem unnecessary, but
# are required since e.g. token rescoping can fail the sessions before the
# next API call, also might try to use the API while rescoping -> 401
def test_api_check_raise_on_no_cookie():
    """
    Test that the function raises if there's no session cookie.
    """
    testreq = get_request_with_fernet()
    _, testreq.cookies['S3BROW_SESSION'] = generate_cookie(testreq)
    testreq.app['Sessions'] = []
    with pytest.raises(HTTPUnauthorized):
        api_check(testreq)


def test_api_check_raise_on_invalid_cookie():
    """
    Test that the function raises if there's an invalid session cookie.
    """
    testreq = get_request_with_fernet()
    testreq.app['Sessions'] = []
    with pytest.raises(HTTPUnauthorized):
        api_check(testreq)


# NOTE: The order of operations for these tests is significant (i.e. there is
# a reason some of the placeholders are missing in the test functions, to
# enable testing correct raising order in the same time)
def test_api_check_raise_on_no_connection():
    """
    Test that the function raises if there's no existing OS connection during
    an API call.
    """
    testreq = get_request_with_fernet()
    cookie, testreq.cookies['S3BROW_SESSION'] = generate_cookie(testreq)
    testreq.app['Sessions'] = [cookie]
    testreq.app['Creds'][cookie] = {}
    testreq.app['Creds'][cookie]['Avail'] = "placeholder"
    testreq.app['Creds'][cookie]['OS_sess'] = "placeholder"
    with pytest.raises(HTTPUnauthorized):
        api_check(testreq)


def test_api_check_raise_on_no_session():
    """
    Test that the function raises if there's no established OS session during
    an API call.
    """
    testreq = get_request_with_fernet()
    cookie, testreq.cookies['S3BROW_SESSION'] = generate_cookie(testreq)
    testreq.app['Sessions'] = [cookie]
    testreq.app['Creds'][cookie] = {}
    testreq.app['Creds'][cookie]['Avail'] = "placeholder"
    with pytest.raises(HTTPUnauthorized):
        api_check(testreq)


def test_api_check_raise_on_no_avail():
    """
    Test that the function raises if the availability hasn't been checked
    before an API call.
    """
    testreq = get_request_with_fernet()
    cookie, testreq.cookies['S3BROW_SESSION'] = generate_cookie(testreq)
    testreq.app['Creds'][cookie] = {}
    testreq.app['Sessions'] = [cookie]
    with pytest.raises(HTTPUnauthorized):
        api_check(testreq)


def test_api_check_success():
    testreq = get_request_with_fernet()
    cookie, testreq.cookies['S3BROW_SESSION'] = generate_cookie(testreq)
    testreq.app['Sessions'] = [cookie]
    testreq.app['Creds'][cookie] = {}
    testreq.app['Creds'][cookie]['Avail'] = "placeholder"
    testreq.app['Creds'][cookie]['OS_sess'] = "placeholder"
    testreq.app['Creds'][cookie]['ST_conn'] = "placeholder"
    ret = api_check(testreq)
    assert ret == cookie  # nosec

# NOTE: the next one in order would be get_availability_from_token, which
# requires a mock OS response – this cannot be done before the code has
# been refactored to have non-hardcoded endpoints.

# NOTE: the next one in order would be initiate_os_session, which needn't
# be tested, as it requires mocking the whole OS
# NOTE: the next would be initiate_os_service, which needn't be tested as
# it too requires mocking the whole OS
# Also a noteworthy thing, there probably is no point in directly testing
# OS SDK / swiftclient, since these are direct wrappers for the correct
# initialization function.
