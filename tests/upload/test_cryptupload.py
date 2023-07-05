"""Unit tests for swift_browser_ui.upload.cryptupload module."""

import aiohttp.web
import unittest.mock

from swift_browser_ui.upload.cryptupload import EncryptedUploadProxy
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

    async def test_add_headers(self):
        """Test adding header for the upload file."""
        proxy = EncryptedUploadProxy(self.mock_session, self.mock_client)
        # When container creation fails
        with self.assertRaises(aiohttp.web.HTTPForbidden):
            await proxy.add_header(self.mock_request)

        alt_client_resp = self.mock_client_response
        alt_client_resp.status = 204
        alt_client = self.mock_client
        alt_client.head = unittest.mock.Mock(
            return_value=self.MockHandler(
                alt_client_resp,
            )
        )
        resp = await proxy.add_header(self.mock_request)
        self.assertTrue(proxy.header_uploaded)
        self.assertEqual(resp.status, 201)
