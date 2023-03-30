"""Unit tests for swift_browser_ui.upload.upload module."""

import unittest.mock

import aiohttp.web

from swift_browser_ui.upload.upload import ResumableFileUploadProxy
import tests.common.mockups


class UploadTestClass(tests.common.mockups.APITestBase):
    """Test class for swift_browser_ui.upload.upload functions."""

    def setUp(self):
        """Set up mocks."""
        super().setUp()
        self.mock_session = {
            "endpoint": "https://test-endpoint-0/v1/AUTH_test-id",
            "token": "test-token",
        }
        self.mock_query = {
            "resumableChunkSize": 0,
            "resumableTotalSize": 9999999999,
            "resumableChunkNumber": 10,
            "resumableTotalChunks": 10,
            "resumableType": "",
            "resumableIdentifier": "",
            "resumableFilename": "",
            "resumableRelativePath": "",
        }
        self.file_upload_proxy = ResumableFileUploadProxy(
            self.mock_session,
            self.mock_query,
            self.mock_request.match_info,
            self.mock_client,
        )

    async def test_create_container(self):
        """Test creating a container for an upload."""
        self.mock_client_response.status = 200
        with self.assertRaises(aiohttp.web.HTTPForbidden):
            await self.file_upload_proxy.a_create_container()
        self.mock_client.head.assert_called_once()
        self.mock_client.put.assert_called_once()
        self.mock_client.head.reset_mock()
        self.mock_client.put.reset_mock()

        self.mock_client_response.status = 201
        await self.file_upload_proxy.a_create_container()
        self.assertEqual(self.mock_client.head.call_count, 2)
        self.assertEqual(self.mock_client.put.call_count, 2)

    async def test_check_container(self):
        """Test checking if container is allowed."""
        with self.assertRaises(aiohttp.web.HTTPBadRequest):
            await self.file_upload_proxy.a_check_container()
        self.mock_client.head.assert_called_once()
        self.mock_client.head.reset_mock()

        self.mock_client_response.status = 201
        match_info = {
            "project": "AUTH_test-id",
            "container": "test-container",
        }
        new_proxy = ResumableFileUploadProxy(
            self.mock_session,
            self.mock_query,
            match_info,
            self.mock_client,
        )
        await new_proxy.a_check_container()
        self.assertEqual(self.mock_client.head.call_count, 3)

    async def test_check_segment(self):
        """Test checking existence of a segment."""
        resp = await self.file_upload_proxy.a_check_segment(1)
        self.mock_client.head.assert_called_once()
        self.mock_client.head.reset_mock()
        self.assertEqual(resp.status, 200)

        self.mock_client_response.status = 204
        resp = await self.file_upload_proxy.a_check_segment(1)
        self.mock_client.head.assert_called_once()
        self.assertEqual(resp.status, 204)

    async def test_add_manifest(self):
        """Test adding manifest file."""
        with self.assertRaises(aiohttp.web.HTTPBadRequest):
            await self.file_upload_proxy.a_add_manifest()
        self.mock_client.put.assert_called_once()
        self.mock_client.put.reset_mock()

        self.mock_client_response.status = 201
        await self.file_upload_proxy.a_add_manifest()
        self.mock_client.put.assert_called_once()

    async def test_add_chunk(self):
        """Test adding chunk."""
        self.mock_chunk_reader = unittest.mock.Mock()
        self.file_upload_proxy.upload_file = unittest.mock.AsyncMock()
        self.patch_coro_upload = unittest.mock.patch(
            "swift_browser_ui.upload.upload.ResumableFileUploadProxy.upload_file",
            self.file_upload_proxy.upload_file,
        )

        self.file_upload_proxy.done_chunks = {9}
        resp = await self.file_upload_proxy.a_add_chunk(
            self.mock_query, self.mock_chunk_reader
        )
        self.assertEqual(resp.status, 200)

        self.file_upload_proxy.done_chunks = {}
        resp = await self.file_upload_proxy.a_add_chunk(
            self.mock_query, self.mock_chunk_reader
        )
        self.file_upload_proxy.upload_file.assert_awaited_once()
        self.assertEqual(resp.status, 201)

    async def test_upload_file(self):
        """Test uploading non-segmented file."""
        self.file_upload_proxy.segmented = False
        await self.file_upload_proxy.upload_file()
        self.mock_client.put.assert_called_once()
        self.mock_client_response.status = 408
        with self.assertRaises(aiohttp.web.HTTPRequestTimeout):
            await self.file_upload_proxy.upload_file()
        self.mock_client_response.status = 411
        with self.assertRaises(aiohttp.web.HTTPLengthRequired):
            await self.file_upload_proxy.upload_file()
        self.mock_client_response.status = 422
        with self.assertRaises(aiohttp.web.HTTPUnprocessableEntity):
            await self.file_upload_proxy.upload_file()

    async def test_wait_for_chunk(self):
        """Test the method doesn't get stuck in an infinite loop."""
        self.file_upload_proxy.done_chunks = {1}
        await self.file_upload_proxy.a_wait_for_chunk(1)
