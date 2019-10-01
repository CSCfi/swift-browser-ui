"""Test sharing backend server functions."""


import unittest
import unittest.mock


import aiohttp.web
import asynctest


from swift_x_account_sharing.server import (
    init_server,
    run_server_devel
)


class TestInitServer(asynctest.TestCase):
    """Test case for server initialization."""

    async def test_init_server(self):
        """Test the init_server function."""
        app = await init_server()
        self.assertTrue(app is not None)


class TestRunServerFunctions(unittest.TestCase):
    """Test case for server run functions."""

    def test_run_server_devel(self):
        """Test the development mode run server function."""
        run_app_mock = unittest.mock.MagicMock(aiohttp.web.run_app)
        with unittest.mock.patch(
                "swift_x_account_sharing.server.aiohttp.web.run_app",
                new=run_app_mock
        ):
            run_server_devel(None)
            run_app_mock.assert_called_once()
