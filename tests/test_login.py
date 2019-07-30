"""Test ``s3browser.login`` module."""

import hashlib
import os


import pytest
from aiohttp.web import HTTPClientError
import unittest

import s3browser.login
import s3browser.settings


from .creation import get_request_with_fernet, get_request_with_mock_openstack
from .mockups import return_project_avail
from .mockups import return_invalid


@pytest.mark.asyncio
async def test_handle_login():
    """Test initial login handler."""
    resp = await s3browser.login.handle_login(None)
    assert resp.headers['Location'] == "/login/front"  # nosec
    assert resp.status == 302  # nosec


@pytest.mark.asyncio
async def test_sso_query_begin_with_trust():
    """Test sso query begin function."""
    with unittest.mock.patch("s3browser.login.setd", new={
        "auth_endpoint_url": "https://example.os.com:5001/v3",
        "origin_address": "https://localhost/login/websso",
        "has_trust": True,
    }):
        resp = await s3browser.login.sso_query_begin(None)
        assert resp.status == 302  # nosec
        assert resp.headers['Location'] == (  # nosec
            "https://example.os.com:5001/v3" +
            "/auth/OS-FEDERATION/identity_providers/haka/protocols/saml2/websso" +
            "?origin={origin}".format(
                origin="https://localhost/login/websso"
            )
        )


@pytest.mark.asyncio
async def test_sso_query_begin_without_trust():
    """Test sso query begin without trust."""
    with unittest.mock.patch("s3browser.login.setd", new={
        "auth_endpoint_url": "https://example.os.com:5001/v3",
        "origin_address": "https://localhost/login/websso",
        "has_trust": False,
        "static_directory": __file__.replace("/settings.py", "") + "/static",
    }):
        resp = await s3browser.login.sso_query_begin(None)
        assert resp.status == 200  # nosec


@pytest.mark.asyncio
async def test_sso_query_end_successful_http_form():
    """
    Test sso query end function with correct execution parameters.

    This version tests the token delivery in a http encoded form.
    """
    patch1 = unittest.mock.patch("s3browser.login.setd", new={
        "auth_endpoint_url": "http://example-auth.exampleosep.com:5001/v3",
        "swift_endpoint_url": "http://obj.exampleosep.com:443/v1",
    })

    # Patch away the convenience function for checking project availability
    patch2 = unittest.mock.patch(
        "s3browser.login.get_availability_from_token",
        new=return_project_avail
    )

    patch3 = unittest.mock.patch(
        "keystoneauth1.identity.v3.Token"
    )
    patch4 = unittest.mock.patch(
        "keystoneauth1.session.Session"
    )
    patch5 = unittest.mock.patch(
        "swiftclient.service.SwiftService"
    )

    with patch1, patch2, patch3, patch4, patch5:
        req = get_request_with_fernet()
        token = hashlib.md5(os.urandom(64)).hexdigest()  # nosec
        req.set_post({
            "token": token
        })

        resp = await s3browser.login.sso_query_end(req)

        # Test for the correct values
        assert req.app['Sessions']  # nosec
        session = req.app['Sessions'][0]
        assert req.app['Creds'][session]['Token'] is not None  # nosec
        assert req.app['Creds'][session]['Avail'] != "INVALID"  # nosec
        assert req.app['Creds'][session]['active_project'] == {  # nosec
            "name": "placeholder",
            "id": "placeholder",
        }
        assert resp.status == 303  # nosec
        assert resp.headers['Location'] == "/browse"  # nosec
        assert "S3BROW_SESSION" in resp.cookies  # nosec


@pytest.mark.asyncio
async def test_sso_query_end_successful_url_form():
    """
    Test sso query end function with correct execution parameters.

    This version tests the token delivery in a urlencoded form instead of a
    http encoded one.
    """
    patch1 = unittest.mock.patch("s3browser.login.setd", new={
        "auth_endpoint_url": "http://example-auth.exampleosep.com:5001/v3",
        "swift_endpoint_url": "http://obj.exampleosep.com:443/v1",
    })

    patch2 = unittest.mock.patch(
        "s3browser.login.get_availability_from_token",
        new=return_project_avail
    )

    patch3 = unittest.mock.patch(
        "keystoneauth1.identity.v3.Token"
    )
    patch4 = unittest.mock.patch(
        "keystoneauth1.session.Session"
    )
    patch5 = unittest.mock.patch(
        "swiftclient.service.SwiftService"
    )

    with patch1, patch2, patch3, patch4, patch5:
        req = get_request_with_fernet()
        token = hashlib.md5(os.urandom(64)).hexdigest()  # nosec

        req.query['token'] = token

        resp = await s3browser.login.sso_query_end(req)

        # Test for the correct values
        assert req.app['Sessions']  # nosec
        session = req.app['Sessions'][0]
        assert req.app['Creds'][session]['Token'] is not None  # nosec
        assert req.app['Creds'][session]['Avail'] != "INVALID"  # nosec
        assert req.app['Creds'][session]['active_project'] == {  # nosec
            "name": "placeholder",
            "id": "placeholder",
        }
        assert resp.status == 303  # nosec
        assert resp.headers['Location'] == "/browse"  # nosec
        assert "S3BROW_SESSION" in resp.cookies  # nosec


