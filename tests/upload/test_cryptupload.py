"""Unit tests for swift_browser_ui.upload.cryptupload module."""

import aiohttp.web
import unittest.mock

from swift_browser_ui.upload.cryptupload import FileUpload
from swift_browser_ui.common.vault_client import VaultClient
import tests.common.mockups


class CryptTestClass(tests.common.mockups.APITestBase):
    """Test class for swift_browser_ui.upload.download functions."""

    def setUp(self):
        """Set up mocks."""
        super().setUp()
        self.mock_session = {
            "endpoint": "https://test-endpoint-0/v1/AUTH_test-id",
            "token": "test-token1",
        }
        self.test_header = b"this is a test header"
        self.mock_socket = unittest.mock.AsyncMock(aiohttp.web.WebSocketResponse)
        self.mock_vault = unittest.mock.AsyncMock(VaultClient)

    async def test_add_headers(self):
        """Test adding header for the upload file."""
        proxy = FileUpload(
            self.mock_client,
            self.mock_vault,
            self.mock_session,
            self.mock_socket,
            "test-project",
            "test-container",
            "test-name",
            "test-path",
            100000,
            "",
            "",
        )

        # When container creation fails
        self.mock_client.put = unittest.mock.Mock(side_effect=aiohttp.web.HTTPForbidden)
        with self.assertRaises(aiohttp.web.HTTPForbidden):
            await proxy.add_header(self.test_header)

        # TODO: update cryptupload tests to reflect the new upload implementation
        # alt_client_resp = self.mock_client_response
        # alt_client_resp.status = 204
        # alt_client = self.mock_client
        # alt_client.head = unittest.mock.Mock(
        #     return_value=self.MockHandler(
        #         alt_client_resp,
        #     )
        # )
        # resp = await proxy.add_header(self.test_header)
        # self.assertTrue(proxy.header_uploaded)
        # self.assertEqual(resp.status, 201)
