"""Module for testing authentication module."""


import unittest.mock
import hmac
from types import SimpleNamespace
import time


import aiohttp.web
import asynctest


from swift_sharing_request.auth import (
    read_in_keys,
    handle_validate_authentication
)
from swift_sharing_request.auth import test_signature as t_signature


class AuthModuleTestCase(asynctest.TestCase):
    """Class for testing authentication module functions."""

    def setUp(self):
        """Set up necessary mocks."""
        self.app_mock = {}

    async def test_read_in_keys(self):
        """Tets read_in_keys function."""
        os_environ_mock = unittest.mock.Mock(
            return_value="a,b,c,d,e,f"
        )
        os_environ_patch = unittest.mock.patch(
            "swift_sharing_request.auth.os.environ.get",
            new=os_environ_mock
        )
        with os_environ_patch:
            await read_in_keys(self.app_mock)
            os_environ_mock.assert_called_once()
            self.assertIsNotNone(self.app_mock["tokens"])

    async def test_test_signature_failure(self):
        """Test test_signature function when failure."""
        message_mock = "abcdefghijklmnopqrstuvwxyz"
        tokens_mock = []
        with self.assertRaises(aiohttp.web.HTTPUnauthorized):
            await t_signature(
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
            "test_token".encode("utf-8"),
            message_mock.encode("utf-8"),
            digestmod="sha256"
        ).hexdigest()
        await t_signature(
            tokens_mock,
            signature,
            message_mock,
            time.time() + 3600
        )

    async def test_handle_validate_authentication_success(self):
        """Test authentication validation handler success."""
        t_singature_mock = asynctest.CoroutineMock()
        t_signature_patch = unittest.mock.patch(
            "swift_sharing_request.auth.test_signature",
            t_singature_mock
        )

        handler_mock = asynctest.CoroutineMock()
        request_mock = SimpleNamespace(**{
            "app": {
                "tokens": ["awefi"],
            },
            "query": {
                "signature": "a",
                "valid": "b"
            },
            "url": SimpleNamespace(**{
                "path": "c"
            }),
            "match_info": {},
            "path": "/health",
        })

        with t_signature_patch:
            await handle_validate_authentication(
                request_mock,
                handler_mock
            )

    async def test_handle_validate_authentication_failure(self):
        """Test authentication validation handler failure."""
        handler_mock = asynctest.CoroutineMock()
        request_mock = SimpleNamespace(**{
            "query": {
                "signature": "a",
                "vali": "b"
            },
            "url": SimpleNamespace(**{
                "path": "c"
            }),
            "match_info": {},
            "path": "/health",

        })
        with self.assertRaises(aiohttp.web.HTTPClientError):
            await handle_validate_authentication(
                request_mock,
                handler_mock
            )
