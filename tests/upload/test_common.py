"""Unit tests for swift_browser_ui.upload.common module."""


import unittest

import aiohttp

import swift_browser_ui.upload.common

import tests.common.mockups


class CommonTestClass(unittest.IsolatedAsyncioTestCase):
    """Test class for testing swift_browser_ui.upload.common functions."""

    def setUp(self):
        super().setUp()

    async def test_generate_download_url(self):
        """Test generate_download_url function."""
        self.assertEqual(
            "test_host",
            swift_browser_ui.upload.common.generate_download_url("test_host"),
        )
        self.assertEqual(
            "test_host/test_container",
            swift_browser_ui.upload.common.generate_download_url(
                "test_host", container="test_container"
            ),
        )
        self.assertEqual(
            "test_host/test_container/test_object",
            swift_browser_ui.upload.common.generate_download_url(
                "test_host",
                container="test_container",
                object_name="test_object",
            ),
        )

    async def test_get_download_host(self):
        """Test get_download_host function."""
        auth = tests.common.mockups.Mock_Session()

        ret = swift_browser_ui.upload.common.get_download_host(auth, "AUTH_testproject")

        self.assertIn("AUTH_testproject", ret)

    async def test_get_session_id(self):
        """Test get_session_id function."""
        req = tests.common.mockups.Mock_Request()

        # Test fetching when session id is not present
        with self.assertRaises(aiohttp.web.HTTPUnauthorized):
            swift_browser_ui.upload.common.get_session_id(req)

        # Test fetching when session id is in query string
        req.set_query(
            {
                "session": "test_session_query",
            }
        )
        self.assertEqual(
            "test_session_query", swift_browser_ui.upload.common.get_session_id(req)
        )

        # Test fetching when session id is in cookies
        req.set_cookies({"RUNNER_SESSION_ID": "test_session_cookie"})
        self.assertEqual(
            "test_session_cookie", swift_browser_ui.upload.common.get_session_id(req)
        )

    async def test_get_upload_instance(self):
        """Test get_upload_instance function."""
        mock_upload = unittest.mock.create_autospec(
            swift_browser_ui.upload.common.upload.ResumableFileUploadProxy
        )
        patch_upload = unittest.mock.patch(
            "swift_browser_ui.upload.common.upload.ResumableFileUploadProxy", mock_upload
        )

        req = tests.common.mockups.Mock_Request()
        req.app["client"] = None
        req.app["test-session"] = {}
        req.app["test-session"]["uploads"] = {}
        req.app["test-session"]["auth"] = tests.common.mockups.Mock_Session()
        req.set_query({"session": "test-session"})

        query = {
            "resumableIdentifier": "test-identifier",
        }

        with patch_upload:
            with self.assertRaises(aiohttp.web.HTTPBadRequest):
                await swift_browser_ui.upload.common.get_upload_instance(
                    req, "test-project", "test-container"
                )

        with patch_upload:
            ret = await swift_browser_ui.upload.common.get_upload_instance(
                req, "test-project", "test-container", p_query=query
            )
        self.assertIn("test-project", req.app["test-session"]["uploads"].keys())
        self.assertIn(
            "test-container", req.app["test-session"]["uploads"]["test-project"].keys()
        )
        self.assertIsNotNone(ret)

        req.set_query(query)
        with patch_upload:
            ret = await swift_browser_ui.upload.common.get_upload_instance(
                req, "test-project", "test-container"
            )
        self.assertIsNotNone(ret)

    async def test_get_path_from_list(self):
        """Test get_path_from_list function."""
        path = swift_browser_ui.upload.common.get_path_from_list(
            [
                "folder_a",
                "folder_b",
                "folder_c",
            ],
            "",
        )
        self.assertEqual(
            path,
            "folder_a/folder_b/folder_c",
        )
