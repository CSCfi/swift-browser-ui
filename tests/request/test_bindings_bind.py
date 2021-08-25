"""Module for testing the bindings module / class."""


import unittest.mock
from types import SimpleNamespace


import asynctest


from swift_browser_ui.request.bindings.bind import SwiftSharingRequest


class MockRequestContextManager(asynctest.TestCase):
    """Mock class for aiohttp request context manager."""

    def __init__(self, *args, **kwargs):
        """."""
        self.resp = SimpleNamespace(
            **{"text": asynctest.CoroutineMock(return_value="[]"), "status": 200}
        )

    async def __aenter__(self, *args, **kwargs):
        """."""
        return self.resp


class MockGenericContextManager(MockRequestContextManager):
    """Mock class for aiohttp context manager."""

    def __init__(self, *args, **kwargs):
        """."""
        super(MockGenericContextManager, self).__init__(self, *args, **kwargs)

    async def __aexit__(self, *excinfo):
        """Perform assertions done upon exit."""
        self.resp.text.assert_awaited()


# Delete method mock context manager won't have any assertions in the
# __aexit__ method, since there's no real assertable functionality.
# Functionality will be tested in integration testing.
class MockDeleteContextManager(MockRequestContextManager):
    """Mock class for aiohttp delete context manager."""

    def __init__(self, *args, **kwargs):
        """."""
        super(MockDeleteContextManager, self).__init__(self, *args, **kwargs)

    async def __aexit__(self, *excinfo):
        """."""


class BindingsClassTestCase(asynctest.TestCase):
    """Bindings class test case."""

    def setUp(self):
        """Set up relevant mocks."""
        self.session_mock = SimpleNamespace(
            **{
                "close": asynctest.CoroutineMock(),
                "get": MockGenericContextManager,
                "post": MockGenericContextManager,
                "delete": MockDeleteContextManager,
            }
        )
        self.session_open_mock = unittest.mock.Mock(return_value=self.session_mock)
        self.session_open_patch = unittest.mock.patch(
            "swift_browser_ui.request.bindings.bind.aiohttp.ClientSession",
            new=self.session_open_mock,
        )

        self.signature_mock = unittest.mock.Mock(
            return_value={"valid": "60", "signature": "example"}
        )
        self.patch_signature = unittest.mock.patch(
            "swift_browser_ui.common.signature.sign_api_request",
            new=self.signature_mock,
        )

    async def test_add_access_request(self):
        """Test add_access_request API binding."""
        with self.patch_signature, self.session_open_patch:
            async with SwiftSharingRequest("http://example") as client:
                await client.add_access_request(
                    "test-user", "test-container", "test-woner"
                )

    async def test_list_made_requests(self):
        """Test list_made_requests API binding."""
        with self.patch_signature, self.session_open_patch:
            async with SwiftSharingRequest("http://example") as client:
                await client.list_made_requests("test-user")

    async def test_list_owned_requests(self):
        """Test list_owned_requests API binding."""
        with self.patch_signature, self.session_open_patch:
            async with SwiftSharingRequest("http://example") as client:
                await client.list_owned_requests(
                    "test-user",
                )

    async def test_list_container_requests(self):
        """Test get_share API binding."""
        with self.patch_signature, self.session_open_patch:
            async with SwiftSharingRequest("http://example") as client:
                await client.list_container_requests(
                    "test-container",
                )

    async def test_share_delete_access(self):
        """Test share_delete_access API binding."""
        with self.patch_signature, self.session_open_patch:
            async with SwiftSharingRequest("http://example") as client:
                await client.share_delete_access(
                    "test-user",
                    "test-container",
                    "test-owner",
                )
