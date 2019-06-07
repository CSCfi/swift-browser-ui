"""
This module contains the mock-up classes and functions, used for testing the
s3browser package.
"""


import random
import hashlib
import os
import time
from swiftclient import ClientException


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
                raise ClientException(
                    msg="",
                )
        else:
            return None

    def stat(self, container=None, objects=None):
        """
        Mock function for the stat() call of the represented class
        """
        ret = {}
        # Add the tempurl headers to the return dictionary, if they have been
        # initialized
        if self.tempurl_key_1 is not None:
            pass
        if self.tempurl_key_2 is not None:
            pass

        return ret


class Mock_Session:
    """
    Mock--up class for the Openstack keystoneauth1 session instance, which
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
