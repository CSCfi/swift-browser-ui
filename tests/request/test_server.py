"""Module for testing server.py."""


import unittest
import aiohttp


from swift_browser_ui.request.server import (
    init_server,
    run_server_devel,
    main,
)


class ServerTestCase(unittest.IsolatedAsyncioTestCase):
    """Test case for testing server module functions."""

    async def test_init_server(self):
        """Test init_server function."""
        app = await init_server()
        self.assertIsInstance(app, aiohttp.web.Application)

    async def test_run_server_devel(self):
        """Test server development mode launch function."""
        run_app_mock = unittest.mock.MagicMock(aiohttp.web.run_app)
        run_app_patch = unittest.mock.patch(
            "swift_browser_ui.request.server.aiohttp.web.run_app", new=run_app_mock
        )
        with run_app_patch:
            run_server_devel(None)
            run_app_mock.assert_called_once()

    async def test_main_wrong_version(self):
        """Test main function call when Python version is too old."""
        sys_version_patch = unittest.mock.patch(
            "swift_browser_ui.request.server.sys.version_info", new=(3, 5)
        )
        sys_exit_mock = unittest.mock.Mock(side_effect=KeyboardInterrupt)
        sys_exit_patch = unittest.mock.patch(
            "swift_browser_ui.request.server.sys.exit", new=sys_exit_mock
        )
        with sys_version_patch, sys_exit_patch:
            with self.assertRaises(KeyboardInterrupt):
                main()
                sys_exit_mock.assert_called_once()

    async def test_main_correct_version(self):
        """Test main function call when all is correct."""
        run_server_mock = unittest.mock.Mock()
        run_server_patch = unittest.mock.patch(
            "swift_browser_ui.request.server.run_server_devel", new=run_server_mock
        )
        init_server_patch = unittest.mock.Mock()
        init_server_patch = unittest.mock.patch(
            "swift_browser_ui.request.server.init_server", new=init_server_patch
        )
        with run_server_patch, init_server_patch:
            main()
            run_server_mock.assert_called_once()
