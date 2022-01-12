"""Module for testing ``signature.py``."""


import types
import unittest

import aiohttp

from swift_browser_ui.ui.signature import handle_signature_request
from swift_browser_ui.ui.signature import handle_ext_token_create
from swift_browser_ui.ui.signature import handle_ext_token_remove
from swift_browser_ui.ui.signature import handle_ext_token_list
from swift_browser_ui.ui.signature import handle_form_post_signature


class SignatureMiscTestClass(unittest.IsolatedAsyncioTestCase):
    """Class for testing the signature module misc handlers."""

    def setUp(self):
        """Set up relevant mocks."""
        self.session_check_mock = unittest.mock.Mock()
        self.session_check_patch = unittest.mock.patch(
            "swift_browser_ui.ui._convenience.session_check", self.session_check_mock
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

        self.api_check_mock = unittest.mock.Mock(return_value="test-session")
        self.api_check_patch = unittest.mock.patch(
            "swift_browser_ui.ui._convenience.api_check", self.api_check_mock
        )

        self.mock_request = types.SimpleNamespace(
            **{
                "query": {
                    "path": "/test/path",
                    "count": "60",
                },
                "match_info": {
                    "valid": "600",
                    "container": "test-container",
                },
                "app": {
                    "Sessions": {
                        "test-session": {
                            "ST_conn": None,
                            "OS_sess": types.SimpleNamespace(
                                **{
                                    "get_endpoint": unittest.mock.Mock(
                                        return_value="https://test-endpoint/swift/v1/AUTH_test"  # noqa
                                    )
                                }
                            ),
                        },
                    }
                },
                "remote": "test-remote",
            }
        )

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

    async def test_handle_signature_request_correct(self):
        """Test signature request handler."""
        with self.session_check_patch, self.sign_patch:
            resp = await handle_signature_request(self.mock_request)

            self.assertIsInstance(resp, aiohttp.web.Response)

    async def test_handle_signature_request_fail_no_values(self):
        """Test signature request handler when failing on client error."""
        with self.session_check_patch, self.sign_patch:
            with self.assertRaises(aiohttp.web_exceptions.HTTPClientError):
                await handle_signature_request(self.mock_request_noval)

    async def test_handle_form_post_signature_correct(self):
        """Test form post signature handler."""
        with self.get_tempurl_key_patch, self.api_check_patch:
            resp = await handle_form_post_signature(self.mock_request)
            self.assertIsInstance(resp, aiohttp.web.Response)


class SignatureTokenTestClass(unittest.IsolatedAsyncioTestCase):
    """Class for testing the token creation proxy handlers."""

    def setUp(self):
        """Set up relevant mocks."""
        self.mock_request = types.SimpleNamespace(
            **{
                "match_info": {"id": "test-token"},
                "app": {
                    "Sessions": {
                        "test-session": {
                            "active_project": {
                                "id": "test-project",
                            },
                        },
                    },
                    "api_client": types.SimpleNamespace(
                        **{
                            "post": unittest.mock.AsyncMock(
                                return_value=types.SimpleNamespace(**{"status": 200})
                            ),
                            "delete": unittest.mock.AsyncMock(),
                            "get": unittest.mock.AsyncMock(
                                return_value=types.SimpleNamespace(
                                    **{
                                        "text": unittest.mock.AsyncMock(
                                            return_value="test-token"
                                        )
                                    }
                                )
                            ),
                        }
                    ),
                },
            }
        )

        self.mock_request_fail_post = types.SimpleNamespace(
            **{
                "match_info": {"id": "test-token"},
                "app": {
                    "Sessions": {
                        "test-session": {
                            "active_project": {"id": "test-project"},
                        },
                    },
                    "api_client": types.SimpleNamespace(
                        **{
                            "post": unittest.mock.AsyncMock(
                                return_value=types.SimpleNamespace(
                                    **{
                                        "status": 500,
                                        "text": unittest.mock.AsyncMock(
                                            return_value="Error"
                                        ),
                                        "url": "http://example-endpoint",
                                    }
                                )
                            ),
                        }
                    ),
                },
            }
        )

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

        self.api_check_mock = unittest.mock.Mock(return_value="test-session")
        self.api_check_patch = unittest.mock.patch(
            "swift_browser_ui.ui._convenience.api_check", self.api_check_mock
        )

    async def test_handle_ext_token_create_correct(self):
        """Test external API token creation handler."""
        with self.sign_patch, self.setd_patch, self.api_check_patch:
            resp = await handle_ext_token_create(self.mock_request)
            self.assertIsInstance(resp, aiohttp.web.Response)
            self.assertEqual(resp.status, 201)

    async def test_handle_ext_token_create_fail_no_api_address(self):
        """Test external API token creation handler with no API address."""
        with self.sign_patch, self.setd_missing_patch, self.api_check_patch:
            with self.assertRaises(aiohttp.web.HTTPNotFound):
                await handle_ext_token_create(self.mock_request)

    async def test_handle_ext_token_create_fail_token_creation(self):
        """Test external API token creation handler in case of failure."""
        with self.sign_patch, self.setd_patch, self.api_check_patch:
            with self.assertRaises(aiohttp.web.HTTPInternalServerError):
                await handle_ext_token_create(self.mock_request_fail_post)

    async def test_handle_ext_token_remove_correct(self):
        """Test external API token removal handler."""
        with self.sign_patch, self.setd_patch, self.api_check_patch:
            resp = await handle_ext_token_remove(self.mock_request)
            self.assertIsInstance(resp, aiohttp.web.Response)
            self.assertEqual(resp.status, 204)

    async def test_handle_ext_token_remove_fail_no_api_address(self):
        """Test external API token creation handler with no API address."""
        with self.sign_patch, self.setd_missing_patch, self.api_check_patch:
            with self.assertRaises(aiohttp.web.HTTPNotFound):
                await handle_ext_token_remove(self.mock_request)

    async def test_handle_ext_token_list_correct(self):
        """Test external API token listing handler."""
        with self.sign_patch, self.setd_patch, self.api_check_patch:
            resp = await handle_ext_token_list(self.mock_request)
            self.assertIsInstance(resp, aiohttp.web.Response)
            self.assertEqual(resp.status, 200)

    async def test_handle_ext_token_list_fail_no_api_address(self):
        """Test external API token listing handler with no API address."""
        with self.sign_patch, self.setd_missing_patch, self.api_check_patch:
            with self.assertRaises(aiohttp.web.HTTPNotFound):
                await handle_ext_token_list(self.mock_request)
