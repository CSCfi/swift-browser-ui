"""Module for testing ``swift_browser_ui.ui.api``."""

import json
import hashlib
import os
import unittest
import types
import logging

from aiohttp.web import HTTPNotFound
import asynctest

from swiftclient.service import SwiftError

from swift_browser_ui.ui.api import get_os_user, os_list_projects
from swift_browser_ui.ui.api import swift_list_buckets, swift_list_objects
from swift_browser_ui.ui.api import swift_download_object
from swift_browser_ui.ui.api import get_metadata_object
from swift_browser_ui.ui.api import get_metadata_bucket
from swift_browser_ui.ui.api import get_project_metadata
from swift_browser_ui.ui.api import get_os_active_project
from swift_browser_ui.ui.api import swift_download_shared_object
from swift_browser_ui.ui.api import swift_download_container
from swift_browser_ui.ui.api import swift_upload_object_chunk
from swift_browser_ui.ui.api import swift_replicate_container
from swift_browser_ui.ui.api import swift_check_object_chunk
from swift_browser_ui.ui.settings import setd

from .creation import get_request_with_mock_openstack


class APITestClass(asynctest.TestCase):
    """Testing the Object Browser API."""

    def setUp(self):
        """Set up necessary mocks."""
        self.cookie, self.request = get_request_with_mock_openstack()

    async def test_get_os_user(self):
        """Test for the API call for fetching the Openstack username."""
        # _, request = get_request_with_mock_openstack()
        response = await get_os_user(self.request)
        self.assertEqual(json.loads(response.text), "test_user_id")

    # Follows the testing of the different list functions
    async def test_list_containers_correct(self):
        """Test function swift_list_buckets with a correct query."""
        self.request.app["Sessions"][self.cookie]["ST_conn"].init_with_data(
            containers=100,
            object_range=(0, 10),
            size_range=(65535, 262144),
        )
        response = await swift_list_buckets(self.request)
        buckets = json.loads(response.text)
        buckets = [i["name"] for i in buckets]
        comp = [
            i
            for i in self.request.app["Sessions"][self.cookie][
                "ST_conn"
            ].containers.keys()
        ]
        # Test if return all the correct values from the mock service
        self.assertEqual(buckets, comp)

    async def test_list_containers_swift_error(self):
        """Test function swift_list_buckets when raising SwiftError."""
        self.request.app["Sessions"][self.cookie]["ST_conn"].list = unittest.mock.Mock(
            side_effect=SwiftError("...")
        )
        with self.assertRaises(HTTPNotFound):
            _ = await swift_list_buckets(self.request)

    async def test_list_objects_correct(self):
        """Test function swift_list_objetcs with a correct query."""
        self.request.app["Sessions"][self.cookie]["ST_conn"].init_with_data(
            containers=5,
            object_range=(10, 100),
            size_range=(65535, 262144),
        )
        for container in ["test-container-" + str(i) for i in range(0, 5)]:
            self.request.query["bucket"] = container
            response = await swift_list_objects(self.request)
            objects = json.loads(response.text)
            objects = [i["hash"] for i in objects]
            comp = [
                i["hash"]
                for i in self.request.app["Sessions"][self.cookie]["ST_conn"].containers[
                    container
                ]
            ]
            self.assertEqual(objects, comp)

    async def test_list_objects_with_unicode_nulls(self):
        """Test function swift_list_objects with unicode nulls in type."""
        self.request.app["Sessions"][self.cookie]["ST_conn"].init_with_data(
            containers=1,
            object_range=(1, 10),
            size_range=(65535, 262144),
            has_content_type="text/html",
        )
        self.request.query["bucket"] = "test-container-0"
        response = await swift_list_objects(self.request)
        objects = json.loads(response.text)
        self.assertEqual(
            objects[0]["content_type"],
            "text/html",
        )

    async def test_list_without_containers(self):
        """Test function list buckets on a project without object storage."""
        self.request.app["Sessions"][self.cookie]["ST_conn"].init_with_data(containers=0)
        with self.assertRaises(HTTPNotFound):
            _ = await swift_list_buckets(self.request)

    async def test_list_with_invalid_container(self):
        """Test function list objects with an invalid container id."""
        # Let's create some test data anyway
        self.request.app["Sessions"][self.cookie]["ST_conn"].init_with_data(
            containers=3,
            object_range=(1, 5),
            size_range=(65535, 262144),
        )
        self.request.query[
            "bucket"
        ] = """Free buckets causing havoc\
                                          at the local market"""
        response = await swift_list_objects(self.request)
        objects = json.loads(response.text)
        self.assertEqual(objects, [])

    async def test_list_without_objects(self):
        """Test function list objects without an object query in request."""
        self.request.app["Sessions"][self.cookie]["ST_conn"].init_with_data(
            containers=1,
            object_range=(0, 0),
        )
        self.request.query["bucket"] = "test-container-0"
        with self.assertRaises(HTTPNotFound):
            _ = await swift_list_objects(self.request)

    async def test_os_list_projects(self):
        """Test function os_list_projects for correct output."""
        # No need to generate test data, all required stuff can be found in the
        # mock-app
        response = await os_list_projects(self.request)
        projects = json.loads(response.text)
        self.assertEqual(
            projects, self.request.app["Sessions"][self.cookie]["Avail"]["projects"]
        )

    async def test_swift_download_object(self):
        """Test object download function."""
        self.request.app["Sessions"][self.cookie]["ST_conn"].init_with_data(
            containers=1,
            object_range=(1, 1),
            size_range=(4096, 4096),
        )
        # Get names for the download query
        container = "test-container-0"
        o_name = self.request.app["Sessions"][self.cookie]["ST_conn"].containers[
            container
        ][0]["name"]

        self.request.app["Sessions"][self.cookie]["ST_conn"].set_swift_meta_container(
            "test-container-0"
        )
        self.request.app["Sessions"][self.cookie]["ST_conn"].set_swift_meta_object(
            "test-container-0", o_name
        )

        self.request.query["bucket"] = container
        self.request.query["objkey"] = o_name

        # Set the swift endpoint URL
        setd["swift_endpoint_url"] = "http://object.example-os.com:443/v1"

        # Case 1: Only Meta-Temp-URL-Key exists
        self.request.app["Sessions"][self.cookie]["ST_conn"].tempurl_key_1 = hashlib.md5(
            os.urandom(128)
        ).hexdigest()  # nosec
        resp = await swift_download_object(self.request)
        self.assertTrue(resp.headers["Location"] is not None)

        # Case 2: Only Meta-Temp-URL-Key-2
        self.request.app["Sessions"][self.cookie]["ST_conn"].tempurl_key_1 = None
        self.request.app["Sessions"][self.cookie]["ST_conn"].tempurl_key_2 = hashlib.md5(
            os.urandom(128)
        ).hexdigest()  # nosec
        resp = await swift_download_object(self.request)
        self.assertTrue(resp.headers["Location"] is not None)

        # Case 3: No pre-existing keys
        self.request.app["Sessions"][self.cookie]["ST_conn"].meta = {
            "tempurl_key_1": None,
            "tempurl_key_2": None,
        }
        resp = await swift_download_object(self.request)
        self.assertTrue(
            self.request.app["Sessions"][self.cookie]["ST_conn"].meta["tempurl_key_1"]
            is None
        )
        self.assertTrue(
            self.request.app["Sessions"][self.cookie]["ST_conn"].meta["tempurl_key_2"]
            is not None
        )
        self.assertTrue(resp.headers["Location"] is not None)

    # Below are the tests for the metadata API endpoint. The account metadata
    # fetches won't be implemented and thus won't be tested,
    # because the account
    # metadata contains sensitive information. (e.g. the tempurl keys)
    async def test_get_container_meta_swift(self):
        """Test metadata API endpoint with container metadata."""
        req_sessions = self.request.app["Sessions"]
        req_sessions[self.cookie]["ST_conn"].init_with_data(
            containers=1,
            object_range=(1, 1),
            size_range=(252144, 252144),
        )
        req_sessions[self.cookie]["ST_conn"].meta = {
            "tempurl_key_1": None,
            "tempurl_key_2": None,
        }
        req_sessions[self.cookie]["ST_conn"].set_swift_meta_container("test-container-0")

        # Set up the query string
        self.request.query["container"] = "test-container-0"

        resp = await get_metadata_bucket(self.request)
        resp = json.loads(resp.text)

        expected = ["test-container-0", {"obj-example": "example"}]  # nosec
        self.assertEqual(resp, expected)

    async def test_get_object_meta_swift(self):
        """Test metadata API endpoint when object has swift metadata."""
        req_sessions = self.request.app["Sessions"]
        req_sessions[self.cookie]["ST_conn"].init_with_data(
            containers=1,
            object_range=(1, 1),
            size_range=(252144, 252144),
        )
        req_sessions[self.cookie]["ST_conn"].meta = {
            "tempurl_key_1": None,
            "tempurl_key_2": None,
        }
        # Get the object key to test with
        objs = req_sessions[self.cookie]["ST_conn"].containers["test-container-0"]
        objkey = [i["name"] for i in objs][0]

        req_sessions[self.cookie]["ST_conn"].set_swift_meta_container("test-container-0")

        req_sessions[self.cookie]["ST_conn"].set_swift_meta_object(
            "test-container-0", objkey
        )

        # Set up the query string
        self.request.query["container"] = "test-container-0"
        self.request.query["object"] = objkey

        resp = await get_metadata_object(self.request)
        resp = json.loads(resp.text)
        expected = [[objkey, {"obj-example": "example"}]]
        self.assertEqual(resp, expected)

    async def test_get_object_meta_s3(self):
        """Test metadata API endpoint when object has s3 metadata."""
        req_sessions = self.request.app["Sessions"]
        req_sessions[self.cookie]["ST_conn"].init_with_data(
            containers=1,
            object_range=(1, 1),
            size_range=(252144, 252144),
        )
        req_sessions[self.cookie]["ST_conn"].meta = {
            "tempurl_key_1": None,
            "tempurl_key_2": None,
        }
        # Get the object key to test with
        objs = req_sessions[self.cookie]["ST_conn"].containers["test-container-0"]
        objkey = [i["name"] for i in objs][0]

        req_sessions[self.cookie]["ST_conn"].set_swift_meta_container("test-container-0")

        req_sessions[self.cookie]["ST_conn"].set_s3_meta_object(
            "test-container-0", objkey
        )

        # Set up the query string
        self.request.query["container"] = "test-container-0"
        self.request.query["object"] = objkey

        resp = await get_metadata_object(self.request)
        resp = json.loads(resp.text)

        expected = [
            [  # nosec
                objkey,
                {
                    "s3cmd-attrs": {
                        "atime": "1536648772",
                        "ctime": "1536648921",
                        "gid": "101",
                        "gname": "example",
                    }
                },
            ]
        ]
        self.assertEqual(resp, expected)

    async def test_get_object_meta_swift_whole(self):
        """Test metadata API endpoint with containers' objects."""
        req_sessions = self.request.app["Sessions"]
        req_sessions[self.cookie]["ST_conn"].init_with_data(
            containers=1,
            object_range=(5, 5),
            size_range=(252144, 252144),
        )
        req_sessions[self.cookie]["ST_conn"].meta = {
            "tempurl_key_1": None,
            "tempurl_key_2": None,
        }

        req_sessions[self.cookie]["ST_conn"].set_swift_meta_container("test-container-0")

        objs = req_sessions[self.cookie]["ST_conn"].containers["test-container-0"]
        for key in [i["name"] for i in objs]:
            req_sessions[self.cookie]["ST_conn"].set_swift_meta_object(
                "test-container-0", key
            )

        self.request.query["container"] = "test-container-0"
        self.request.query["object"] = "%s,%s,%s,%s,%s" % tuple([i["name"] for i in objs])

        resp = await get_metadata_object(self.request)
        resp = json.loads(resp.text)

        comp = [[i, {"obj-example": "example"}] for i in [j["name"] for j in objs]]

        self.assertEqual(resp, comp)

    async def test_get_project_metadata(self):
        """Test metadata API endpoint for account metadata."""
        self.request.app["Sessions"][self.cookie]["ST_conn"].init_with_data(
            containers=5, object_range=(100, 100), size_range=(1073741824, 1073741824)
        )

        # Compare against the bare minimum amount of information
        # required, which
        # will be what the function should return.
        comp = {
            "Account": "AUTH_test_account",
            "Containers": 5,
            "Objects": 500,
            "Bytes": 536870912000,
        }

        resp = await get_project_metadata(self.request)
        resp = json.loads(resp.text)

        self.assertEqual(resp, comp)

    async def test_get_os_active_project(self):
        """Test active project API endpoint."""
        self.request.app["Sessions"][self.cookie]["active_project"] = "placeholder"
        resp = await get_os_active_project(self.request)
        text = json.loads(resp.text)
        self.assertEqual(resp.status, 200)
        self.assertEqual(text, "placeholder")

    def tearDown(self):
        """Test teardown."""
        self.cookie = None
        self.request = None


