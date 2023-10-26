"""Unit tests for swift_browser_ui.upload.api module."""


import json
import types
import unittest

import aiohttp.web

import swift_browser_ui.upload.api
from swift_browser_ui.upload.common import VAULT_CLIENT

import tests.common.mockups


class APITestClass(tests.common.mockups.APITestBase):
    """Test class for swift_browser_ui.upload.api functions."""

    def setUp(self) -> None:
        """."""
        super().setUp()
        self.mock_get_session_id = unittest.mock.Mock(
            return_value="test-id",
        )
        self.p_get_sess = unittest.mock.patch(
            "swift_browser_ui.upload.api.get_session_id", self.mock_get_session_id
        )

        self.mock_upload_instance = types.SimpleNamespace(
            **{
                "a_add_chunk": unittest.mock.AsyncMock(return_value="add-success"),
                "a_check_segment": unittest.mock.AsyncMock(return_value="check-success"),
            }
        )
        self.mock_get_upload_instance = unittest.mock.AsyncMock(
            return_value=self.mock_upload_instance
        )
        self.patch_get_upload_instance = unittest.mock.patch(
            "swift_browser_ui.upload.api.get_upload_instance",
            self.mock_get_upload_instance,
        )

        self.mock_response = types.SimpleNamespace(
            **{
                "prepare": unittest.mock.AsyncMock(),
                "headers": {},
            }
        )
        self.mock_streamresponse_init = unittest.mock.Mock(
            return_value=self.mock_response
        )
        self.patch_streamresponse = unittest.mock.patch(
            "aiohttp.web.StreamResponse", self.mock_streamresponse_init
        )

        self.mock_a_begin = unittest.mock.AsyncMock()
        self.mock_a_get_type = unittest.mock.AsyncMock(return_value="binary/octet-stream")
        self.mock_a_get_size = unittest.mock.AsyncMock(return_value="1024")
        self.mock_a_write = unittest.mock.AsyncMock()
        self.mock_a_begin_container = unittest.mock.AsyncMock()
        self.mock_download = types.SimpleNamespace(
            **{
                "a_begin_download": self.mock_a_begin,
                "a_begin_container_download": self.mock_a_begin_container,
                "a_get_type": self.mock_a_get_type,
                "a_get_size": self.mock_a_get_size,
                "a_write_to_response": self.mock_a_write,
            }
        )
        self.mock_init_download = unittest.mock.Mock(return_value=self.mock_download)

    async def test_handle_get_object(self):
        """Test swift_browser_ui.upload.api.handle_get_object."""
        self.mock_request.match_info["project"] = "test-project"
        self.mock_request.match_info["container"] = "test-container"
        self.mock_request.match_info["object_name"] = "test-object"

        patch_init_download = unittest.mock.patch(
            "swift_browser_ui.upload.api.FileDownloadProxy",
            self.mock_init_download,
        )

        with patch_init_download, self.p_get_sess, self.patch_streamresponse:
            resp = await swift_browser_ui.upload.api.handle_get_object(self.mock_request)

        self.assertIs(resp, self.mock_response)
        self.mock_a_begin.assert_called_once_with(
            "test-project", "test-container", "test-object"
        )
        self.mock_a_get_type.assert_called_once()
        self.mock_a_get_size.assert_called_once()
        self.mock_a_write.assert_called_once_with(resp)

    async def test_handle_replicate_container(self):
        """Test swift_browser_ui.upload.api.handle_replicate_container."""
        mock_copy_from_container = unittest.mock.AsyncMock()
        mock_ensure_container = unittest.mock.AsyncMock()
        mock_replicator = types.SimpleNamespace(
            **{
                "a_copy_from_container": mock_copy_from_container,
                "a_ensure_container": mock_ensure_container,
            }
        )
        mock_init_replicator = unittest.mock.Mock(return_value=mock_replicator)
        patch_replicator = unittest.mock.patch(
            "swift_browser_ui.upload.api.ObjectReplicationProxy", mock_init_replicator
        )

        self.mock_request.query["from_project"] = "other-project"
        self.mock_request.query["from_container"] = "source-container"
        self.mock_request.match_info["project"] = "test-project"
        self.mock_request.match_info["container"] = "test-container"

        mock_vault_client = unittest.mock.Mock()
        self.mock_request.app[VAULT_CLIENT] = mock_vault_client

        with self.p_get_sess, patch_replicator:
            resp = await swift_browser_ui.upload.api.handle_replicate_container(
                self.mock_request,
            )

        self.assertIsInstance(resp, aiohttp.web.Response)
        self.assertEqual(resp.status, 202)
        mock_init_replicator.assert_called_once_with(
            "placeholder",
            self.mock_client,
            mock_vault_client,
            "test-project",
            "test-container",
            "other-project",
            "source-container",
            "",
            "",
        )
        mock_copy_from_container.assert_called_once()
        mock_ensure_container.assert_called()

    async def test_handle_replicate_object(self):
        """Test swift_brwser_ui.upload.api.handle_replicate_object."""
        mock_copy_object = unittest.mock.AsyncMock()
        mock_ensure_container = unittest.mock.AsyncMock()
        mock_replicator = types.SimpleNamespace(
            **{
                "a_copy_single_object": mock_copy_object,
                "a_ensure_container": mock_ensure_container,
            }
        )
        mock_init_replicator = unittest.mock.Mock(return_value=mock_replicator)
        patch_replicator = unittest.mock.patch(
            "swift_browser_ui.upload.api.ObjectReplicationProxy", mock_init_replicator
        )

        self.mock_request.match_info["project"] = "test-project"
        self.mock_request.match_info["container"] = "test-container"
        self.mock_request.query["from_project"] = "other-project"
        self.mock_request.query["from_container"] = "source-container"
        self.mock_request.query["from_object"] = "source-object"

        mock_vault_client = unittest.mock.Mock()
        self.mock_request.app[VAULT_CLIENT] = mock_vault_client

        with self.p_get_sess, patch_replicator:
            resp = await swift_browser_ui.upload.api.handle_replicate_object(
                self.mock_request,
            )

        self.assertIsInstance(resp, aiohttp.web.Response)
        self.assertEqual(resp.status, 202)
        mock_init_replicator.assert_called_once_with(
            "placeholder",
            self.mock_client,
            mock_vault_client,
            "test-project",
            "test-container",
            "other-project",
            "source-container",
            "",
            "",
        )
        mock_copy_object.assert_called_once_with("source-object")
        mock_ensure_container.assert_called()

    async def test_handle_post_object_chunk(self):
        """Test swift_browser_ui.upload.api.handle_post_object_chunk."""
        # Test for the edge cases of rerouted POST
        mock_handle_repl_object = unittest.mock.AsyncMock(
            return_value=aiohttp.web.Response()
        )
        patch_handle_repl_object = unittest.mock.patch(
            "swift_browser_ui.upload.api.handle_replicate_object", mock_handle_repl_object
        )
        mock_handle_repl_container = unittest.mock.AsyncMock(
            return_value=aiohttp.web.Response()
        )
        patch_handle_repl_container = unittest.mock.patch(
            "swift_browser_ui.upload.api.handle_replicate_container",
            mock_handle_repl_container,
        )

        req = tests.common.mockups.Mock_Request()
        req.set_query({"from_object": "source-object"})
        with patch_handle_repl_object:
            await swift_browser_ui.upload.api.handle_post_object_chunk(req)
        mock_handle_repl_object.assert_called_once()
        req = tests.common.mockups.Mock_Request()
        req.set_query({"from_container": "source-container"})
        with patch_handle_repl_container:
            await swift_browser_ui.upload.api.handle_post_object_chunk(req)
        mock_handle_repl_container.assert_called_once()

        # The actual test for uploaded object chunk post
        mock_parse_multipart_in = unittest.mock.AsyncMock(
            return_value=("example-query", "example-data")
        )
        patch_parse_multipart_in = unittest.mock.patch(
            "swift_browser_ui.upload.api.parse_multipart_in", mock_parse_multipart_in
        )

        req = tests.common.mockups.Mock_Request()
        req.set_match({"project": "test-project", "container": "test-container"})

        with patch_parse_multipart_in, self.patch_get_upload_instance:
            resp = await swift_browser_ui.upload.api.handle_post_object_chunk(req)

        self.assertEqual(resp, "add-success")
        mock_parse_multipart_in.assert_called_once()
        self.mock_get_upload_instance.assert_called_once()
        self.mock_upload_instance.a_add_chunk.assert_called_once_with(
            "example-query", "example-data"
        )

    async def test_handle_get_object_chunk(self):
        """Test swift_browser_ui.upload.api.handle_get_object_chunk."""
        req = tests.common.mockups.Mock_Request()
        req.set_match({"project": "test-project", "container": "test-container"})

        with self.assertRaises(aiohttp.web.HTTPBadRequest), self.p_get_sess:
            await swift_browser_ui.upload.api.handle_get_object_chunk(req)

        req.set_query({"resumableChunkNumber": 100})

        with self.p_get_sess, self.patch_get_upload_instance:
            resp = await swift_browser_ui.upload.api.handle_get_object_chunk(req)

        self.assertEqual(resp, "check-success")
        self.mock_upload_instance.a_check_segment.assert_called_once_with(99)

    async def test_handle_post_object_options(self):
        """Test swift_browser_ui.upload.api.handle_post_object_options."""
        resp = await swift_browser_ui.upload.api.handle_post_object_options(None)
        self.assertIsInstance(resp, aiohttp.web.Response)
        self.assertIn("Access-Control-Allow-Methods", resp.headers)
        self.assertIn("Access-Control-Max-Age", resp.headers)

    async def test_handle_get_container(self):
        """Test swift_browser_ui.upload.api.handle_get_container."""
        # Handle edge case of uploaded object chunk check
        self.mock_request.match_info["project"] = "test-project"
        self.mock_request.match_info["container"] = "test-container"
        self.mock_request.query["resumableChunkNumber"] = 1

        mock_get_object_chunk = unittest.mock.AsyncMock(return_value="get-chunk-success")
        patch_get_object_chunk = unittest.mock.patch(
            "swift_browser_ui.upload.api.handle_get_object_chunk", mock_get_object_chunk
        )
        with patch_get_object_chunk:
            resp = await swift_browser_ui.upload.api.handle_get_container(
                self.mock_request,
            )
        self.assertEqual(resp, "get-chunk-success")

        # Test normal behaviour
        self.mock_request.query.pop("resumableChunkNumber")
        patch_init_download = unittest.mock.patch(
            "swift_browser_ui.upload.api.ContainerArchiveDownloadProxy",
            self.mock_init_download,
        )

        with self.p_get_sess, self.patch_streamresponse, patch_init_download:
            resp = await swift_browser_ui.upload.api.handle_get_container(
                self.mock_request,
            )

        self.assertIs(resp, self.mock_response)
        self.mock_download.a_write_to_response.assert_called_once()
        self.mock_init_download.assert_called_once_with(
            "placeholder", "test-project", "test-container"
        )
        self.assertEqual(resp.headers["Content-Type"], "application/x-tar")
        self.assertIsNotNone(resp.headers["Content-Disposition"])

    async def test_handle_health_check(self):
        """Test swift_browser_ui.upload.api.handle_health_check."""
        mock_vault_client = unittest.mock.Mock()
        mock_vault_client.get_sys_health = unittest.mock.AsyncMock(return_value="Ok")
        self.mock_request.app[VAULT_CLIENT] = mock_vault_client

        resp = await swift_browser_ui.upload.api.handle_health_check(self.mock_request)
        self.assertIsInstance(resp, aiohttp.web.Response)
        self.assertEqual(resp.status, 200)
        resp_json = json.loads(resp.body)
        self.assertEqual(resp_json["vault-instance"]["status"], "Ok")

    async def test_handle_project_key(self):
        """Test swift_browser_ui.upload.api.handle_project_key."""
        mock_vault_client = unittest.mock.Mock()
        mock_vault_client.get_public_key = unittest.mock.AsyncMock(
            return_value="test-key"
        )
        self.mock_request.app[VAULT_CLIENT] = mock_vault_client

        resp = await swift_browser_ui.upload.api.handle_project_key(self.mock_request)
        self.assertIsInstance(resp, aiohttp.web.Response)
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.text, "test-key")

    async def test_handle_object_header(self):
        """Test swift_browser_ui.upload.api.handle_object_header."""
        mock_vault_client = unittest.mock.Mock()
        mock_vault_client.get_header = unittest.mock.AsyncMock(return_value="test-header")
        self.mock_request.app[VAULT_CLIENT] = mock_vault_client

        resp = await swift_browser_ui.upload.api.handle_object_header(self.mock_request)
        self.assertIsInstance(resp, aiohttp.web.Response)
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.text, "test-header")

        self.mock_request.query["owner"] = "test-owner"
        resp = await swift_browser_ui.upload.api.handle_object_header(self.mock_request)
        self.assertIsInstance(resp, aiohttp.web.Response)
        mock_vault_client.get_header.assert_called_with(
            "test-id-0", "test-container", "test-object1", "test-owner"
        )

    async def test_handle_project_whitelist(self):
        """Test swift_browser_ui.upload.api.handle_project_whitelist."""
        mock_vault_client = unittest.mock.Mock()
        mock_vault_client.put_whitelist_key = unittest.mock.AsyncMock()
        self.mock_request.app[VAULT_CLIENT] = mock_vault_client

        resp = await swift_browser_ui.upload.api.handle_project_whitelist(
            self.mock_request
        )
        self.assertIsInstance(resp, aiohttp.web.Response)
        self.assertEqual(resp.status, 204)

    async def test_handle_delete_project_whitelist(self):
        """Test swift_browser_ui.upload.api.handle_delete_project_whitelist."""
        mock_vault_client = unittest.mock.Mock()
        mock_vault_client.remove_whitelist_key = unittest.mock.AsyncMock()
        self.mock_request.app[VAULT_CLIENT] = mock_vault_client

        resp = await swift_browser_ui.upload.api.handle_delete_project_whitelist(
            self.mock_request
        )
        self.assertIsInstance(resp, aiohttp.web.Response)
        self.assertEqual(resp.status, 204)

    async def test_handle_batch_add_sharing_whitelist(self):
        """Test swift_browser_ui.upload.api.handle_batch_add_sharing_whitelist."""
        mock_vault_client = unittest.mock.Mock()
        mock_vault_client.put_project_whitelist = unittest.mock.AsyncMock()
        self.mock_request.app[VAULT_CLIENT] = mock_vault_client
        self.mock_request.json = unittest.mock.AsyncMock(
            return_value=[{"name": "name", "id": "1"}]
        )

        resp = await swift_browser_ui.upload.api.handle_batch_add_sharing_whitelist(
            self.mock_request
        )
        self.assertIsInstance(resp, aiohttp.web.Response)
        self.assertEqual(resp.status, 204)
        mock_vault_client.put_project_whitelist.assert_called_with(
            "test-id-0", "name", "test-container", "1"
        )

    async def test_handle_batch_remove_sharing_whitelist(self):
        """Test swift_browser_ui.upload.api.handle_batch_remove_sharing_whitelist."""
        mock_vault_client = unittest.mock.Mock()
        mock_vault_client.remove_project_whitelist = unittest.mock.AsyncMock()
        self.mock_request.app[VAULT_CLIENT] = mock_vault_client
        self.mock_request.json = unittest.mock.AsyncMock(
            return_value=[{"name": "name", "id": "1"}]
        )

        resp = await swift_browser_ui.upload.api.handle_batch_remove_sharing_whitelist(
            self.mock_request
        )
        self.assertIsInstance(resp, aiohttp.web.Response)
        self.assertEqual(resp.status, 204)
        mock_vault_client.remove_project_whitelist.assert_called_with(
            "test-id-0", {"name": "name", "id": "1"}, "test-container"
        )

    async def test_handle_check_sharing_whitelist(self):
        """Test swift_browser_ui.upload.api.handle_check_sharing_whitelist."""
        mock_vault_client = unittest.mock.Mock()
        mock_vault_client.get_project_whitelist = unittest.mock.AsyncMock(
            return_value=None
        )
        self.mock_request.app[VAULT_CLIENT] = mock_vault_client
        resp = await swift_browser_ui.upload.api.handle_check_sharing_whitelist(
            self.mock_request
        )
        self.assertIsInstance(resp, aiohttp.web.Response)
        self.assertEqual(resp.status, 204)

        mock_vault_client.get_project_whitelist = unittest.mock.AsyncMock(return_value={})
        self.mock_request.app[VAULT_CLIENT] = mock_vault_client
        resp = await swift_browser_ui.upload.api.handle_check_sharing_whitelist(
            self.mock_request
        )
        self.assertIsInstance(resp, aiohttp.web.Response)
        self.assertEqual(resp.text, "{}")
