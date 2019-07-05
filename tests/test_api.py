"""Module for testing ``s3browser.api``."""

import pytest
import json
import hashlib
import os


from .creation import get_request_with_mock_openstack
from s3browser.api import get_os_user, os_list_projects
from s3browser.api import swift_list_buckets, swift_list_objects
from s3browser.api import swift_download_object
from s3browser.settings import setd


@pytest.mark.asyncio
async def test_get_os_user():
    """Test for the API call for fetching the Openstack username."""
    _, request = get_request_with_mock_openstack()
    response = await get_os_user(request)
    assert json.loads(response.text) == "test_user_id"  # nosec


# Follows the testing of the different list functions
@pytest.mark.asyncio
async def test_list_containers_correct():
    """Test function swift_list_buckets with a correct query."""
    cookie, request = get_request_with_mock_openstack()
    request.app['Creds'][cookie]['ST_conn'].init_with_data(
        containers=100,
        object_range=(0, 10),
        size_range=(65535, 262144),
    )
    response = await swift_list_buckets(request)
    buckets = json.loads(response.text)
    buckets = [i['name'] for i in buckets]
    comp = [
        i for i in request.app['Creds'][cookie]['ST_conn'].containers.keys()
    ]
    # Test if return all the correct values from the mock service
    assert buckets == comp  # nosec


@pytest.mark.asyncio
async def test_list_objects_correct():
    """Test function swift_list_objetcs with a correct query."""
    cookie, request = get_request_with_mock_openstack()
    request.app['Creds'][cookie]['ST_conn'].init_with_data(
        containers=5,
        object_range=(0, 100),
        size_range=(65535, 262144),
    )
    for container in ['test-container-' + str(i) for i in range(0, 5)]:
        request.query['bucket'] = container
        response = await swift_list_objects(request)
        objects = json.loads(response.text)
        objects = [i['hash'] for i in objects]
        comp = [
            i['hash'] for i
            in request.app['Creds'][cookie]['ST_conn'].containers[container]
        ]
        assert objects == comp  # nosec


@pytest.mark.asyncio
async def test_list_wihtout_containers():
    """Test function list buckets on a project without object storage."""
    cookie, request = get_request_with_mock_openstack()
    request.app['Creds'][cookie]['ST_conn'].init_with_data(
        containers=0
    )
    response = await swift_list_buckets(request)
    containers = json.loads(response.text)
    assert containers == []  # nosec


@pytest.mark.asyncio
async def test_list_with_invalid_container():
    """Test function list objects with an invalid container id."""
    cookie, request = get_request_with_mock_openstack()
    # Let's create some test data anyway
    request.app['Creds'][cookie]['ST_conn'].init_with_data(
        containers=3,
        object_range=(1, 5),
        size_range=(65535, 262144),
    )
    request.query['bucket'] = "Free buckets causing havoc at the local market"
    response = await swift_list_objects(request)
    objects = json.loads(response.text)
    assert objects == []  # nosec


@pytest.mark.asyncio
async def test_list_without_objects():
    """Test function list objects without an object query in the request."""
    cookie, request = get_request_with_mock_openstack()
    request.app['Creds'][cookie]['ST_conn'].init_with_data(
        containers=1,
        object_range=(0, 0),
    )
    request.query['bucket'] = "test-container-0"
    response = await swift_list_objects(request)
    objects = json.loads(response.text)
    assert objects == []  # nosec


@pytest.mark.asyncio
async def test_list_with_many_objects():
    """Test function list objects with a large set of objects."""
    cookie, request = get_request_with_mock_openstack()
    # Shouldn't be any reason to test with multiple containers, saves time
    # this way
    request.app['Creds'][cookie]['ST_conn'].init_with_data(
        containers=1,
        object_range=(100000, 100000),  # default max container limit
        size_range=(65535, 262144),
    )
    container = "test-container-0"
    request.query['bucket'] = container
    response = await swift_list_objects(request)
    objects = json.loads(response.text)
    objects = [i['hash'] for i in objects]
    comp = [
        i['hash'] for i
        in request.app['Creds'][cookie]['ST_conn'].containers[container]
    ]
    assert objects == comp  # nosec


@pytest.mark.asyncio
async def test_os_list_projects():
    """Test function os_list_projects for correct output."""
    cookie, request = get_request_with_mock_openstack()
    # No need to generate test data, all required stuff can be found in the
    # mock-app
    response = await os_list_projects(request)
    projects = json.loads(response.text)
    assert (  # nosec
        projects == request.app['Creds'][cookie]['Avail']['projects']
    )


@pytest.mark.asyncio
async def test_swift_download_object():
    """Test object download function."""
    cookie, request = get_request_with_mock_openstack()
    request.app['Creds'][cookie]['ST_conn'].init_with_data(
        containers=1,
        object_range=(1, 1),
        size_range=(4096, 4096),
    )
    # Get names for the download query
    container = "test-container-0"
    object_name = request.app['Creds'][cookie]['ST_conn'].containers[
        container
    ][0]

    request.query['bucket'] = container
    request.query['objkey'] = object_name

    # Set the swift endpoint URL
    setd["swift_endpoint_url"] = "http://object.example-os.com:443/v1"

    # Case 1: Only Meta-Temp-URL-Key exists
    request.app['Creds'][cookie]['ST_conn'].tempurl_key_1 = \
        hashlib.md5(os.urandom(128)).hexdigest()  # nosec
    resp = await swift_download_object(request)
    assert resp.headers['Location'] is not None  # nosec

    # Case 2: Only Meta-Temp-URL-Key-2
    request.app['Creds'][cookie]['ST_conn'].tempurl_key_1 = None
    request.app['Creds'][cookie]['ST_conn'].tempurl_key_2 = \
        hashlib.md5(os.urandom(128)).hexdigest()  # nosec
    resp = await swift_download_object(request)
    assert resp.headers['Location'] is not None  # nosec

    # Case 3: No pre-existing keys
    request.app['Creds'][cookie]['ST_conn'].tempurl_key_1 = None
    request.app['Creds'][cookie]['ST_conn'].tempurl_key_2 = None
    resp = await swift_download_object(request)
    assert(  # nosec
        request.app['Creds'][cookie]['ST_conn'].tempurl_key_1 is None
    )
    assert(  # nosec
        request.app['Creds'][cookie]['ST_conn'].tempurl_key_2 is not None
    )
    assert resp.headers['Location'] is not None  # nosec
