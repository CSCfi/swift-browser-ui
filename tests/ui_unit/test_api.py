"""Module for testing ``swift_browser_ui.ui.api``."""

import json
import unittest
import types

import aiohttp.web

import tests.common.mockups
import swift_browser_ui.ui.api


class APITestClass(tests.common.mockups.APITestBase):
    """Test the Object Browser API."""

    def setUp(self):
        """Set up mocks."""
        super().setUp()

    async def test_get_os_user(self):
        """Test session Openstack username fetch."""
        with self.p_get_sess, self.p_json_resp:
            await swift_browser_ui.ui.api.get_os_user(self.mock_request)
        self.aiohttp_json_response_mock.assert_called_once_with("testuser")

    async def test_os_list_projects(self):
        """Test Openstack available project scope fetch."""
        with self.p_get_sess, self.p_json_resp:
            await swift_browser_ui.ui.api.os_list_projects(
                self.mock_request,
            )
        self.aiohttp_json_response_mock.assert_called_once_with(
            [
                {
                    "id": "test-id-0",
                    "title": "",
                    "name": "test-name-0",
                    "tainted": False,
                },
                {
                    "id": "test-id-1",
                    "title": "",
                    "name": "test-name-1",
                    "tainted": False,
                },
            ]
        )

    async def test_swift_list_containers(self):
        """Test container listing fetch from Openstack."""
        mock_check = unittest.mock.AsyncMock(return_value={})
        patch_mock_check = unittest.mock.patch(
            "swift_browser_ui.ui.api._check_last_modified", mock_check
        )
        with self.p_get_sess, self.p_sresp, patch_mock_check:
            await swift_browser_ui.ui.api.swift_list_containers(
                self.mock_request,
            )
            self.mock_response_prepare.assert_awaited_once()
            self.mock_iter.assert_called()
            self.mock_response_write.assert_awaited()
            self.mock_response_write_eof.assert_awaited_once()

    async def test_swift_list_containers_fail_ostack(self):
        """Test failed container listing fetch from Openstack."""
        # Set client response to incorrect
        self.mock_client_response.status = 401
        with self.p_get_sess, self.p_sresp:
            await swift_browser_ui.ui.api.swift_list_containers(
                self.mock_request,
            )
            self.aiohttp_construct_response_mock.assert_called_once_with(status=401)
            self.mock_response_write.assert_not_called()
            self.mock_response_prepare.assert_awaited_once()
            self.mock_response_write_eof.assert_awaited_once()

    async def test_swift_list_containers_no_access(self):
        """Test failed container listing access rights."""
        # Set request project to incorrect
        self.mock_request.match_info["project"] = "test-id-not-available"
        with self.p_get_sess, self.assertRaises(aiohttp.web.HTTPForbidden):
            await swift_browser_ui.ui.api.swift_list_containers(
                self.mock_request,
            )

    async def test_check_last_modified(self):
        """Test different scenarios for container list last_modified value."""
        # If container in the list already has last_modified key and value
        container = {"name": "folder", "last_modified": "something"}
        with self.p_get_sess:
            ret = await swift_browser_ui.ui.api._check_last_modified(
                self.mock_request,
                container,
            )
        self.mock_client.head.assert_not_called()
        self.assertEqual(ret["last_modified"], "something")

        # If head request response doesn't have Last-Modified value for some reason
        container = {"name": "folder"}
        with self.p_get_sess:
            ret = await swift_browser_ui.ui.api._check_last_modified(
                self.mock_request,
                container,
            )
        self.mock_client.head.assert_called_once()
        self.assertEqual(ret["last_modified"], None)

        # If head request response has a value for Last-Modified
        self.mock_client_response.headers = {
            "Last-Modified": "Thu, 1 Jan 1970 13:37:00 GMT",
        }
        container = {"name": "folder"}
        with self.p_get_sess:
            ret = await swift_browser_ui.ui.api._check_last_modified(
                self.mock_request,
                container,
            )
        self.assertEqual(ret["last_modified"], "1970-01-01T13:37:00.000000")


class ProxyFunctionsTestClass(tests.common.mockups.APITestBase):
    """Test the handlers proxying information to the upload runner."""

    def setUp(self):
        """."""
        super().setUp()
        self.mock_request.match_info = {
            "project": "test-id-1",
            "container": "test-container",
            "object": "test-object",
            "object_name": "test-object-name",
        }
        self.mock_request.query = {
            "from_container": "test-container-2",
            "from_project": "test-project-2",
            "project": "test-project",
        }
        self.mock_request.query_string = ("&test-query=test-value§",)
        self.mock_request.remote = ("remote",)

        self.session_open_mock = unittest.mock.AsyncMock(return_value="test_runner_id")
        self.patch_runner_session = unittest.mock.patch(
            "swift_browser_ui.ui.api.open_upload_runner_session", self.session_open_mock
        )

        self.sign_mock = unittest.mock.AsyncMock(
            return_value={
                "signature": "test-signature",
                "valid": "test-valid",
            }
        )
        self.patch_sign = unittest.mock.patch(
            "swift_browser_ui.ui.api.sign", self.sign_mock
        )

    async def test_get_upload_session(self):
        """Test get active upload session."""
        with self.p_get_sess, self.patch_runner_session, self.patch_setd, self.patch_sign:
            await swift_browser_ui.ui.api.get_upload_session(
                self.mock_request,
            )
        self.session_open_mock.assert_awaited_once()
        self.sign_mock.assert_awaited_once()

    async def test_get_crypted_upload_session(self):
        """Test get crypted upload session."""
        with self.p_get_sess, self.patch_runner_session, self.patch_setd, self.patch_sign:
            await swift_browser_ui.ui.api.get_crypted_upload_session(
                self.mock_request,
            )
        self.session_open_mock.assert_awaited_once()
        self.assertEqual(self.sign_mock.await_count, 2)

    async def test_close_upload_session(self):
        """Test close upload session."""
        with self.p_get_sess, self.patch_runner_session, self.patch_setd, self.patch_sign:
            resp = await swift_browser_ui.ui.api.close_upload_session(
                self.mock_request,
            )
        self.mock_client.delete.assert_called_once()
        self.assertEqual(200, resp.status)
