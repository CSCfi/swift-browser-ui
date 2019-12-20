"""Module for testing the bindings module / class."""


import unittest.mock
from types import SimpleNamespace


import asynctest


from swift_x_account_sharing.bindings.bind import SwiftXAccountSharing


class MockRequestContextManager:
    """Mock class for aiohttp request context manager."""

    def __init__(self, *args, **kwargs):
        """."""

    async def __aenter__(self, *args, **kwargs):
        """."""
        return SimpleNamespace(**{
            "text": asynctest.CoroutineMock(
                return_value="[]"
            ),
            "status": 204
        })

    async def __aexit__(self, *excinfo):
        """."""


class BindingsClassTestCase(asynctest.TestCase):
    """Bindings class test case."""

    def setUp(self):
        """Set up relevant mocks."""
        self.session_mock = SimpleNamespace(**{
            "close": asynctest.CoroutineMock(),
            "get": MockRequestContextManager,
            "post": MockRequestContextManager,
            "patch": MockRequestContextManager,
            "delete": MockRequestContextManager,
        })
        self.session_open_mock = unittest.mock.Mock(
            return_value=self.session_mock
        )
        self.session_open_patch = unittest.mock.patch(
            "swift_x_account_sharing.bindings.bind.aiohttp.ClientSession",
            new=self.session_open_mock
        )

        self.signature_mock = unittest.mock.Mock(
            return_value={"valid": "60", "signature": "example"}
        )
        self.patch_signature = unittest.mock.patch(
            "swift_x_account_sharing.bindings.bind.sign_api_request",
            new=self.signature_mock
        )

    async def test_parse_list_to_string(self):
        """Test parsing lists to string as a comma separated values."""
        to_parse = ["a", "b", "c", "d"]
        ret = SwiftXAccountSharing.parse_list_to_string(to_parse)
        self.assertEqual(ret, "a,b,c,d")

    async def test_get_access(self):
        """Test get_access API binding."""
        with self.patch_signature, self.session_open_patch:
            async with SwiftXAccountSharing("http://example") as client:
                await client.get_access("test-user")

    async def test_get_access_details(self):
        """Test get_access_details API binding."""
        with self.patch_signature, self.session_open_patch:
            async with SwiftXAccountSharing("http://example") as client:
                await client.get_access_details(
                    "test-user",
                    "test-container",
                    "test-owner"
                )

    async def test_get_share(self):
        """Test get_share API binding."""
        with self.patch_signature, self.session_open_patch:
            async with SwiftXAccountSharing("http://example") as client:
                await client.get_share("test-user")

    async def test_get_share_details(self):
        """Test get_share_details API binding."""
        with self.patch_signature, self.session_open_patch:
            async with SwiftXAccountSharing("http://example") as client:
                await client.get_share_details(
                    "test-user",
                    "test-container"
                )

    async def test_share_new_access(self):
        """Test share_new_access API binding."""
        with self.patch_signature, self.session_open_patch:
            async with SwiftXAccountSharing("http://example") as client:
                await client.share_new_access(
                    "test-user",
                    "test-container",
                    ["test-user1", "test-user2", "test-user3"],
                    ["r", "s"],
                    "http://example"
                )

    async def test_share_edit_access(self):
        """Test share_edit_access API binding."""
        with self.patch_signature, self.session_open_patch:
            async with SwiftXAccountSharing("http://example") as client:
                await client.share_edit_access(
                    "test-user",
                    "test-container",
                    ["test-user1", "test-user2", "test-user3"],
                    ["r", "s"],
                )

    async def test_share_delete_access(self):
        """Test share_delete_access API binding."""
        with self.patch_signature, self.session_open_patch:
            async with SwiftXAccountSharing("http://example") as client:
                await client.share_delete_access(
                    "test-user",
                    "test-container",
                    ["test-user1", "test-user2", "test-user3"],
                )
