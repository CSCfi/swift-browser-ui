"""Test ``swift_browser_ui.login`` module."""

import hashlib
import os
import unittest

import aiohttp

import swift_browser_ui.ui.login
import swift_browser_ui.ui.settings

import tests.common.mockups

_path = "/auth/OS-FEDERATION/identity_providers/haka/protocols/saml2/websso"


class LoginTestClass(tests.common.mockups.APITestBase):
    """Testing the Object Browser API."""

    def setUp(self):
        """."""
        super().setUp()
        self.setd_mock["static_directory"] = (
            __file__.replace("/settings.py", "") + "/static"
        )
        self.p_get_sess = unittest.mock.patch(
            "swift_browser_ui.ui.login.aiohttp_session.get_session",
            self.aiohttp_session_get_session_mock,
        )

    async def test_oidc_start(self):
        """Test oidc initial request."""
        self.setd_mock["oidc_enabled"] = True
        with unittest.mock.patch(
            "swift_browser_ui.ui.login.setd",
            self.setd_mock,
        ):
            resp = await swift_browser_ui.ui.login.oidc_start(self.mock_request)
            self.assertEqual(resp.status, 302)
            self.assertEqual(resp.headers["Location"], "/should_be_oidc_provider")

    async def test_oidc_end(self):
        """Test oidc initial request."""
        self.setd_mock["oidc_enabled"] = True
        with unittest.mock.patch(
            "swift_browser_ui.ui.login.setd",
            self.setd_mock,
        ), self.p_new_sess:
            self.mock_request.query["code"] = "code"
            self.mock_request.query["state"] = "state"
            resp = await swift_browser_ui.ui.login.oidc_end(self.mock_request)
            self.assertEqual(resp.status, 302)
            self.assertEqual(resp.headers["Location"], "/login")

    async def test_handle_login(self):
        """Test initial login handler."""
        self.mock_request.query["navto"] = "http://example"
        resp = await swift_browser_ui.ui.login.handle_login(self.mock_request)

        self.assertEqual(resp.headers["Location"], "/login/front")
        self.assertEqual(resp.status, 302)

    async def test_handle_login_oidc_enabled(self):
        """Test login handler with OIDC enabled."""
        self.setd_mock["oidc_enabled"] = True
        with unittest.mock.patch(
            "swift_browser_ui.ui.login.setd",
            self.setd_mock,
        ):
            with self.p_get_sess:
                resp = await swift_browser_ui.ui.login.handle_login(self.mock_request)
                self.assertEqual(resp.status, 302)
                self.assertEqual(resp.headers["Location"], "/")

            with self.p_get_sess_oidc:
                resp = await swift_browser_ui.ui.login.handle_login(self.mock_request)
                self.assertEqual(resp.status, 200)

    async def test_sso_query_begin_with_trust(self):
        """Test sso query begin function."""
        with unittest.mock.patch(
            "swift_browser_ui.ui.login.setd",
            self.setd_mock,
        ):
            resp = await swift_browser_ui.ui.login.sso_query_begin(None)
            self.assertEqual(resp.status, 302)
            self.assertEqual(
                resp.headers["Location"],
                f"https://example.os.com:5001/v3{_path}"
                "?origin=https://localhost/login/websso",
            )

        self.setd_mock["oidc_enabled"] = True
        with unittest.mock.patch(
            "swift_browser_ui.ui.login.setd",
            self.setd_mock,
        ), self.p_get_sess:
            resp = await swift_browser_ui.ui.login.handle_login(self.mock_request)
            self.assertEqual(resp.status, 302)
            self.assertEqual(resp.headers["Location"], "/")

    async def test_sso_query_begin_without_trust(self):
        """Test sso query begin without trust."""
        self.setd_mock["has_trust"] = False
        with unittest.mock.patch(
            "swift_browser_ui.ui.login.setd",
            self.setd_mock,
        ):
            resp = await swift_browser_ui.ui.login.sso_query_begin(None)
            self.assertEqual(resp.status, 200)

    async def test_sso_query_begin_oidc_enabled(self):
        """Test sso query begin with OIDC enabled."""
        self.setd_mock["oidc_enabled"] = True
        with unittest.mock.patch(
            "swift_browser_ui.ui.login.setd",
            self.setd_mock,
        ), self.p_get_sess:
            resp = await swift_browser_ui.ui.login.sso_query_begin(self.mock_request)
            self.assertEqual(resp.status, 302)
            self.assertEqual(resp.headers["Location"], "/")

    async def test_test_token(self):
        """Test the token validity checks."""
        token_md5 = hashlib.md5(os.urandom(64)).hexdigest()  # nosec
        token_fernet = (  # nosec
            "gAAAAABiAmI1X69b0kYq7V41NYl7RJDGIikq4rvN4nWwWeo-CNLkr08ZSLxA0aL"
            "DqUhMYIhUSvkqqAbUvHXsjcHfx8gIroUY4h3y1MGBOvpHOZqdhCHq5oMuYsHE1rSpzq7UNfVsW"
            "ce6"
        )

        # Test with missing token
        with self.assertRaises(aiohttp.web.HTTPBadRequest):
            swift_browser_ui.ui.login.test_token(
                {},
                self.mock_request,
            )

        # Test with malformed "fernet" token
        with self.assertRaises(aiohttp.web.HTTPBadRequest):
            swift_browser_ui.ui.login.test_token(
                {
                    "token": b"1_HsWO4xZLCL5NRBpvF_Fg==",
                },
                self.mock_request,
            )

        # Test with token in form
        ret = swift_browser_ui.ui.login.test_token(
            {
                "token": token_md5,
            },
            self.mock_request,
        )
        self.assertEqual(ret, token_md5)

        # Test with token in query
        self.mock_request.query["token"] = token_fernet
        ret = swift_browser_ui.ui.login.test_token(
            {},
            self.mock_request,
        )
        self.assertEqual(ret, token_fernet)
        self.mock_request.query = {}

        # Test with token in headers
        self.mock_request.headers["X-Auth-Token"] = token_md5
        ret = swift_browser_ui.ui.login.test_token(
            {},
            self.mock_request,
        )
        self.assertEqual(ret, token_md5)

        # Test with token that's malformed with both md5 and fernet
        self.mock_request.headers["X-Auth-Token"] = "token-garbage"
        with self.assertRaises(aiohttp.web.HTTPBadRequest):
            swift_browser_ui.ui.login.test_token(
                {},
                self.mock_request,
            )

    async def test_credentials_login_end(self):
        """Test credentials login end handler."""
        self.mock_request.post.return_value = {}
        self.mock_client_response.text.return_value = "test-reason"
        # Test with missing username/password
        with self.assertRaises(aiohttp.web.HTTPBadRequest):
            await swift_browser_ui.ui.login.credentials_login_end(
                self.mock_request,
            )

        self.mock_request.post.return_value = {
            "username": "test-username",
            "password": "test-password",
        }
        # Test with different response failure status codes
        self.mock_client_response.status = 400
        with self.assertRaises(aiohttp.web.HTTPBadRequest):
            await swift_browser_ui.ui.login.credentials_login_end(
                self.mock_request,
            )
        self.mock_client_response.status = 401
        with self.assertRaises(aiohttp.web.HTTPUnauthorized):
            await swift_browser_ui.ui.login.credentials_login_end(
                self.mock_request,
            )
        self.mock_client_response.status = 500
        with self.assertRaises(aiohttp.web.HTTPUnauthorized):
            await swift_browser_ui.ui.login.credentials_login_end(
                self.mock_request,
            )

        # Test with "correct" credentials
        self.mock_client_response.status = 201
        self.mock_client_response.headers["X-Subject-Token"] = "test-token"
        mock_login = unittest.mock.AsyncMock()
        patch_login = unittest.mock.patch(
            "swift_browser_ui.ui.login.login_with_token", mock_login
        )
        with patch_login:
            await swift_browser_ui.ui.login.credentials_login_end(
                self.mock_request,
            )
        mock_login.assert_awaited_once_with(
            self.mock_request,
            "test-token",
        )

    async def test_sso_query_end(self):
        """Test SSO query end handler."""
        self.mock_request.post.return_value = {
            "token": "test-token",
        }
        mock_login = unittest.mock.AsyncMock()
        patch_login = unittest.mock.patch(
            "swift_browser_ui.ui.login.login_with_token",
            mock_login,
        )
        patch_test_token = unittest.mock.patch(
            "swift_browser_ui.ui.login.test_token",
            unittest.mock.Mock(return_value="test-token"),
        )
        with patch_login, patch_test_token:
            await swift_browser_ui.ui.login.sso_query_end(
                self.mock_request,
            )
        mock_login.assert_awaited_once_with(
            self.mock_request,
            "test-token",
        )

    async def test_login_with_token(self):
        """
        Test sso query end function with correct execution parameters.

        This version tests the token delivery in a http encoded form.
        """
        self.setd_mock["session_lifetime"] = 28800
        self.setd_mock["history_lifetime"] = 2592000
        self.setd_mock["force_restricted_mode"] = False
        self.setd_mock["swift_endpoint_url"] = ("http://obj.exampleosep.com:443/v1",)
        self.setd_mock["os_accepted_roles"] = "object_store_user"
        patch1 = unittest.mock.patch(
            "swift_browser_ui.ui.login.setd",
            self.setd_mock,
        )

        # Patch away the convenience function for checking project availability
        mock_get_avail = unittest.mock.AsyncMock(
            return_value=tests.common.mockups.mock_token_output,
        )
        patch2 = unittest.mock.patch(
            "swift_browser_ui.ui.login.get_availability_from_token",
            mock_get_avail,
        )

        self.mock_client_response.headers["X-Subject-Token"] = "test-token"  # nosec
        self.mock_client_json = {
            "token": {
                "user": {
                    "name": "test-user",
                },
                "roles": [
                    {
                        "name": "object_store_user",
                    },
                ],
                "catalog": [
                    {
                        "type": "object-store",
                        "id": "test-id",
                        "name": "swift",
                        "endpoints": [
                            {
                                "region_id": "default",
                                "url": "https://test-swift:443/swift/v1/AUTH_test-id-0",
                                "region": "default",
                                "interface": "admin",
                                "id": "test-id",
                            },
                            {
                                "region_id": "default",
                                "url": "https://test-swift:443/swift/v1/AUTH_test-id-0",
                                "region": "default",
                                "interface": "public",
                                "id": "test-id",
                            },
                            {
                                "region_id": "default",
                                "url": "https://test-swift:443/swift/v1/AUTH_test-id-0",
                                "region": "default",
                                "interface": "internal",
                                "id": "test-id",
                            },
                        ],
                    },
                ],
            },
        }
        self.mock_client_response.json = unittest.mock.AsyncMock(
            return_value=self.mock_client_json,
        )

        token = hashlib.md5(os.urandom(64)).hexdigest()  # nosec

        with patch1, patch2, self.p_new_sess:
            resp = await swift_browser_ui.ui.login.login_with_token(
                self.mock_request,
                token,
            )

        self.assertEqual(resp.status, 303)
        self.assertEqual(resp.headers["Location"], "/browse")
        self.mock_client.post.assert_called_with(
            "https://example.os.com:5001/v3/auth/tokens",
            json={
                "auth": {
                    "identity": {
                        "methods": [
                            "token",
                        ],
                        "token": {
                            "id": token,
                        },
                    },
                    "scope": {"project": {"id": "what"}},
                }
            },
        )

        self.mock_request.cookies["NAV_TO"] = "/test-nav"
        with patch1, patch2, self.p_new_sess:
            resp = await swift_browser_ui.ui.login.login_with_token(
                self.mock_request,
                token,
            )

        self.assertEqual(resp.headers["Location"], "/test-nav")

        self.setd_mock["oidc_enabled"] = True
        with patch1, patch2, self.p_get_sess:
            resp = await swift_browser_ui.ui.login.login_with_token(
                self.mock_request,
                token,
            )
            self.assertEqual(resp.status, 303)
            self.assertEqual(resp.headers["Location"], "/test-nav")
        self.setd_mock["oidc_enabled"] = False

        self.mock_client_response.status = 401
        with self.assertRaises(
            aiohttp.web.HTTPUnauthorized
        ), patch1, patch2, self.p_new_sess:
            await swift_browser_ui.ui.login.login_with_token(
                self.mock_request,
                token,
            )

        self.mock_client_response.status = 403
        with self.assertRaises(
            aiohttp.web.HTTPForbidden
        ), patch1, patch2, self.p_new_sess:
            await swift_browser_ui.ui.login.login_with_token(
                self.mock_request,
                token,
            )

    async def test_handle_logout(self):
        """Test logging out."""
        with self.p_get_sess:
            resp = await swift_browser_ui.ui.login.handle_logout(
                self.mock_request,
            )
        self.mock_client.delete.assert_called()
        self.assertEqual(resp.status, 303)
        self.assertEqual(resp.headers["Location"], "/")

        # Test with "undecryptable" session
        self.aiohttp_session_get_session_mock.side_effect = aiohttp.web.HTTPUnauthorized
        with self.assertRaises(aiohttp.web.HTTPUnauthorized), self.p_get_sess:
            await swift_browser_ui.ui.login.handle_logout(
                self.mock_request,
            )
