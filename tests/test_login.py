"""Test s3browser.login module"""


import pytest


import s3browser.login
import s3browser.settings


@pytest.mark.asyncio
async def test_handle_login():
    """Test initial login handler"""
    resp = await s3browser.login.handle_login(None)
    assert resp.headers['Location'] == "/login/front"  # nosec
    assert resp.status == 302  # nosec


@pytest.mark.asyncio
async def test_sso_query_begin():
    """Test sso query begin function"""
    # First test without trust
    resp = await s3browser.login.sso_query_begin(None)
    assert resp.status == 200  # nosec

    # Test with trust
    s3browser.settings.setd['auth_endpoint_url'] = \
        "https://example.os.com:5001/v3"
    s3browser.settings.setd['origin_address'] = \
        "https://localhost/login/websso"
    s3browser.settings.setd['has_trust'] = True
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
async def test_sso_query_end():
    """Test sso query end function"""
    pass


@pytest.mark.asyncio
async def test_handle_logout():
    """Test the logout function"""
    pass
