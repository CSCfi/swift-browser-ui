"""
Module for testing ``swift_browser_ui.server``.

Contains the tests for ``front.py``.
"""


import os
import unittest
import ssl

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
import aiohttp
import asynctest

from swift_browser_ui.server import servinit, run_server_insecure
from swift_browser_ui.server import kill_sess_on_shutdown, run_server_secure
from swift_browser_ui.settings import setd

from .creation import get_request_with_mock_openstack


# Set static folder in settings so it can be tested
setd["static_directory"] = os.getcwd() + "/swift_browser_ui_frontend"


class TestServinitMethod(asynctest.TestCase):
    """Small test case for servinit."""

    async def test_servinit(self):
        """Test server initialization function execution."""
        # Don't really need much testing here, if the server initialization
        # executes to the end all is fine.
        app = await servinit()
        self.assertTrue(app is not None)


class TestServerShutdownHandler(asynctest.TestCase):
    """Test case for the server graceful shutdown handler."""

    async def test_kill_sess_on_shutdown(self):
        """Test kill_sess_on_shutdown function."""
        session, req = get_request_with_mock_openstack()

        await kill_sess_on_shutdown(req.app)

        self.assertNotIn(session, req.app["Sessions"])


class TestRunServerFunctions(unittest.TestCase):
    """Test class for server run functions."""

    @staticmethod
    def mock_ssl_context_creation(purpose=None):
        """Return a MagicMock instance of an ssl context."""
        return unittest.mock.MagicMock(ssl.create_default_context)()

    def test_run_server_secure(self):
        """Test run_server_secure function."""
        run_app_mock = unittest.mock.MagicMock(aiohttp.web.run_app)
        patch_run_app = unittest.mock.patch(
            "swift_browser_ui.server.aiohttp.web.run_app", run_app_mock
        )
        patch_ssl_defcontext = unittest.mock.patch(
            "swift_browser_ui.server.ssl.create_default_context",
            self.mock_ssl_context_creation,
        )
        with patch_run_app, patch_ssl_defcontext:
            run_server_secure(None, None, None)
            run_app_mock.assert_called_once()

    def test_run_server_insecure(self):
        """Test run_server_insecure function."""
        run_app_mock = unittest.mock.MagicMock(aiohttp.web.run_app)
        with unittest.mock.patch(
            "swift_browser_ui.server.aiohttp.web.run_app", run_app_mock
        ):
            run_server_insecure(None)
            run_app_mock.assert_called_once()


# After testing the server initialization, we can use the correctly starting
# server for testing other modules.
class AppTestCase(AioHTTPTestCase):
    """
    Test Web app.

    Testing web app endpoints.
    """

    async def get_application(self):
        """Retrieve web Application for test."""
        return await servinit()

    @unittest_run_loop
    async def test_working_routes(self):
        """
        Test all the specified server routes.

        All routes need to
        work in order for the test to pass, i.e. no 404
        is allowed from any of the
        specified routes in the application back-end.
        """
        # OPINION: this unit test will fail on the first
        # encountered broken route,
        # and thus won't check the others.
        # In my opinion it's fine, since the
        # broken routes can be fixed one at a time.
        # Having all the route checks in
        # a single compact function is better overall. – Sampsa Penna
        new_setd = {"static_directory": os.getcwd() + "/swift_browser_ui_frontend/dist"}
        patch_setd_front = unittest.mock.patch(
            "swift_browser_ui.front.setd",
            new=new_setd,
        )
        patch_setd_middleware = unittest.mock.patch(
            "swift_browser_ui.middlewares.setd",
            new=new_setd,
        )
        patch_setd_login = unittest.mock.patch(
            "swift_browser_ui.login.setd",
            new=new_setd,
        )
        with patch_setd_front, patch_setd_middleware, patch_setd_login:
            response = await self.client.request("GET", "/")
            self.assertNotEqual(response.status, 404)
            response = await self.client.request("GET", "/browse")
            self.assertNotEqual(response.status, 404)
            response = await self.client.request("GET", "/login")
            self.assertNotEqual(response.status, 404)
            response = await self.client.request("GET", "/login/kill")
            self.assertNotEqual(response.status, 404)
            response = await self.client.request("GET", "/login/front")
            self.assertNotEqual(response.status, 404)
            response = await self.client.request("GET", "/login/rescope")
            self.assertNotEqual(response.status, 404)
            response = await self.client.request("GET", "/api/buckets")
            self.assertNotEqual(response.status, 404)
            response = await self.client.request("GET", "/api/bucket/objects")
            self.assertNotEqual(response.status, 404)
            response = await self.client.request("GET", "/api/object/dload")
            self.assertNotEqual(response.status, 404)
            response = await self.client.request("GET", "/api/username")
            self.assertNotEqual(response.status, 404)
            response = await self.client.request("GET", "/api/projects")
            self.assertNotEqual(response.status, 404)
            response = await self.client.request("GET", "/api/bucket/meta")
            self.assertNotEqual(response.status, 404)
            response = await self.client.request(
                "GET",
                "/api/project/meta",
            )
            self.assertNotEqual(response.status, 404)
