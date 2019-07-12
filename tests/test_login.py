"""Test ``s3browser.login`` module."""

import hashlib
import os


import pytest
from aiohttp.web import HTTPClientError


import s3browser.login
import s3browser.settings


from .creation import get_request_with_fernet, get_request_with_mock_openstack
from .mockups import return_project_avail
from .mockups import return_same_cookie, return_invalid


@pytest.mark.asyncio
async def test_handle_login():
    """Test initial login handler."""
    resp = await s3browser.login.handle_login(None)
    assert resp.headers['Location'] == "/login/front"  # nosec
    assert resp.status == 302  # nosec


@pytest.mark.asyncio
async def test_sso_query_begin_with_trust(mocker):
    """Test sso query begin function."""
    mocker.patch("s3browser.login.setd", new={
        "auth_endpoint_url": "https://example.os.com:5001/v3",
        "origin_address": "https://localhost/login/websso",
        "has_trust": True,
    })
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
async def test_sso_query_begin_without_trust(mocker):
    """Test sso query begin without trust."""
    mocker.patch("s3browser.login.setd", new={
        "auth_endpoint_url": "https://example.os.com:5001/v3",
        "origin_address": "https://localhost/login/websso",
        "has_trust": False,
        "static_directory": __file__.replace("/settings.py", "") + "/static",
    })
    resp = await s3browser.login.sso_query_begin(None)
    assert resp.status == 200  # nosec


@pytest.mark.asyncio
async def test_sso_query_end_successful_http_form(mocker):
    """
    Test sso query end function with correct execution parameters.

    This version tests the token delivery in a http encoded form.
    """
    mocker.patch("s3browser.login.setd", new={
        "auth_endpoint_url": "http://example-auth.exampleosep.com:5001/v3",
        "swift_endpoint_url": "http://obj.exampleosep.com:443/v1",
    })

    # Patch away the convenience function for checking project availability
    mocker.patch(
        "s3browser.login.get_availability_from_token",
        new=return_project_avail
    )

    mocker.patch(
        "s3browser.login.generate_cookie",
        new=return_same_cookie
    )

    mocker.patch(
        "keystoneauth1.identity.v3.Token"
    )
    mocker.patch(
        "keystoneauth1.session.Session"
    )
    mocker.patch(
        "swiftclient.service.SwiftService"
    )

    req = get_request_with_fernet()
    session, _ = return_same_cookie(req)
    token = hashlib.md5(os.urandom(64)).hexdigest()  # nosec
    req.set_post({
        "token": token
    })

    resp = await s3browser.login.sso_query_end(req)

    # Test for the correct values
    assert session in req.app['Sessions']  # nosec
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
async def test_sso_query_end_successful_url_form(mocker):
    """
    Test sso query end function with correct execution parameters.

    This version tests the token delivery in a urlencoded form instead of a
    http encoded one.
    """
    mocker.patch("s3browser.login.setd", new={
        "auth_endpoint_url": "http://example-auth.exampleosep.com:5001/v3",
        "swift_endpoint_url": "http://obj.exampleosep.com:443/v1",
    })

    mocker.patch(
        "s3browser.login.get_availability_from_token",
        new=return_project_avail
    )

    mocker.patch(
        "s3browser.login.generate_cookie",
        new=return_same_cookie
    )

    mocker.patch(
        "keystoneauth1.identity.v3.Token"
    )
    mocker.patch(
        "keystoneauth1.session.Session"
    )
    mocker.patch(
        "swiftclient.service.SwiftService"
    )

    req = get_request_with_fernet()
    session, _ = return_same_cookie(req)
    token = hashlib.md5(os.urandom(64)).hexdigest()  # nosec

    session, _ = return_same_cookie(req)

    req.query['token'] = token

    resp = await s3browser.login.sso_query_end(req)

    # Test for the correct values
    assert session in req.app['Sessions']  # nosec
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
async def test_sso_query_end_successful_header(mocker):
    """
    Test sso query end function with correct execution parameters.

    This version tests the token delivery in a HTTP header.
    """
    mocker.patch("s3browser.login.setd", new={
        "auth_endpoint_url": "http://example-auth.exampleosep.com:5001/v3",
        "swift_endpoint_url": "http://obj.exampleosep.com:443/v1",
    })

    # Patch away the convenience function for checking project availability
    mocker.patch(
        "s3browser.login.get_availability_from_token",
        new=return_project_avail
    )

    mocker.patch(
        "s3browser.login.generate_cookie",
        new=return_same_cookie
    )

    mocker.patch(
        "keystoneauth1.identity.v3.Token"
    )
    mocker.patch(
        "keystoneauth1.session.Session"
    )
    mocker.patch(
        "swiftclient.service.SwiftService"
    )

    req = get_request_with_fernet()
    session, _ = return_same_cookie(req)
    token = hashlib.md5(os.urandom(64)).hexdigest()  # nosec

    req.headers['X-Auth-Token'] = token

    resp = await s3browser.login.sso_query_end(req)

    # Test for the correct values
    assert session in req.app['Sessions']  # nosec
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
async def test_sso_query_end_unsuccessful_missing_token(mocker):
    """Test unsuccessful token delivery with token missing."""
    mocker.patch("s3browser.login.setd", new={
        "auth_endpoint_url": "http://example-auth.exampleosep.com:5001/v3",
        "swift_endpoint_url": "http://obj.exampleosep.com:443/v1",
    })

    mocker.patch(
        "s3browser.login.generate_cookie",
        new=return_same_cookie
    )

    mocker.patch(
        "keystoneauth1.identity.v3.Token"
    )
    mocker.patch(
        "keystoneauth1.session.Session"
    )
    mocker.patch(
        "swiftclient.service.SwiftService"
    )

    req = get_request_with_fernet()
    _, _ = return_same_cookie(req)

    with pytest.raises(HTTPClientError):
        _ = await s3browser.login.sso_query_end(req)