@pytest.mark.asyncio
async def test_sso_query_end_successful_header():
    """
    Test sso query end function with correct execution parameters.

    This version tests the token delivery in a HTTP header.
    """
    patch1 = unittest.mock.patch("s3browser.login.setd", new={
        "auth_endpoint_url": "http://example-auth.exampleosep.com:5001/v3",
        "swift_endpoint_url": "http://obj.exampleosep.com:443/v1",
    })

    # Patch away the convenience function for checking project availability
    patch2 = unittest.mock.patch(
        "s3browser.login.get_availability_from_token",
        new=return_project_avail
    )

    patch3 = unittest.mock.patch(
        "keystoneauth1.identity.v3.Token"
    )
    patch4 = unittest.mock.patch(
        "keystoneauth1.session.Session"
    )
    patch5 = unittest.mock.patch(
        "swiftclient.service.SwiftService"
    )

    with patch1, patch2, patch3, patch4, patch5:
        req = get_request_with_fernet()
        token = hashlib.md5(os.urandom(64)).hexdigest()  # nosec

        req.headers['X-Auth-Token'] = token

        resp = await s3browser.login.sso_query_end(req)

        # Test for the correct values
        assert req.app['Sessions']  # nosec
        session = req.app['Sessions'][0]
        assert req.app['Creds'][session]['Token'] is not None  # nosec
        assert req.app['Creds'][session]['Avail'] != "INVALID"  # nosec
        assert req.app['Creds'][session]['active_project'] == {  # nosec
            "name": "placeholder",
            "id": "placeholder",
        }
        assert resp.status == 303  # nosec
        assert resp.headers['Location'] == "/browse"  # nosec
        assert "S3BROW_SESSION" in resp.cookies  # nosec


@pytest.mark.asyncio
async def test_sso_query_end_unsuccessful_missing_token():
    """Test unsuccessful token delivery with token missing."""
    patch1 = unittest.mock.patch("s3browser.login.setd", new={
        "auth_endpoint_url": "http://example-auth.exampleosep.com:5001/v3",
        "swift_endpoint_url": "http://obj.exampleosep.com:443/v1",
    })

    patch2 = unittest.mock.patch(
        "keystoneauth1.identity.v3.Token"
    )
    patch3 = unittest.mock.patch(
        "keystoneauth1.session.Session"
    )
    patch4 = unittest.mock.patch(
        "swiftclient.service.SwiftService"
    )

    with patch1, patch2, patch3, patch4:
        req = get_request_with_fernet()

        with pytest.raises(HTTPClientError):
            _ = await s3browser.login.sso_query_end(req)


@pytest.mark.asyncio
async def test_sso_query_end_unsuccessful_invalid_token():
    """Test unsuccessful token delivery with an invalid."""
    patch1 = unittest.mock.patch("s3browser.login.setd", new={
        "auth_endpoint_url": "http://example-auth.exampleosep.com:5001/v3",
        "swift_endpoint_url": "http://obj.exampleosep.com:443/v1",
        "has_trust": False,
    })

    # Patch away the convenience function for checking project availability
    patch2 = unittest.mock.patch(
        "s3browser.login.get_availability_from_token",
        new=return_invalid
    )

    patch3 = unittest.mock.patch(
        "keystoneauth1.identity.v3.Token"
    )
    patch4 = unittest.mock.patch(
        "keystoneauth1.session.Session"
    )
    patch5 = unittest.mock.patch(
        "swiftclient.service.SwiftService"
    )

    with patch1, patch2, patch3, patch4, patch5:
        req = get_request_with_fernet()
        token = hashlib.md5(os.urandom(64)).hexdigest()  # nosec

        req.headers['X-Auth-Token'] = token

        resp = await s3browser.login.sso_query_end(req)

        assert resp.status == 302  # nosec
        assert resp.headers['Location'] == "/login"  # nosec
        assert "INVALID_TOKEN" in resp.cookies  # nosec


@pytest.mark.asyncio
async def test_handle_logout():
    """Test the logout function."""
    cookie, req = get_request_with_mock_openstack()

    sess_mock = unittest.mock.MagicMock("keystoneauth.session.Session")
    req.app['Creds'][cookie]['OS_sess'] = sess_mock()

    sess = req.app['Creds'][cookie]['OS_sess']

    resp = await s3browser.login.handle_logout(req)

    assert resp.status == 303  # nosec
    assert resp.headers["Location"] == "/"  # nosec
    sess.invalidate.assert_called_once()
    assert cookie not in req.app['Sessions']  # nosec
