"""Mock-up classes and functions for testing s3browser."""


import random
import hashlib
import os
import datetime
import json
from urllib.error import HTTPError
from contextlib import contextmanager


from swiftclient.service import SwiftError


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
        }, {
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
        }, {
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
        }, {
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
        }, {
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


def return_same_cookie(_):
    """Return same cookie."""
    return ("placeholder", "placeholder")


def return_invalid(_):
    """Return invalid."""
    return "INVALID"


def return_project_avail(_):
    """Return mocked unscoped token availability output."""
    return mock_token_output


@contextmanager
def urlopen(prq):
    """Mockup class for opening keystone."""
    yield MockKeystone(prq)


class MockKeystone:
    """Mockup class for OS Keystone to enable testing availability."""

    def __init__(self, prq):
        """Initialize Mock keystone."""
        self.prq = prq

    def read(self):
        """Read request."""
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
    Mock-up class for the aiohttp.web.Request.

    It contains the dictionary
    representation of the requests that will be passed to the functions.
    (the actual request eing a MutableMapping instance)
    """

    def __init__(self):
        """Initialize Mock request."""
        # Application mutable mapping represented by a dictionary
        self.app = {}
        self.headers = {}
        self.cookies = {}
        self.query = {}
        self.remote = "127.0.0.1"
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
        """Return post data."""
        return self.post_data


class Mock_Service:
    """
    Mock-up class for the Openstack service.

    In this case a swiftclient.Service
    instance. Contains the mock-ups for the relevant methods used in this
    project. Also contains functions for generating test data, in case it is
    necessary.
    """

    def __init__(self):
        """."""
        self.containers = {}
        self.meta = {
            "tempurl_key_1": None,
            "tempurl_key_2": None,
        }
        self.cont_meta = {}
        self.obj_meta = {}

    def init_with_data(
            self,
            containers=0,
            object_range=(0, 0),
            size_range=(0, 0),
            container_name_prefix="test-container-",
            object_name_prefix=None,  # None for just the hash as name
    ):
        """Initialize the Mock_Service instance with some test data."""
        for i in range(0, containers):
            to_add = []

            # Iterate over a random amount of objects
            for _ in range(
                    0, random.randint(object_range[0],  # nosec
                                      object_range[1])
            ):
                ohash = hashlib.sha1(os.urandom(256)).hexdigest()  # nosec
                if object_name_prefix is not None:
                    oname = object_name_prefix + ohash
                else:
                    oname = ohash
                to_add.append({
                    "hash": ohash,
                    "name": oname,
                    "last_modified": datetime.datetime.now().isoformat(),
                    "bytes": random.randint(  # nosec
                        size_range[0], size_range[1]
                    ),
                })

            self.containers[container_name_prefix + str(i)] = to_add

    def list(self, container=None, options=None):
        """Mock function for the service object / container listings."""
        if container is None:
            ret = []
            for i in self.containers:
                ret.append({
                    "name": i,
                    "count": len(self.containers[i]),
                    "bytes": sum([j['bytes'] for j in self.containers[i]]),
                })
            return [{
                "listing": ret
            }]
        if container is not None:
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

    def stat(self, *args):
        """Mock the stat call of SwiftService."""
        ret = {}
        ret["headers"] = {}
        if not args:
            ret["items"] = [("Account", "AUTH_test_account",), ]
            # Add the tempurl headers to the return dictionary, if they have
            # been initialized
            if self.meta["tempurl_key_1"] is not None:
                ret['headers']['x-account-meta-temp-url-key'] = \
                    self.meta["tempurl_key_1"]
            if self.meta["tempurl_key_2"] is not None:
                ret['headers']['x-account-meta-temp-url-key-2'] =\
                    self.meta["tempurl_key_2"]
            return ret

        if len(args) == 1:
            # If the length is exactly one, then only a container was
            # specified.
            if "Acc_example" in self.cont_meta[args[0]].keys():
                ret['container'] = args[0]
                ret['headers']["x-container-meta-obj-example"] = "example"
                ret['success'] = True
            return ret

        # In any other case the query is for an object.
        # Iterate over the object query list.
        ret = []
        for i in args[1]:
            to_add = {}
            to_add["headers"] = {}
            if "Obj_example" in self.obj_meta[args[0]][i].keys():
                to_add['headers']["x-object-meta-obj-example"] = "example"
            if ("Obj_S3_example" in
                    self.obj_meta[args[0]][i].keys()):
                to_add['headers']["x-object-meta-s3cmd-attrs"] = \
                    self.obj_meta[args[0]][i]["Obj_S3_example"]
            to_add["success"] = True
            to_add["object"] = i
            ret.append(to_add)
        return ret

    def post(self, options=None):
        """Mock the post call of SwiftService."""
        # Get the URL key 2
        key = options['meta'][0].split(':')[1]
        self.meta["tempurl_key_2"] = key
        return {"success": True}

    def set_swift_meta_container(self, container):
        """Generate test swift metadata for a container."""
        self.cont_meta[container] = {}
        self.obj_meta[container] = {}
        self.cont_meta[container]["Acc_example"] = "example"

    def set_swift_meta_object(self, container, obj):
        """Generate test swift metadata for an object."""
        self.obj_meta[container][obj] = {}
        self.obj_meta[container][obj]["Obj_example"] = "example"

    def set_s3_meta_object(self, container, obj):
        """Generate test s3 metadata for an object."""
        self.obj_meta[container][obj] = {}
        self.obj_meta[container][obj]["Obj_S3_example"] = \
            "atime:1536648772/ctime:1536648921/gid:101/gname:example"


class Mock_Session:
    """
    Mock-up class for the Openstack keystoneauth1 session instance.

    It contains the relevant methods for querying the OS identity API (aka.
    keystone).
    """

    def __init__(self):
        """Initialize Mock session."""
        self.auth = None

    def invalidate(self, _):
        """Mock session invalidation."""
        return True

    def get_user_id(self):
        """Fetch the user id from the mock OS Session."""
        return "test_user_id"

    def get_endpoint(self, service_type=None):
        """Fetch a service endpoint from the mock OS Session."""
        return "https://object.example-os.com:443/swift/v1/AUTH_example"
