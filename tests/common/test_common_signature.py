"""Module for testing singatures in bindings module."""


import hmac
import time

import unittest
import aiohttp.web

import swift_browser_ui.common.signature


class SignatureModuleTestCase(unittest.IsolatedAsyncioTestCase):
    """Test case for signature related methods."""

    def setUp(self):
        self.app_mock = {}
        super().setUp()

    async def test_sign_api_request(self):
        """Test sign_api_request function."""
        os_environ_mock = unittest.mock.Mock(return_value="testkey")
        os_environ_patch = unittest.mock.patch(
            "swift_browser_ui.common.signature.os.environ.get",
            new=os_environ_mock,
        )

        with os_environ_patch:
            ret = swift_browser_ui.common.signature.sign_api_request(
                "testpath", valid_for=60, key=b"testkey"
            )
            self.assertIsInstance(ret, dict)
            os_environ_mock.assert_not_called()

        with os_environ_patch:
            ret = swift_browser_ui.common.signature.sign_api_request("testpath")
            self.assertIsInstance(ret, dict)
            os_environ_mock.assert_called_once()

    async def test_test_signature_failure(self):
        """Test test_signature function when failure."""
        message_mock = "abcdefghijklmnopqrstuvwxyz"
        tokens_mock = []
        with self.assertRaises(aiohttp.web.HTTPUnauthorized):
            await swift_browser_ui.common.signature.test_signature(
                tokens_mock,
                "",
                message_mock,
                time.time() + 3600,
            )

    async def test_test_signature_success(self):
        """Test test_signature function when successful."""
        message_mock = "abcdefghijklmnopqrstuvwyxz"
        tokens_mock = ["test_token".encode("utf-8")]
        signature = hmac.new(
            "test_token".encode("utf-8"), message_mock.encode("utf-8"), digestmod="sha256"
        ).hexdigest()
        await swift_browser_ui.common.signature.test_signature(
            tokens_mock,
            signature,
            message_mock,
            time.time() + 3600,
        )
