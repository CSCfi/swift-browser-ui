"""Unit tests for swift_browser_ui.upload.api module."""


import types
import unittest.mock

import aiohttp.web
import asynctest.mock

import swift_browser_ui.upload.api

import tests.common.mockups


class APITestClass(asynctest.TestCase):
    """Test class for swift_browser_ui.upload.api functions."""

    def setUp(self) -> None:
        """."""
        self.request = tests.common.mockups.Mock_Request()

        self.mock_get_auth = unittest.mock.Mock(return_value="auth")
        self.patch_get_auth = unittest.mock.patch(
            "swift_browser_ui.upload.api.get_auth_instance", self.mock_get_auth
        )

        self.mock_upload_instance = types.SimpleNamespace(
            **{
                "a_add_chunk": asynctest.mock.CoroutineMock(return_value="add-success"),
                "a_check_segment": asynctest.mock.CoroutineMock(
                    return_value="check-success"
                ),
            }
        )
        self.mock_get_upload_instance = asynctest.mock.CoroutineMock(
            return_value=self.mock_upload_instance
        )
        self.patch_get_upload_instance = unittest.mock.patch(
            "swift_browser_ui.upload.api.get_upload_instance",
            self.mock_get_upload_instance,
        )

        self.mock_response = types.SimpleNamespace(
            **{
                "prepare": asynctest.mock.CoroutineMock(),
                "headers": {},
                "headers": {},
            }
        )
        self.mock_streamresponse_init = unittest.mock.Mock(
            return_value=self.mock_response
        )
        self.patch_streamresponse = unittest.mock.patch(
            "aiohttp.web.StreamResponse", self.mock_streamresponse_init
        )

        self.mock_a_begin = asynctest.mock.CoroutineMock()
        self.mock_a_get_type = asynctest.mock.CoroutineMock(
            return_value="binary/octet-stream"
        )
        self.mock_a_get_size = asynctest.mock.CoroutineMock(return_value="1024")
        self.mock_a_write = asynctest.mock.CoroutineMock()
        self.mock_a_begin_container = asynctest.mock.CoroutineMock()
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

        return super().setUp()

    async def test_handle_get_object(self):
        """Test swift_browser_ui.upload.api.handle_get_object."""
        req = tests.common.mockups.Mock_Request()
        req.set_match(
            {
                "project": "test-project",
                "container": "test-container",
                "object_name": "test-object",
            }
        )

        patch_init_download = unittest.mock.patch(
            "swift_browser_ui.upload.api.FileDownloadProxy",
            self.mock_init_download,
        )

        with patch_init_download, self.patch_get_auth, self.patch_streamresponse:
            resp = await swift_browser_ui.upload.api.handle_get_object(req)

        self.assertIs(resp, self.mock_response)
        self.mock_a_begin.assert_called_once_with(
            "test-project", "test-container", "test-object"
        )
        self.mock_a_get_type.assert_called_once()
        self.mock_a_get_size.assert_called_once()
        self.mock_a_write.assert_called_once_with(resp)

    async def test_handle_replicate_container(self):
        """Test swift_browser_ui.upload.api.handle_replicate_container."""
        mock_copy_from_container = asynctest.mock.CoroutineMock()
        mock_replicator = types.SimpleNamespace(
            **{"a_copy_from_container": mock_copy_from_container}
        )
        mock_init_replicator = unittest.mock.Mock(return_value=mock_replicator)
        patch_replicator = unittest.mock.patch(
            "swift_browser_ui.upload.api.ObjectReplicationProxy", mock_init_replicator
        )

        req = tests.common.mockups.Mock_Request()
        req.set_match({"project": "test-project", "container": "test-container"})
        req.set_query(
            {"from_project": "other-project", "from_container": "source-container"}
        )
        req.app["client"] = "client"

        with self.patch_get_auth, patch_replicator:
            resp = await swift_browser_ui.upload.api.handle_replicate_container(req)

        self.assertIsInstance(resp, aiohttp.web.Response)
        self.assertEqual(resp.status, 202)
        mock_init_replicator.assert_called_once_with(
            "auth",
            "client",
            "test-project",
            "test-container",
            "other-project",
            "source-container",
        )
        mock_copy_from_container.assert_called_once()

    async def test_handle_replicate_object(self):
        """Test swift_brwser_ui.upload.api.handle_replicate_object."""
        mock_copy_object = asynctest.mock.CoroutineMock()
        mock_replicator = types.SimpleNamespace(**{"a_copy_object": mock_copy_object})
        mock_init_replicator = unittest.mock.Mock(return_value=mock_replicator)
        patch_replicator = unittest.mock.patch(
            "swift_browser_ui.upload.api.ObjectReplicationProxy", mock_init_replicator
        )

        req = tests.common.mockups.Mock_Request()
        req.set_match({"project": "test-project", "container": "test-container"})
        req.set_query(
            {
                "from_project": "other-project",
                "from_container": "source-container",
                "from_object": "source-object",
            }
        )
        req.app["client"] = "client"

        with self.patch_get_auth, patch_replicator:
            resp = await swift_browser_ui.upload.api.handle_replicate_object(req)

        self.assertIsInstance(resp, aiohttp.web.Response)
        self.assertEqual(resp.status, 202)
        mock_init_replicator.assert_called_once_with(
            "auth",
            "client",
            "test-project",
            "test-container",
            "other-project",
            "source-container",
        )
        mock_copy_object.assert_called_once_with("source-object")

    async def test_handle_post_object_chunk(self):
        """Test swift_browser_ui.upload.api.handle_post_object_chunk."""
        # Test for the edge cases of rerouted POST
        mock_handle_repl_object = asynctest.mock.CoroutineMock(
            return_value=aiohttp.web.Response()
        )
        patch_handle_repl_object = unittest.mock.patch(
            "swift_browser_ui.upload.api.handle_replicate_object", mock_handle_repl_object
        )
        mock_handle_repl_container = asynctest.mock.CoroutineMock(
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
        mock_parse_multipart_in = asynctest.mock.CoroutineMock(
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

        with self.assertRaises(aiohttp.web.HTTPBadRequest), self.patch_get_auth:
            await swift_browser_ui.upload.api.handle_get_object_chunk(req)

        req.set_query({"resumableChunkNumber": 100})

        with self.patch_get_auth, self.patch_get_upload_instance:
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
        req = tests.common.mockups.Mock_Request()
        req.set_query({"resumableChunkNumber": 1})
        mock_get_object_chunk = asynctest.mock.CoroutineMock(
            return_value="get-chunk-success"
        )
        patch_get_object_chunk = unittest.mock.patch(
            "swift_browser_ui.upload.api.handle_get_object_chunk", mock_get_object_chunk
        )
        with patch_get_object_chunk:
            resp = await swift_browser_ui.upload.api.handle_get_container(req)
        self.assertEqual(resp, "get-chunk-success")

        # Test normal behaviour
        req = tests.common.mockups.Mock_Request()
        req.set_match({"project": "test-project", "container": "test-container"})

        patch_init_download = unittest.mock.patch(
            "swift_browser_ui.upload.api.ContainerArchiveDownloadProxy",
            self.mock_init_download,
        )

        with self.patch_get_auth, self.patch_streamresponse, patch_init_download:
            resp = await swift_browser_ui.upload.api.handle_get_container(req)

        self.assertIs(resp, self.mock_response)
        self.mock_download.a_write_to_response.assert_called_once()
        self.mock_init_download.assert_called_once_with(
            "auth", "test-project", "test-container"
        )
        self.assertEqual(resp.headers["Content-Type"], "application/x-tar")
        self.assertIsNotNone(resp.headers["Content-Disposition"])

    async def test_handle_health_check(self):
        """Test swift_browser_ui.upload.api.handle_health_check."""
        resp = await swift_browser_ui.upload.api.handle_health_check(
            tests.common.mockups.Mock_Request()
        )
        self.assertIsInstance(resp, aiohttp.web.Response)
