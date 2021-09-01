"""Unit tests for swift_browser_ui.upload.auth module."""


import unittest.mock

import asynctest
import aiohttp.web

import swift_browser_ui.upload.auth
import tests.common.mockups


class AuthTestClass(asynctest.TestCase):
    """Test class for swift_browser_ui.upload.auth functions."""

    def setUp(self):
        """."""
        self.initiate_mock = unittest.mock.Mock(return_value="OS_Session")
        self.patch_initiate = unittest.mock.patch(
            "swift_browser_ui.upload.auth.initiate_os_session",
            self.initiate_mock,
        )
        super().setUp()

    async def test_handle_login(self):
        """Test swift_browser_ui.upload.auth.handle_login."""
        req = tests.common.mockups.Mock_Request()

        with self.assertRaises(aiohttp.web.HTTPUnauthorized):
            await swift_browser_ui.upload.auth.handle_login(req)

        req.set_match(
            {
                "project": "test-project",
            }
        )
        req.set_post(
            {
                "token": "test-token",
            }
        )
        with self.patch_initiate:
            resp = await swift_browser_ui.upload.auth.handle_login(req)
            self.assertIsNotNone(resp.cookies["RUNNER_SESSION_ID"])
            self.assertEqual(resp.status, 200)
            session_key = resp.cookies["RUNNER_SESSION_ID"].value
            self.assertEqual(req.app[session_key]["auth"], "OS_Session")

    async def test_handle_validate_authentication(self):
        """Test swift_browser_ui.upload.auth.handle_validate_authentication."""
        handler_mock = asynctest.CoroutineMock()
        req = tests.common.mockups.Mock_Request()
        req.set_path("/")

        t_singature_mock = asynctest.CoroutineMock()
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

        handler_mock = asynctest.CoroutineMock()

        await swift_browser_ui.upload.auth.handle_validate_authentication(
            req,
            handler_mock,
        )
        handler_mock.assert_awaited_once()
