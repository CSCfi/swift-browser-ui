"""
Module for testing s3browser._convenience
"""


import pytest
from creation import get_request_with_fernet
from aiohttp.web import HTTPForbidden, HTTPUnauthorized
from s3browser._convenience import api_check, generate_cookie


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
    with pytest.raises(HTTPForbidden):
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
    testreq.app['Sessions'] = [cookie]
    with pytest.raises(HTTPUnauthorized):
        api_check(testreq)
