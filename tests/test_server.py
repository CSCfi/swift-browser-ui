"""
Module for testing ``swift_browser_ui.server``.

Contains the tests for ``front.py``.
"""


import os

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
import asynctest

from swift_browser_ui.server import servinit
from swift_browser_ui.settings import setd


# Set static folder in settings so it can be tested
setd['static_directory'] = os.getcwd() + '/swift_browser_ui_frontend'


class TestServinitMethod(asynctest.TestCase):
    """Small test case for servinit."""

    async def test_servinit(self):
        """Test server initialization function execution."""
        # Don't really need much testing here, if the server initialization
        # executes to the end all is fine.
        app = await servinit()
        self.assertTrue(app is not None)


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
        response = await self.client.request("GET", '/')
        self.assertNotEqual(response.status, 404)
        response = await self.client.request("GET", '/browse')
        self.assertNotEqual(response.status, 404)
        response = await self.client.request("GET", '/login')
        self.assertNotEqual(response.status, 404)
        response = await self.client.request("GET", '/login/kill')
        self.assertNotEqual(response.status, 404)
        response = await self.client.request("GET", '/login/front')
        self.assertNotEqual(response.status, 404)
        response = await self.client.request("GET", '/login/rescope')
        self.assertNotEqual(response.status, 404)
        response = await self.client.request("GET", '/api/buckets')
        self.assertNotEqual(response.status, 404)
        response = await self.client.request("GET", '/api/objects')
        self.assertNotEqual(response.status, 404)
        response = await self.client.request("GET", '/api/dload')
        self.assertNotEqual(response.status, 404)
        response = await self.client.request("GET", '/api/username')
        self.assertNotEqual(response.status, 404)
        response = await self.client.request("GET", '/api/projects')
        self.assertNotEqual(response.status, 404)
        response = await self.client.request("GET", '/api/meta')
        self.assertNotEqual(response.status, 404)
        response = await self.client.request("GET", '/api/get-project-meta')
        self.assertNotEqual(response.status, 404)
        # Test all the static folders as well
        response = await self.client.request("GET", '/static/index.html')
        self.assertNotEqual(response.status, 404)
        response = await self.client.request("GET", '/static/browse.html')
        self.assertNotEqual(response.status, 404)
        response = await self.client.request("GET", '/static/login.html')
        self.assertNotEqual(response.status, 404)
        response = await self.client.request("GET", '/static/css/login.css')
        self.assertNotEqual(response.status, 404)
        response = await self.client.request("GET", '/static/css/browse.css')
        self.assertNotEqual(response.status, 404)
        response = await self.client.request("GET", '/static/js/browse.js')
        self.assertNotEqual(response.status, 404)
        response = await self.client.request("GET", '/static/js/btablecomp.js')
        self.assertNotEqual(response.status, 404)
