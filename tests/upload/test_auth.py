"""Unit tests for swift_browser_ui.upload.auth module."""


import unittest

import aiohttp.web

import swift_browser_ui.upload.auth
import tests.common.mockups


class AuthTestClass(tests.common.mockups.APITestBase):
    """Test class for swift_browser_ui.upload.auth functions."""

    def setUp(self):
        """."""
        super().setUp()

    async def test_handle_login(self):
        """Test swift_browser_ui.upload.auth.handle_login."""
        with self.assertRaises(aiohttp.web.HTTPUnauthorized):
            await swift_browser_ui.upload.auth.handle_login(self.mock_request)

        self.mock_request.post.return_value = {
            "token": "test-token",
        }

        self.mock_client_response.headers["X-Subject-Token"] = "test-token"  # nosec
        self.mock_client_json = {
            "token": {
                "user": {
                    "name": "test-user",
                },
                "catalog": [
                    {
                        "type": "object-store",
                        "id": "test-id",
                        "name": "swift",
                        "endpoints": [
                            {
                            "region_id": 'default',
                            "url": 'https://test-swift:443/swift/v1/AUTH_test-id-0',
                            "region": 'default',
                            "interface": 'admin',
                            "id": 'test-id',
                            },
                            {
                            "region_id": 'default',
                            "url": 'https://test-swift:443/swift/v1/AUTH_test-id-0',
                            "region": 'default',
                            "interface": 'public',
                            "id": 'test-id',
                            },
                            {
                            "region_id": 'default',
                            "url": 'https://test-swift:443/swift/v1/AUTH_test-id-0',
                            "region": 'default',
                            "interface": 'internal',
                            "id": 'test-id',
                            },
                        ],
                    },
                ],
            },
        }
        self.mock_client_response.json = unittest.mock.AsyncMock(
            return_value=self.mock_client_json,
        )

        resp = await swift_browser_ui.upload.auth.handle_login(self.mock_request)
        self.assertIsNotNone(resp.cookies["RUNNER_SESSION_ID"])
        self.assertEqual(resp.status, 200)
        session_key = resp.cookies["RUNNER_SESSION_ID"].value
        self.assertIsNotNone(self.mock_request.app[session_key])

    async def test_handle_validate_authentication(self):
        """Test swift_browser_ui.upload.auth.handle_validate_authentication."""
        handler_mock = unittest.mock.AsyncMock()
        req = tests.common.mockups.Mock_Request()
        req.set_path("/")

        t_singature_mock = unittest.mock.AsyncMock()
        t_signature_patch = unittest.mock.patch(
            "swift_browser_ui.common.signature.test_signature", t_singature_mock
        )

        with self.assertRaises(aiohttp.web.HTTPUnauthorized):
            await swift_browser_ui.upload.auth.handle_validate_authentication(
                req, handler_mock
            )
        handler_mock.assert_not_called()

        req.set_query(
            {
                "signature": "test-signature",
                "valid": "is-valid",
            }
        )
        req.app["tokens"] = {"token_1", "token_2", "token_3"}

        with t_signature_patch:
            await swift_browser_ui.upload.auth.handle_validate_authentication(
                req, handler_mock
            )
        handler_mock.assert_called_once()

    async def test_handle_validate_authentication_health_endpoint(self):
        """Test handle_validate_authentication with health endpoint."""
        req = tests.common.mockups.Mock_Request()
        req.set_path("/health")

        handler_mock = unittest.mock.AsyncMock()

        await swift_browser_ui.upload.auth.handle_validate_authentication(
            req,
            handler_mock,
        )
        handler_mock.assert_awaited_once()
