"""
Module for testing ``s3browser.server``.

Contains the tests for ``front.py``.
"""


import os


import pytest
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop


from s3browser.server import servinit
from s3browser.settings import setd


# Set static folder in settings so it can be tested
setd['static_directory'] = os.getcwd() + '/s3browser_frontend'


@pytest.mark.asyncio
async def test_servinit():
    """Test server initialization function execution."""
    # Don't really need much testing here, if the server initialization
    # executes to the end all is fine.
    app = await servinit()
    assert app is not None  # nosec


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
        assert response.status != 404  # nosec
        response = await self.client.request("GET", '/browse')
        assert response.status != 404  # nosec
        response = await self.client.request("GET", '/login')
        assert response.status != 404  # nosec
        response = await self.client.request("GET", '/login/kill')
        assert response.status != 404  # nosec
        response = await self.client.request("GET", '/login/front')
        assert response.status != 404  # nosec
        response = await self.client.request("GET", '/login/rescope')
        assert response.status != 404  # nosec
        response = await self.client.request("GET", '/api/buckets')
        assert response.status != 404  # nosec
        response = await self.client.request("GET", '/api/objects')
        assert response.status != 404  # nosec
        response = await self.client.request("GET", '/api/dload')
        assert response.status != 404  # nosec
        response = await self.client.request("GET", '/api/username')
        assert response.status != 404  # nosec
        response = await self.client.request("GET", '/api/projects')
        assert response.status != 404  # nosec
        response = await self.client.request("GET", '/api/meta')
        assert response.status != 404  # nosec
        # Test all the static folders as well
        response = await self.client.request("GET", '/static/index.html')
        assert response.status != 404  # nosec
        response = await self.client.request("GET", '/static/browse.html')
        assert response.status != 404  # nosec
        response = await self.client.request("GET", '/static/login.html')
        assert response.status != 404  # nosec
        response = await self.client.request("GET", '/static/css/login.css')
        assert response.status != 404  # nosec
        response = await self.client.request("GET", '/static/css/browse.css')
        assert response.status != 404  # nosec
        response = await self.client.request("GET", '/static/js/browse.js')
        assert response.status != 404  # nosec
        response = await self.client.request("GET", '/static/js/btablecomp.js')
        assert response.status != 404  # nosec
