"""
This module contains the mock-up classes and functions, used for testing the
s3browser package.
"""


import random
import hashlib
import os
import time
import json
from swiftclient.service import SwiftError
from urllib.error import HTTPError
from contextlib import contextmanager


mock_token_project_avail = json.dumps({
    "projects": [
        {
            "is_domain": False,
            "description": "",
            "links": {
                "self": "https://place-holder-url:5001/v3/projects/placeholder"
            },
            "enabled": True,
            "id": "placeholder",
            "parent_id": "default",
            "domain_id": "default",
            "name": "placeholder",
        },        {
            "is_domain": False,
            "description": "Wololo yol aweii",
            "links": {
                "self": "https://place-holder-url:5001/v3/projects/wol"
            },
            "enabled": True,
            "id": "wol",
            "parent_id": "default",
            "domain_id": "default",
            "name": "wol",
        },        {
            "is_domain": False,
            "description": "Hmmph, what is",
            "links": {
                "self": "https://place-holder-url:5001/v3/projects/what"
            },
            "enabled": True,
            "id": "what",
            "parent_id": "default",
            "domain_id": "default",
            "name": "what",
        },
    ],
})


mock_token_domain_avail = json.dumps({"domains": []})


mock_token_output = {
    "projects": [
        {
            "is_domain": False,
            "description": "",
            "links": {
                "self": "https://place-holder-url:5001/v3/projects/placeholder"
            },
            "enabled": True,
            "id": "placeholder",
            "parent_id": "default",
            "domain_id": "default",
            "name": "placeholder",
        },        {
            "is_domain": False,
            "description": "Wololo yol aweii",
            "links": {
                "self": "https://place-holder-url:5001/v3/projects/wol"
            },
            "enabled": True,
            "id": "wol",
            "parent_id": "default",
            "domain_id": "default",
            "name": "wol",
        },        {
            "is_domain": False,
            "description": "Hmmph, what is",
            "links": {
                "self": "https://place-holder-url:5001/v3/projects/what"
            },
            "enabled": True,
            "id": "what",
            "parent_id": "default",
            "domain_id": "default",
            "name": "what",
        },
    ],
    "domains": [],
}


def return_same_cookie(req):
    return ("placeholder", "placeholder")


def return_project_avail(token):
    """Return mocked unscoped token availability output"""
    return mock_token_output


@contextmanager
def urlopen(prq):
    """Mockup class for opening keystone"""
    yield Mock_Keystone(prq)


class Mock_Keystone:
    """Mockup class for OS Keystone to enable testing availability."""

    def __init__(self, prq):
        self.prq = prq

    def read(self):
        if "X-auth-token" not in self.prq.headers:
            raise HTTPError(
                url=None,
                code=401,
                msg="Unauthorized",
                hdrs=self.prq.headers,
                fp=None
            )
        if "projects" in self.prq.full_url:
            return mock_token_project_avail.encode('utf-8')
        if "domains" in self.prq.full_url:
            return mock_token_domain_avail.encode('utf-8')
        else:
            raise HTTPError(
                url=None,
                code=401,
                msg="Unauthorized",
                hdrs=self.prq.headers,
                fp=None
            )


class Mock_Request:
    """
    Mock-up class for the aiohttp.web.Request, which contains the dictionary
    representation of the requests that will be passed to the functions. (the
    actual request eing a MutableMapping instance)
    """
    app = None
    headers = {}
    cookies = {}
    query = {}
    remote = "127.0.0.1"

    def __init__(self):
        # Application mutable mapping represented by a dictionary
        self.app = {}
        self.post_data = {}

    def set_headers(self, headers):
        """
        Set mock request headers.
        Params:
            headers: dict
        """
        for i in headers.keys():
            self.headers[i] = headers[i]

    def set_cookies(self, cookies):
        """
        Set mock request cookies.
        Params:
            cookies: dict
        """
        for i in cookies.keys():
            self.cookies[i] = cookies[i]

    def set_post(self, data):
        """Set post data."""
        self.post_data = data

    async def post(self):
        """"Return post data."""
        return self.post_data


class Mock_Service:
    """
    Mock-up class for the Openstack service, in this case a swiftclient.Service
    instance. Contains the mock-ups for the relevant methods used in this
    project. Also contains functions for generating test data, in case it is
    necessary.
    """
    containers = {}  # mock containers as a dictionary
    tempurl_key_1 = None  # Tempurl keys for the stat() command
    tempurl_key_2 = None  # Tempurl keys for the stat() command

    def init_with_data(
        self,
        containers=0,
        object_range=(0, 0),
        size_range=(0, 0),
        container_name_prefix="test-container-",
        object_name_prefix=None,  # None for just the hash as name
    ):
        """
        Initialize the Mock_Service instance with some test data, that can be
        used for testing.
        """
        for i in range(0, containers):
            to_add = []

            # Iterate over a random amount of objects
            for _ in range(
                0, random.randint(object_range[0], object_range[1])  # nosec
            ):
                ohash = hashlib.sha1(os.urandom(256)).hexdigest()  # nosec
                if object_name_prefix is not None:
                    oname = object_name_prefix + ohash
                else:
                    oname = ohash
                to_add.append({
                    "hash": ohash,
                    "name": oname,
                    "last_modified": str(time.time()),
                    "bytes": random.randint(  # nosec
                        size_range[0], size_range[1]
                    ),
                })

            self.containers[container_name_prefix + str(i)] = to_add

    def list(self, container=None, options=None):
        """
        Mock function for the service object / container listings
        """
        if container is None:
            ret = []
            for i in self.containers.keys():
                ret.append({
                    "name": i
                })
            return [{
                "listing": ret
            }]
        elif container is not None:
            ret = []
            try:
                for i in self.containers[container]:
                    ret.append({
                        "hash": i["hash"],
                        "name": i["name"],
                        "last_modified": i["last_modified"],
                        "bytes": i["bytes"]
                    })
                return [{
                    "listing": ret
                }]
            except KeyError:
                raise SwiftError(None, container=container)
        else:
            return None

    def stat(self, container=None, objects=None):
        """Mock the stat() call of SwiftService"""
        ret = {
            "headers": {},
            "items": [
                ("Account", "AUTH_test_account",)
            ],
        }
        # Add the tempurl headers to the return dictionary, if they have been
        # initialized
        if self.tempurl_key_1 is not None:
            ret['headers']['x-account-meta-temp-url-key'] = self.tempurl_key_1
        if self.tempurl_key_2 is not None:
            ret['headers']['x-account-meta-temp-url-key-2'] =\
                self.tempurl_key_2

        return ret

    def post(self, options=None):
        """Mock the post() call of SwiftService."""
        # Get the URL key 2
        key = options['meta'][0].split(':')[1]
        self.tempurl_key_2 = key
        return {"success": True}


class Mock_Session:
    """
    Mock-up class for the Openstack keystoneauth1 session instance, which
    contains the relevant methods for querying the OS identity API (aka.
    keystone)
    """
    def __init__(self):
        pass

    def get_user_id(self):
        """
        Mock function for fetching the user id from the mock OS Session
        """
        return "test_user_id"
