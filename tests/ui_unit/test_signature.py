"""Module for testing ``signature.py``."""


import types
import unittest

import aiohttp

from swift_browser_ui.ui.signature import handle_signature_request
from swift_browser_ui.ui.signature import handle_ext_token_create
from swift_browser_ui.ui.signature import handle_ext_token_remove
from swift_browser_ui.ui.signature import handle_ext_token_list

import tests.common.mockups


class SignatureMiscTestClass(
    tests.common.mockups.APITestBase,
):
    """Class for testing the signature module misc handlers."""

    def setUp(self):
        """Set up relevant mocks."""
        super().setUp()
        self.sign_mock = unittest.mock.AsyncMock(
            return_value={
                "valid": 15000000,
                "signature": "test-signature",
            }
        )
        self.sign_patch = unittest.mock.patch(
            "swift_browser_ui.ui._convenience.sign", self.sign_mock
        )

        self.mock_request.match_info = {"valid": 600, "count": 60, "project": "test-id-0"}
        self.mock_request.query = {
            "path": "/test/path",
            "count": "60",
        }

        self.get_tempurl_key_mock = unittest.mock.AsyncMock(return_value="test-key")
        self.get_tempurl_key_patch = unittest.mock.patch(
            "swift_browser_ui.ui._convenience.get_tempurl_key", self.get_tempurl_key_mock
        )

        self.mock_request_noval = types.SimpleNamespace(
            **{
                "query": {},
                "match_info": {},
            }
        )

        self.p_get_sess = unittest.mock.patch(
            "swift_browser_ui.ui.signature.aiohttp_session.get_session",
            self.aiohttp_session_get_session_mock,
        )

        self.mock_client_text = "Test token listing."

    async def test_handle_signature_request_correct(self):
        """Test signature request handler."""
        with self.p_get_sess, self.sign_patch:
            resp = await handle_signature_request(self.mock_request)
        self.assertIsInstance(resp, aiohttp.web.Response)

    async def test_handle_signature_request_fail_no_values(self):
        """Test signature request handler when failing on client error."""
        with self.assertRaises(aiohttp.web_exceptions.HTTPClientError):
            with self.p_get_sess, self.sign_patch:
                await handle_signature_request(self.mock_request_noval)


class SignatureTokenTestClass(
    tests.common.mockups.APITestBase,
):
    """Class for testing the token creation proxy handlers."""

    def setUp(self):
        """Set up relevant mocks."""
        super().setUp()
        self.mock_request.match_info = {
            "id": "test-token-id",
            "project": "test-id-0",
        }

        self.setd_mock = {
            "sharing_internal_endpoint": "http://sharing-test-endpoint",
            "request_internal_endpoint": "http://request-test-endpoint",
        }
        self.setd_patch = unittest.mock.patch(
            "swift_browser_ui.ui.signature.setd", self.setd_mock
        )

        self.setd_mock_missing_endpoints = {
            "sharing_internal_endpoint": None,
            "request_internal_endpoint": None,
        }
        self.setd_missing_patch = unittest.mock.patch(
            "swift_browser_ui.ui.signature.setd", self.setd_mock_missing_endpoints
        )

        self.sign_mock = unittest.mock.AsyncMock(
            return_value={
                "valid": 15000000,
                "signature": "test-signature",
            }
        )
        self.sign_patch = unittest.mock.patch(
            "swift_browser_ui.ui._convenience.sign", self.sign_mock
        )

        self.p_get_sess = unittest.mock.patch(
            "swift_browser_ui.ui.signature.aiohttp_session.get_session",
            self.aiohttp_session_get_session_mock,
        )

    async def test_handle_ext_token_create_correct(self):
        """Test external API token creation handler."""
        with self.sign_patch, self.setd_patch, self.p_get_sess:
            resp = await handle_ext_token_create(self.mock_request)
            self.assertIsInstance(resp, aiohttp.web.Response)
            self.assertEqual(resp.status, 201)

    async def test_handle_ext_token_create_fail_no_api_address(self):
        """Test external API token creation handler with no API address."""
        with self.sign_patch, self.setd_missing_patch, self.p_get_sess:
            with self.assertRaises(aiohttp.web.HTTPNotFound):
                await handle_ext_token_create(self.mock_request)

    async def test_handle_ext_token_create_fail_token_creation(self):
        """Test external API token creation handler in case of failure."""
        self.mock_client_response.status = 500
        self.mock_client_response.text.return_value = "Error"
        with self.sign_patch, self.setd_patch, self.p_get_sess:
            with self.assertRaises(aiohttp.web.HTTPInternalServerError):
                await handle_ext_token_create(self.mock_request)

    async def test_handle_ext_token_remove_correct(self):
        """Test external API token removal handler."""
        with self.sign_patch, self.setd_patch, self.p_get_sess:
            self.mock_request.app["api_client"] = types.SimpleNamespace(
                **{
                    "delete": unittest.mock.AsyncMock(
                        return_value=self.MockHandler(
                            self.mock_client_response,
                        )
                    ),
                }
            )
            resp = await handle_ext_token_remove(self.mock_request)
            self.assertIsInstance(resp, aiohttp.web.Response)
            self.assertEqual(resp.status, 204)

    async def test_handle_ext_token_remove_fail_no_api_address(self):
        """Test external API token creation handler with no API address."""
        with self.sign_patch, self.setd_missing_patch, self.p_get_sess:
            with self.assertRaises(aiohttp.web.HTTPNotFound):
                await handle_ext_token_remove(self.mock_request)

    async def test_handle_ext_token_list_correct(self):
        """Test external API token listing handler."""
        with self.sign_patch, self.setd_patch, self.p_get_sess:
            resp = await handle_ext_token_list(self.mock_request)
            self.assertIsInstance(resp, aiohttp.web.Response)
            self.assertEqual(resp.status, 200)

    async def test_handle_ext_token_list_fail_no_api_address(self):
        """Test external API token listing handler with no API address."""
        with self.sign_patch, self.setd_missing_patch, self.p_get_sess:
            with self.assertRaises(aiohttp.web.HTTPNotFound):
                await handle_ext_token_list(self.mock_request)