@pytest.mark.asyncio
async def test_sso_query_end_unsuccessful_invalid_token(mocker):
    """Test unsuccessful token delivery with an invalid."""
    mocker.patch("s3browser.login.setd", new={
        "auth_endpoint_url": "http://example-auth.exampleosep.com:5001/v3",
        "swift_endpoint_url": "http://obj.exampleosep.com:443/v1",
        "has_trust": False,
    })

    # Patch away the convenience function for checking project availability
    mocker.patch(
        "s3browser.login.get_availability_from_token",
        new=return_invalid
    )

    mocker.patch(
        "s3browser.login.generate_cookie",
        new=return_same_cookie
    )

    mocker.patch(
        "keystoneauth1.identity.v3.Token"
    )
    mocker.patch(
        "keystoneauth1.session.Session"
    )
    mocker.patch(
        "swiftclient.service.SwiftService"
    )

    req = get_request_with_fernet()
    token = hashlib.md5(os.urandom(64)).hexdigest()  # nosec

    req.headers['X-Auth-Token'] = token

    resp = await s3browser.login.sso_query_end(req)

    assert resp.status == 302  # nosec
    assert resp.headers['Location'] == "/login"  # nosec
    assert "INVALID_TOKEN" in resp.cookies  # nosec


@pytest.mark.asyncio
async def test_handle_logout(mocker):
    """Test the logout function."""
    cookie, req = get_request_with_mock_openstack()

    sess_mock = mocker.MagicMock("keystoneauth.session.Session")
    req.app['Creds'][cookie]['OS_sess'] = sess_mock()

    sess = req.app['Creds'][cookie]['OS_sess']

    resp = await s3browser.login.handle_logout(req)

    assert resp.status == 204  # nosec
    sess.invalidate.assert_called_once()
    assert cookie not in req.app['Sessions']  # nosec
