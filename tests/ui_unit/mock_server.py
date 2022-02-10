"""Module for creating a server with mock-up openstack."""


import os
import logging
import typing
import unittest.mock
import random
import hashlib
import datetime
import re
import json
import asyncio

import aiohttp.web

import swift_browser_ui.ui.server


import tests.common.mockups


SESSION_MODE = bool(os.environ.get("TEST_SESSION_MODE", False))


logging.basicConfig()
logging.root.setLevel(logging.DEBUG)


class MockSwiftMiddleware(tests.common.mockups.APITestBase):
    """Mock Openstack implementation as aiohttp server middleware."""

    def setUp(self):
        """Set up mock Openstack Swift object storage contents."""
        super().setUp()
        self.containeramount = int(os.environ.get("TEST_CONTAINER_AMOUNT", 10))
        self.object_range = (0, int(os.environ.get("TEST_MAX_OBJECT_AMOUNT", 100)))
        self.size_range = (1, int(os.environ.get("TEST_MAX_OBJECT_SIZE", 1048576)))

        self.bodge_lock = None

        self.containers = {}
        self.container_meta = {}
        self.object_meta = {}

    def reinit_with_data(self):
        """Reinitialize data if user logs in again."""
        for i in range(0, self.containeramount):
            to_add = []

            # Iterate over a random amount of objects
            for _ in range(
                0,
                random.randint(  # nosec
                    self.object_range[0],
                    self.object_range[1],
                ),
            ):  # nosec
                ohash = hashlib.sha1(os.urandom(256)).hexdigest()  # nosec
                to_append = {
                    "hash": ohash,
                    "name": f"test-object-{ohash}",
                    "last_modified": datetime.datetime.now().isoformat(),
                    "bytes": random.randint(  # nosec
                        self.size_range[0],
                        self.size_range[1],
                    ),
                    "meta": {
                        "X-Object-Meta-Usertags": "objects;with;tags",
                        "X-Object-Meta-Obj-Example": "example",
                    },
                }
                to_append["content_type"] = "binary/octet-stream"
                to_add.append(to_append)

            self.containers[f"test-instance-container-{i}"] = {
                "name": f"test-instance-container-{i}",
                "count": len(to_add),
                "bytes": random.randint(0, 252000000),  # nosec
                "_objects": to_add,
                "meta": {
                    "X-Container-Meta-Obj-Example": "example",
                    "X-Container-Meta-Usertags": ";".join(
                        ("SD-Connect", "with", "container", "tags")
                    ),
                },
            }

            self.container_meta = {
                "X-Container-Meta-Obj-Example": "example",
                "X-Container-Meta-Usertags": ";".join(
                    ("SD-Connect", "with", "container", "tags")
                ),
            }
            self.object_meta = {
                "X-Object-Meta-Usertags": "objects;with;tags",
                "X-Object-Meta-Obj-Example": "example",
            }

    @aiohttp.web.middleware
    async def wrap_mock_swift(
        self,
        request: aiohttp.web.Request,
        handler: typing.Callable[
            [aiohttp.web.Request],
            typing.Coroutine[typing.Awaitable, typing.Any, aiohttp.web.Response],
        ],
    ) -> aiohttp.web.Response:
        """Replace mock aiohttp client return data based on route."""
        if self.bodge_lock is None:
            self.bodge_lock = asyncio.Lock()
        async with self.bodge_lock:
            request.app["api_client"] = self.mock_client

            self.mock_client_response.status = 200

            # Handle logins with simple redirection, we have a "session" in place already
            if request.path == "/login/kill":
                return aiohttp.web.Response(status=303, headers={"Location": "/"})
            if (
                request.path == "/login/return"
                or request.path == "/login/websso"
                or request.path == "/login/credentials"
            ):
                self.reinit_with_data()
                return aiohttp.web.Response(status=303, headers={"Location": "/browse"})

            # Handle frontend routes without patching sessions, we don't want redirections
            # for now
            mock_no_sess = unittest.mock.AsyncMock(
                side_effect=aiohttp.web.HTTPUnauthorized
            )
            p_no_sess = unittest.mock.patch(
                "aiohttp_session.get_session",
                mock_no_sess,
            )
            if (
                request.path == ""
                or request.path == "/"
                or request.path == "/loginpassword"
                or request.path == "/login"
                or request.path == "/login/front"
            ):
                with p_no_sess:
                    return await handler(request)

            # Mock overrides for api related routes, ignoring user and projects since those'
            # are available in the session object
            if request.method == "GET" and re.match(r"^/api/test-id-\d$", request.path):
                if "marker" not in request.query:
                    self.mock_iter.return_value = json.dumps(
                        list(self.containers.values())
                    ).encode("utf-8")
                else:
                    self.mock_iter.return_value = json.dumps([]).encode("utf-8")
            if re.match(r"^/api/test-id-\d/.*$", request.path):
                if request.method == "GET":
                    if "marker" not in request.query:
                        self.mock_iter.return_value = json.dumps(
                            self.containers[request.match_info["container"]]["_objects"]
                        ).encode("utf-8")
                    else:
                        self.mock_iter.return_value = json.dumps([]).encode("utf-8")
                if request.method == "POST":
                    if "objects" in request.query:
                        objects = await request.json()
                        self.object_meta = {
                            f"X-Object-Meta-{k}": v
                            for k, v in filter(lambda i: i[1], objects[0][1].items())
                        }
                        return aiohttp.web.HTTPNoContent()
                    container = await request.json()
                    self.container_meta = {
                        f"X-Container-Meta-{k}": v
                        for k, v in filter(lambda i: i[1], container.items())
                    }
                    return aiohttp.web.HTTPNoContent()
            if request.method == "GET" and re.match(
                r"^/api/meta/test-id-\d/.*$", request.path
            ):
                if "objects" in request.query:
                    print(self.object_meta)
                    self.mock_client_response.headers = self.object_meta
                else:
                    print(self.container_meta)
                    self.mock_client_response.headers = self.container_meta
            if request.method == "GET" and re.match(
                r"^/api/meta/test-id-\d$", request.path
            ):
                self.mock_client_response.status = 204
                self.mock_client_response.headers = {
                    "X-Account-Container-Count": 10,
                    "X-Account-Object-Count": 15000,
                    "X-Account-Bytes-Used": 147284563,
                }

            with self.p_get_sess:
                return await handler(request)


@unittest.mock.patch.dict(
    swift_browser_ui.ui.server.setd,
    {
        "auth_endpoint_url": "https://localhost:5001/v3",
        "has_trust": False,
        "logfile": None,
        "port": int(os.environ.get("TEST_SERVER_PORT", 8080)),
        "verbose": True,
        "debug": True,
        "set_session_devmode": SESSION_MODE,
        "static_directory": swift_browser_ui.ui.settings.__file__.replace(
            "settings.py", "static"
        ),
    },
)
def run_mock_server():
    """Run test server with mock openstack."""
    # Run the server in an ordinary fashion after patching everything
    logging.basicConfig()
    logging.root.setLevel(logging.DEBUG)

    inject = MockSwiftMiddleware()
    inject.setUp()
    inject.reinit_with_data()

    app = swift_browser_ui.ui.server.servinit(inject_middleware=[inject.wrap_mock_swift])
    swift_browser_ui.ui.server.run_server_insecure(app)


if __name__ == "__main__":
    run_mock_server()