class TestProxyFunctions(asynctest.TestCase):
    """Test the handlers proxying information to the upload runner."""

    def setUp(self):
        """."""
        self.mock_request = types.SimpleNamespace(
            **{
                "match_info": {
                    "project": "test-project",
                    "container": "test-container",
                    "object": "test-object",
                },
                "query": {
                    "from_container": "test-container-2",
                    "from_project": "test-project-2",
                },
                "query_string": "&test-query=test-value",
                "app": {
                    "Sessions": {
                        "session_key": {
                            "active_project": {"id": "test-id"},
                            "Token": "test-token",
                        }
                    },
                    "Log": logging.getLogger(name="test_logger"),
                },
                "remote": "remote",
            }
        )

        self.api_check_mock = unittest.mock.MagicMock(return_value="session_key")
        self.patch_api_check = unittest.mock.patch(
            "swift_browser_ui.ui.api.api_check", self.api_check_mock
        )

        self.session_open_mock = asynctest.CoroutineMock(return_value="test_runner_id")
        self.patch_runner_session = unittest.mock.patch(
            "swift_browser_ui.ui.api.open_upload_runner_session", self.session_open_mock
        )

        self.sign_mock = asynctest.CoroutineMock(
            return_value={
                "signature": "test-signature",
                "valid_until": "test-valid",
            }
        )
        self.patch_sign = unittest.mock.patch(
            "swift_browser_ui.ui.api.sign", self.sign_mock
        )

        self.setd_mock = {"upload_external_endpoint": "http://test-endpoint:9092/"}
        self.patch_setd = unittest.mock.patch(
            "swift_browser_ui.ui.api.setd", self.setd_mock
        )

    async def test_swift_download_share_object(self):
        """Test share object download handler."""
        with self.patch_api_check, self.patch_runner_session, self.patch_setd, self.patch_sign:
            resp = await swift_download_shared_object(self.mock_request)

            self.assertIn("test-signature", resp.headers["Location"])
            self.assertIn("test-valid", resp.headers["Location"])
            self.assertIn("test-endpoint", resp.headers["Location"])
            self.assertEqual(303, resp.status)

    async def test_swift_download_container(self):
        """Test container download handler."""
        with self.patch_api_check, self.patch_runner_session, self.patch_setd, self.patch_sign:
            resp = await swift_download_container(self.mock_request)

            self.assertIn("test-signature", resp.headers["Location"])
            self.assertIn("test-valid", resp.headers["Location"])
            self.assertIn("test-endpoint", resp.headers["Location"])
            self.assertEqual(303, resp.status)

    async def test_swift_upload_object_chunk(self):
        """Test upload object chunk handler."""
        with self.patch_api_check, self.patch_runner_session, self.patch_setd, self.patch_sign:
            resp = await swift_upload_object_chunk(self.mock_request)

            self.assertIn("test-signature", resp.headers["Location"])
            self.assertIn("test-valid", resp.headers["Location"])
            self.assertIn("test-endpoint", resp.headers["Location"])
            self.assertEqual(307, resp.status)

    async def test_swift_replicate_container(self):
        """Test replicate container handler."""
        with self.patch_api_check, self.patch_runner_session, self.patch_setd, self.patch_sign:
            resp = await swift_replicate_container(self.mock_request)

            self.assertIn("test-signature", resp.headers["Location"])
            self.assertIn("test-valid", resp.headers["Location"])
            self.assertIn("test-endpoint", resp.headers["Location"])
            self.assertEqual(307, resp.status)
            self.assertIn("from_container", resp.headers["Location"])
            self.assertIn("test-container-2", resp.headers["Location"])
            self.assertIn("from_project", resp.headers["Location"])
            self.assertIn("test-project-2", resp.headers["Location"])

    async def test_swift_check_object_chunk(self):
        """Test upload object chunk handler."""
        with self.patch_api_check, self.patch_runner_session, self.patch_setd, self.patch_sign:
            resp = await swift_check_object_chunk(self.mock_request)

            self.assertIn("test-signature", resp.headers["Location"])
            self.assertIn("test-valid", resp.headers["Location"])
            self.assertIn("test-endpoint", resp.headers["Location"])
            self.assertEqual(307, resp.status)
            self.assertIn("&test-query=test-value", resp.headers["Location"])
