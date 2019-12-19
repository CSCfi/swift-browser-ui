"""Test sharing backend database functions."""


import unittest


import asynctest
import asyncpg


from swift_x_account_sharing.db import DBConn


class DBConnTestClass(asynctest.TestCase):
    """Test database connection class code."""

    def setUp(self):
        """Set up necessary mocks."""
        self.asyncpg_connection_mock = asynctest.MagicMock(
            asyncpg.Connection
        )
        self.patch_asyncpg_connection = unittest.mock.patch(
            "swift_x_account_sharing.db.asyncpg.Connection",
            new=self.asyncpg_connection_mock
        )

        self.asyncpg_connect_mock = asynctest.CoroutineMock(
            return_value=self.asyncpg_connection_mock(),
        )
        self.patch_asyncpg_connect = unittest.mock.patch(
            "swift_x_account_sharing.db.asyncpg.connect",
            new=self.asyncpg_connect_mock
        )

        self.asyncpg_connect_mock_connection_error = asynctest.CoroutineMock(
            side_effect=ConnectionError
        )
        self.patch_asyncpg_connect_connection_error = unittest.mock.patch(
            "swift_x_account_sharing.db.asyncpg.connect",
            new=self.asyncpg_connect_mock_connection_error
        )

        self.asyncpg_connect_mock_invalid_pwd = asynctest.CoroutineMock(
            side_effect=asyncpg.InvalidPasswordError("Invalid")
        )
        self.patch_asyncpg_connect_invalid_password = unittest.mock.patch(
            "swift_x_account_sharing.db.asyncpg.connect",
            new=self.asyncpg_connect_mock_invalid_pwd
        )

        self.os_environ_mock = unittest.mock.Mock(
            return_value=True
        )
        self.patch_os_environ_get = unittest.mock.patch(
            "swift_x_account_sharing.db.os.environ.get",
            new=self.os_environ_mock
        )

        self.asyncio_sleep_mock = asynctest.CoroutineMock(
            side_effect=Exception
        )
        self.patch_asyncio_sleep = unittest.mock.patch(
            "swift_x_account_sharing.db.asyncio.sleep",
            new=self.asyncio_sleep_mock
        )

        self.db = DBConn()

    def test_db_erase(self):
        """Test connection erase method."""
        self.db.conn = True
        self.db.erase()
        self.assertIsNone(self.db.conn)

    async def test_db_open(self):
        """Test database connection open method."""
        with self.patch_asyncpg_connection, \
                self.patch_asyncpg_connect, \
                self.patch_os_environ_get:
            await self.db.open()
            self.assertIsNotNone(self.db.conn)
            self.asyncpg_connect_mock.assert_awaited_once()
            self.os_environ_mock.assert_called()

    async def test_db_connection_error(self):
        """Test database when connection fails."""
        with self.patch_asyncpg_connection, \
                self.patch_asyncpg_connect_connection_error, \
                self.patch_asyncio_sleep, \
                self.patch_os_environ_get:
            with self.assertRaises(Exception):
                await self.db.open()
                self.asyncpg_connect_mock_connection_error.assert_called()
                self.asyncio_sleep_mock.assert_awaited_once()
                self.assertIsNone(self.db.conn)

    async def test_db_invalid_password(self):
        """Test database when password is invalid."""
        with self.patch_asyncpg_connection, \
                self.patch_asyncpg_connect_invalid_password, \
                self.patch_asyncio_sleep, \
                self.patch_os_environ_get:
            with self.assertRaises(Exception):
                await self.db.open()
                self.asyncpg_connect_mock_invalid_pwd.assert_called()
                self.asyncio_sleep_mock.assert_awaited_once()
                self.assertIsNone(self.db.conn)
