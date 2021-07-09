"""Module for testing server.py."""


from types import SimpleNamespace
import unittest.mock


import asynctest
import aiohttp


from swift_sharing_request.server import (
    resume_on_start,
    graceful_shutdown,
    init_server,
    run_server_devel,
    main
)
from swift_sharing_request.db import DBConn


class ServerTestCase(asynctest.TestCase):
    """Test case for testing server module functions."""

    def setUp(self):
        """Set up relevant mocks."""
        self.mock_db_conn = SimpleNamespace(**{
            "open": asynctest.CoroutineMock(),
            "close": asynctest.CoroutineMock(),
        })

        self.mock_application = {
            "db_conn": self.mock_db_conn
        }

    async def test_resume_on_start(self):
        """Test resume on start function."""
        await resume_on_start(self.mock_application)
        self.mock_db_conn.open.assert_awaited_once()

    async def test_graceful_shutdown(self):
        """Test graceful shutdown function."""
        await graceful_shutdown(self.mock_application)
        self.mock_db_conn.close.assert_awaited_once()

    async def test_init_server(self):
        """Test init_server function."""
        app = await init_server()
        self.assertIsInstance(app, aiohttp.web.Application)
        self.assertIsInstance(app["db_conn"], DBConn)
        self.assertIsNotNone(app["tokens"])

    async def test_run_server_devel(self):
        """Test server development mode launch function."""
        run_app_mock = unittest.mock.MagicMock(
            aiohttp.web.run_app
        )
        run_app_patch = unittest.mock.patch(
            "swift_sharing_request.server.aiohttp.web.run_app",
            new=run_app_mock
        )
        with run_app_patch:
            run_server_devel(None)
            run_app_mock.assert_called_once()

    async def test_main_wrong_version(self):
        """Test main function call when Python version is too old."""
        sys_version_patch = unittest.mock.patch(
            "swift_sharing_request.server.sys.version_info",
            new=(3, 5)
        )
        sys_exit_mock = unittest.mock.Mock(
            side_effect=KeyboardInterrupt
        )
        sys_exit_patch = unittest.mock.patch(
            "swift_sharing_request.server.sys.exit",
            new=sys_exit_mock
        )
        with sys_version_patch, sys_exit_patch:
            with self.assertRaises(KeyboardInterrupt):
                main()
                sys_exit_mock.assert_called_once()

    async def test_main_correct_version(self):
        """Test main function call when all is correct."""
        run_server_mock = unittest.mock.Mock()
        run_server_patch = unittest.mock.patch(
            "swift_sharing_request.server.run_server_devel",
            new=run_server_mock
        )
        init_server_patch = unittest.mock.Mock()
        init_server_patch = unittest.mock.patch(
            "swift_sharing_request.server.init_server",
            new=init_server_patch
        )
        with run_server_patch, init_server_patch:
            main()
            run_server_mock.assert_called_once()
