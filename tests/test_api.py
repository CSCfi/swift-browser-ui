"""Module for testing ``s3browser.api``."""

import json
import hashlib
import os

import pytest

from aiohttp.web import HTTPNotFound
import asynctest

from s3browser.api import get_os_user, os_list_projects
from s3browser.api import swift_list_buckets, swift_list_objects
from s3browser.api import swift_download_object
from s3browser.api import get_metadata
from s3browser.api import get_project_metadata
from s3browser.settings import setd

from .creation import get_request_with_mock_openstack


class APITestClass(asynctest.TestCase):
    """."""

    def setUp(self):
        """Set up necessary mocks."""
        self.cookie, self.request = get_request_with_mock_openstack()

    @pytest.mark.asyncio
    async def test_get_os_user(self):
        """Test for the API call for fetching the Openstack username."""
        # _, request = get_request_with_mock_openstack()
        response = await get_os_user(self.request)
        self.assertEqual(json.loads(response.text), "test_user_id")

    # Follows the testing of the different list functions
    @pytest.mark.asyncio
    async def test_list_containers_correct(self):
        """Test function swift_list_buckets with a correct query."""
        self.request.app['Creds'][self.cookie]['ST_conn'].init_with_data(
            containers=100,
            object_range=(0, 10),
            size_range=(65535, 262144),
        )
        response = await swift_list_buckets(self.request)
        buckets = json.loads(response.text)
        buckets = [i['name'] for i in buckets]
        comp = [
            i for i in self.request.app['Creds'][self.cookie]['ST_conn'].containers.keys()
        ]
        # Test if return all the correct values from the mock service
        self.assertEqual(buckets, comp)

    @pytest.mark.asyncio
    async def test_list_objects_correct(self):
        """Test function swift_list_objetcs with a correct query."""
        self.request.app['Creds'][self.cookie]['ST_conn'].init_with_data(
            containers=5,
            object_range=(10, 100),
            size_range=(65535, 262144),
        )
        for container in ['test-container-' + str(i) for i in range(0, 5)]:
            self.request.query['bucket'] = container
            response = await swift_list_objects(self.request)
            objects = json.loads(response.text)
            objects = [i['hash'] for i in objects]
            comp = [
                i['hash'] for i
                in self.request.app['Creds'][self.cookie]['ST_conn'].containers[container]
            ]
            self.assertEqual(objects, comp)

    @pytest.mark.asyncio
    async def test_list_without_containers(self):
        """Test function list buckets on a project without object storage."""
        self.request.app['Creds'][self.cookie]['ST_conn'].init_with_data(
            containers=0
        )
        with self.assertRaises(HTTPNotFound):
            _ = await swift_list_buckets(self.request)

    @pytest.mark.asyncio
    async def test_list_with_invalid_container(self):
        """Test function list objects with an invalid container id."""
        # Let's create some test data anyway
        self.request.app['Creds'][self.cookie]['ST_conn'].init_with_data(
            containers=3,
            object_range=(1, 5),
            size_range=(65535, 262144),
        )
        self.request.query['bucket'] = "Free buckets causing havoc at the local market"
        response = await swift_list_objects(self.request)
        objects = json.loads(response.text)
        self.assertEqual(objects, [])

    @pytest.mark.asyncio
    async def test_list_without_objects(self):
        """Test function list objects without an object query in the self.request."""
        self.request.app['Creds'][self.cookie]['ST_conn'].init_with_data(
            containers=1,
            object_range=(0, 0),
        )
        self.request.query['bucket'] = "test-container-0"
        with self.assertRaises(HTTPNotFound):
            _ = await swift_list_objects(self.request)

    @pytest.mark.asyncio
    async def test_os_list_projects(self):
        """Test function os_list_projects for correct output."""
        # No need to generate test data, all required stuff can be found in the
        # mock-app
        response = await os_list_projects(self.request)
        projects = json.loads(response.text)
        self.assertEqual(
            projects, self.request.app['Creds'][self.cookie]['Avail']['projects']
        )

    @pytest.mark.asyncio
    async def test_swift_download_object(self):
        """Test object download function."""
        self.request.app['Creds'][self.cookie]['ST_conn'].init_with_data(
            containers=1,
            object_range=(1, 1),
            size_range=(4096, 4096),
        )
        # Get names for the download query
        container = "test-container-0"
        object_name = self.request.app['Creds'][self.cookie]['ST_conn'].containers[
            container
        ][0]

        self.request.query['bucket'] = container
        self.request.query['objkey'] = object_name

        # Set the swift endpoint URL
        setd["swift_endpoint_url"] = "http://object.example-os.com:443/v1"

        # Case 1: Only Meta-Temp-URL-Key exists
        self.request.app['Creds'][self.cookie]['ST_conn'].tempurl_key_1 = \
            hashlib.md5(os.urandom(128)).hexdigest()  # nosec
        resp = await swift_download_object(self.request)
        self.assertTrue(resp.headers['Location'] is not None)

        # Case 2: Only Meta-Temp-URL-Key-2
        self.request.app['Creds'][self.cookie]['ST_conn'].tempurl_key_1 = None
        self.request.app['Creds'][self.cookie]['ST_conn'].tempurl_key_2 = \
            hashlib.md5(os.urandom(128)).hexdigest()  # nosec
        resp = await swift_download_object(self.request)
        self.assertTrue(resp.headers['Location'] is not None)

        # Case 3: No pre-existing keys
        self.request.app['Creds'][self.cookie]['ST_conn'].meta = {
            "tempurl_key_1": None,
            "tempurl_key_2": None,
        }
        resp = await swift_download_object(self.request)
        self.assertTrue(
            self.request.app['Creds'][self.cookie]['ST_conn'].meta[
                "tempurl_key_1"
            ] is None
        )
        self.assertTrue(
            self.request.app['Creds'][self.cookie]['ST_conn'].meta[
                "tempurl_key_2"
            ] is not None
        )
        self.assertTrue(resp.headers['Location'] is not None)

    # Below are the tests for the metadata API endpoint. The account metadata
    # fetches won't be implemented and thus won't be tested, because the account
    # metadata contains sensitive information. (e.g. the tempurl keys)
    @pytest.mark.asyncio
    async def test_get_container_meta_swift(self):
        """Test metadata API endpoint with container metadata."""
        self.request.app['Creds'][self.cookie]['ST_conn'].init_with_data(
            containers=1,
            object_range=(1, 1),
            size_range=(252144, 252144),
        )
        self.request.app['Creds'][self.cookie]['ST_conn'].meta = {
            "tempurl_key_1": None,
            "tempurl_key_2": None,
        }
        self.request.app['Creds'][self.cookie]['ST_conn'].set_swift_meta_container(
            "test-container-0"
        )

        # Set up the query string
        self.request.query["container"] = "test-container-0"

        resp = await get_metadata(self.request)
        resp = json.loads(resp.text)

        expected = [  # nosec
            "test-container-0", {"obj-example": "example"}
        ]
        self.assertEqual(resp, expected)

    @pytest.mark.asyncio
    async def test_get_object_meta_swift(self):
        """Test metadata API endpoint when object has swift metadata."""
        self.request.app['Creds'][self.cookie]['ST_conn'].init_with_data(
            containers=1,
            object_range=(1, 1),
            size_range=(252144, 252144),
        )
        self.request.app['Creds'][self.cookie]['ST_conn'].meta = {
            "tempurl_key_1": None,
            "tempurl_key_2": None,
        }
        # Get the object key to test with
        objs = self.request.app['Creds'][self.cookie]['ST_conn'].containers[
            "test-container-0"]
        objkey = [i['name'] for i in objs][0]

        self.request.app['Creds'][self.cookie]['ST_conn'].set_swift_meta_container(
            "test-container-0"
        )

        self.request.app['Creds'][self.cookie]['ST_conn'].set_swift_meta_object(
            "test-container-0",
            objkey
        )

        # Set up the query string
        self.request.query["container"] = "test-container-0"
        self.request.query["object"] = objkey

        resp = await get_metadata(self.request)
        resp = json.loads(resp.text)
        expected = [[
            objkey, {"obj-example": "example"}
        ]]
        self.assertEqual(resp, expected)

    @pytest.mark.asyncio
    async def test_get_object_meta_s3(self):
        """Test metadata API endpoint when object has s3 metadata."""
        self.request.app['Creds'][self.cookie]['ST_conn'].init_with_data(
            containers=1,
            object_range=(1, 1),
            size_range=(252144, 252144),
        )
        self.request.app['Creds'][self.cookie]['ST_conn'].meta = {
            "tempurl_key_1": None,
            "tempurl_key_2": None,
        }
        # Get the object key to test with
        objs = self.request.app['Creds'][self.cookie]['ST_conn'].containers[
            "test-container-0"]
        objkey = [i['name'] for i in objs][0]

        self.request.app['Creds'][self.cookie]['ST_conn'].set_swift_meta_container(
            "test-container-0"
        )

        self.request.app['Creds'][self.cookie]['ST_conn'].set_s3_meta_object(
            "test-container-0",
            objkey
        )

        # Set up the query string
        self.request.query["container"] = "test-container-0"
        self.request.query["object"] = objkey

        resp = await get_metadata(self.request)
        resp = json.loads(resp.text)

        expected = [[  # nosec
            objkey, {
                "s3cmd-attrs": {
                    "atime": "1536648772",
                    "ctime": "1536648921",
                    "gid": "101",
                    "gname": "example",
                }
            }
        ]]
        self.assertEqual(resp, expected)

    @pytest.mark.asyncio
    async def test_get_object_meta_swift_whole(self):
        """Test metadata API endpoint with containers' objects."""
        self.request.app['Creds'][self.cookie]['ST_conn'].init_with_data(
            containers=1,
            object_range=(5, 5),
            size_range=(252144, 252144),
        )
        self.request.app['Creds'][self.cookie]['ST_conn'].meta = {
            "tempurl_key_1": None,
            "tempurl_key_2": None,
        }

        self.request.app['Creds'][self.cookie]['ST_conn'].set_swift_meta_container(
            "test-container-0"
        )

        objs = self.request.app['Creds'][self.cookie]['ST_conn'].containers[
            "test-container-0"]
        for key in [i['name'] for i in objs]:
            self.request.app['Creds'][self.cookie]['ST_conn'].set_swift_meta_object(
                "test-container-0",
                key
            )

        self.request.query["container"] = "test-container-0"
        self.request.query["object"] = (
            "%s,%s,%s,%s,%s" % tuple([i["name"] for i in objs])
        )

        resp = await get_metadata(self.request)
        resp = json.loads(resp.text)

        comp = [
            [i, {"obj-example": "example"}]
            for i in [j["name"] for j in objs]
        ]

        self.assertEqual(resp, comp)

    @pytest.mark.asyncio
    async def test_get_project_metadata(self):
        """Test metadata API endpoint for account metadata."""
        self.request.app['Creds'][self.cookie]['ST_conn'].init_with_data(
            containers=5,
            object_range=(100, 100),
            size_range=(1073741824, 1073741824)
        )

        # Compare against the bare minimum amount of information required, which
        # will be what the function should return.
        comp = {
            'Account': 'AUTH_test_account',
            'Containers': 5,
            'Objects': 500,
            'Bytes': 536870912000,
        }

        resp = await get_project_metadata(self.request)
        resp = json.loads(resp.text)

        self.assertEqual(resp, comp)
