"""Unit tests for swift_browser_ui.upload.cryptupload module."""

import aiohttp.web
import unittest.mock

from swift_browser_ui.upload.cryptupload import FileUpload, UploadSession

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
        self.file_uploader = FileUpload(
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
        self.upload_session = UploadSession(self.mock_request, self.mock_session)
        self.upload_session.set_ws(self.mock_socket)
        self.msg = {
            "container": "test-container",
            "object": "test-object",
            "name": "test-name",
            "owner": "test-owner",
            "owner_name": "test-owner-name",
            "total": 100000,
            "data": b"",
            "order": 1,
        }
        self.upload_session.uploads["test-container"] = {
            "test-object": self.file_uploader
        }

    async def test_add_headers(self):
        """Test adding header for the upload file."""

        # When container creation fails
        self.mock_client.put = unittest.mock.Mock(side_effect=aiohttp.web.HTTPForbidden)
        with self.assertRaises(aiohttp.web.HTTPForbidden):
            await self.file_uploader.add_header(self.test_header)

        # When container creation succeeds
        alt_client_resp = self.mock_client_response
        alt_client_resp.status = 204
        alt_client = self.mock_client
        alt_client.head = unittest.mock.Mock(
            return_value=self.MockHandler(
                alt_client_resp,
            )
        )

        mock_start = unittest.mock.AsyncMock()
        self.file_uploader.start_upload = mock_start
        await self.file_uploader.add_header(self.test_header)
        self.mock_socket.send_bytes.assert_not_awaited()
        mock_start.assert_awaited_once()

        mock_a_create_container = unittest.mock.AsyncMock(return_value=False)
        self.file_uploader.a_create_container = mock_a_create_container
        await self.file_uploader.add_header(self.test_header)
        self.assertEqual(self.file_uploader.failed, True)
        mock_a_create_container.assert_awaited_once()
        self.mock_socket.send_bytes.assert_awaited_once()

    async def test_add_to_chunks(self):
        """Test adding chunk to cache logic."""
        await self.file_uploader.add_to_chunks(0, b"data")
        self.assertEqual(self.file_uploader.chunk_cache[0], b"data")

        await self.file_uploader.add_to_chunks(0, b"different_data")
        self.assertEqual(self.file_uploader.chunk_cache[0], b"data")

        self.file_uploader.done_chunks.add(1)
        await self.file_uploader.add_to_chunks(1, b"data")
        self.assertEqual(len(self.file_uploader.chunk_cache), 1)

    async def test_slice_into_queue(self):
        """Test slicing segment from queue."""
        for i in range(0, 2):
            self.file_uploader.chunk_cache[i] = b""
        mock_upload_segment = unittest.mock.AsyncMock(return_value=200)
        self.file_uploader.upload_segment = mock_upload_segment
        mock_queue = unittest.mock.AsyncMock()
        mock_queue.put = unittest.mock.AsyncMock(return_value=None)
        await self.file_uploader.slice_into_queue(0, mock_queue)
        mock_queue.put.assert_awaited_with(b"")
        self.assertEqual(self.file_uploader.done_chunks, {0, 1})

        for i in range(81885, 163770):
            self.file_uploader.chunk_cache[i] = b""
        await self.file_uploader.slice_into_queue(1, mock_queue)
        self.assertEqual(len(self.file_uploader.done_chunks), 81887)

    async def test_upload_segment(self):
        """Test uploading segment with given ordering number."""
        self.mock_client_response.status = 201
        self.mock_client.put = unittest.mock.Mock(
            return_value=self.MockHandler(
                self.mock_client_response,
            )
        )

        self.file_uploader.q_cache = ["queue1", "queue2"]
        resp = await self.file_uploader.upload_segment(1)
        self.mock_socket.send_bytes.assert_not_awaited()
        self.assertEqual(resp, 201)

        self.file_uploader.q_cache.pop(1)
        resp = await self.file_uploader.upload_segment(0)
        self.mock_socket.send_bytes.assert_awaited_once()
        self.assertEqual(resp, 201)

    async def test_finish_upload(self):
        """Test finalizing the upload."""
        self.mock_client_response.status = 201
        self.mock_client.put = unittest.mock.Mock(
            return_value=self.MockHandler(
                self.mock_client_response,
            )
        )
        resp = await self.file_uploader.finish_upload()
        self.assertEqual(resp.status, 201)

    async def test_abort_upload(self):
        """Test aborting the upload."""
        self.mock_client_response.status = 204
        self.mock_client.delete = unittest.mock.AsyncMock(
            side_effect=[self.mock_client_response],
        )
        await self.file_uploader.abort_upload()
        self.mock_socket.send_bytes.assert_awaited_once()

    async def test_handle_begin_upload(self):
        """Test upload start handling."""
        mock_ws = unittest.mock.AsyncMock()
        self.upload_session.ws = mock_ws
        await self.upload_session.handle_begin_upload(self.msg)
        mock_ws.send_bytes.assert_awaited_once()
        self.upload_session.ws = self.mock_socket
        self.upload_session.uploads = {}
        await self.upload_session.handle_begin_upload(self.msg)
        assert self.mock_socket.send_bytes.await_count == 2

    async def test_handle_upload_chunk(self):
        """Test addition of a new chunk."""
        await self.upload_session.handle_upload_chunk(self.msg)
        self.assertEqual(
            self.upload_session.uploads["test-container"]["test-object"].chunk_cache,
            {1: b""},
        )

    async def test_handle_finish_upload(self):
        """Test handling the end of upload."""
        await self.upload_session.handle_finish_upload(self.msg)
        self.assertEqual(self.upload_session.uploads, {"test-container": {}})

    async def test_handle_close(self):
        """Test closing ongoing uploads."""
        self.file_uploader.abort_upload = unittest.mock.AsyncMock()
        await self.upload_session.handle_close()
        self.file_uploader.abort_upload.assert_called_once()
