"""Test sharing backend database functions."""


import unittest
from types import SimpleNamespace
import asyncio

import asynctest
import asyncpg
import aiohttp.web

from swift_x_account_sharing.db import DBConn
from swift_x_account_sharing.db import handle_dropped_connection


class HandleDroppedTestClass(asynctest.TestCase):
    """Test class for dropped connection handling."""

    def setUp(self):
        """Set up necessary mocks."""
        self.mock_request = SimpleNamespace(**{
            "app": {
                "db_conn": SimpleNamespace(**{
                    "erase": unittest.mock.Mock(),
                    "open": asynctest.mock.Mock(),
                }),
            },
        })

        self.ensure_future_mock = unittest.mock.MagicMock(
            asyncio.ensure_future
        )
        self.patch_asyncio_ensure_future = unittest.mock.patch(
            "swift_x_account_sharing.db.asyncio.ensure_future",
            new=self.ensure_future_mock
        )

    async def test_handle_dropped_connection(self):
        """Test handling dropped connection."""
        with self.patch_asyncio_ensure_future:
            with self.assertRaises(aiohttp.web.HTTPServiceUnavailable):
                await handle_dropped_connection(self.mock_request)
            self.mock_request.app["db_conn"].erase.assert_called_once()
            self.mock_request.app["db_conn"].open.assert_called_once()


class DBConnTestClass(asynctest.TestCase):
    """Test database connection class code."""

    def setUp(self):
        """Set up necessary mocks."""
        self.asyncpg_connection_mock = SimpleNamespace(**{
            "close": asynctest.CoroutineMock()
        })
        self.patch_asyncpg_connection = unittest.mock.patch(
            "swift_x_account_sharing.db.asyncpg.Connection",
            new=self.asyncpg_connection_mock
        )

        self.asyncpg_connect_mock = asynctest.CoroutineMock(
            return_value=self.asyncpg_connection_mock,
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

    async def test_db_connection_close(self):
        """Test closing the database connection."""
        with self.patch_asyncpg_connection, \
                self.patch_asyncpg_connect, \
                self.patch_os_environ_get:
            await self.db.open()
            await self.db.close()
            self.db.conn.close.assert_awaited_once()


class DBMethodTestCase(asynctest.TestCase):
    """Test database query methods."""

    def setUp(self):
        """Set up required mocks."""
        self.connection_transaction_mock = asynctest.MagicMock(
            asyncpg.Connection.transaction
        )

        self.asyncpg_connection_mock = SimpleNamespace(**{
            "fetch": asynctest.CoroutineMock(
                return_value=[{
                    "container": "test-container",
                    "container_owner": "test-owner",
                    "recipient": "test-receiver",
                    "sharingdate": "testdate",
                    "address": "test-address",
                    "r_read": True,
                    "r_write": True,
                }]
            ),
            "fetchrow": asynctest.CoroutineMock(
                return_value={
                    "r_read": True,
                    "r_write": True,
                    "container": "test-container",
                    "sharingdate": "testdate",
                    "container_owner": "test-owner",
                    "recipient": "test-recipient",
                    "address": "test-address",
                }
            ),
            "execute": asynctest.CoroutineMock(),
            "transaction": self.connection_transaction_mock
        })

        self.db = DBConn()
        self.db.conn = self.asyncpg_connection_mock

    async def test_add_share(self):
        """Test add_share method."""
        await self.db.add_share(
            "test-owner",
            "test-container",
            ["test-user1", "test-user2", "test-user3", "test-user4"],
            ["r"],
            "http://test-address/"
        )
        self.db.conn.execute.assert_awaited()

    async def test_edit_share(self):
        """Test edit_share method."""
        await self.db.edit_share(
            "test-owner",
            "test-container",
            ["test-user1", "test-user2", "test-user3", "test-user4"],
            ["r"]
        )
        self.db.conn.execute.assert_awaited()

    async def test_delete_share(self):
        """Test delete_share method."""
        await self.db.delete_share(
            "test-owner",
            "test-container",
            ["test-user1", "test-user2", "test-user3"]
        )
        self.db.conn.execute.assert_awaited()

    async def test_delete_container_shares(self):
        """Test delete_container_shares method."""
        await self.db.delete_container_shares(
            "test-owner",
            "test-container"
        )
        self.db.conn.execute.assert_awaited()

    async def test_get_access_list(self):
        """Test get_access_list method."""
        await self.db.get_access_list(
            "test-user"
        )
        self.db.conn.fetch.assert_awaited_once()

    async def test_get_shared_list(self):
        """Test get_shared_list method."""
        await self.db.get_shared_list(
            "test-user"
        )
        self.db.conn.fetch.assert_awaited_once()

    async def test_get_access_container_details(self):
        """Test get_access_container_details method."""
        await self.db.get_access_container_details(
            "test-user",
            "test-owner",
            "test-container"
        )
        self.db.conn.fetchrow.assert_awaited_once()

    async def test_get_shared_container_details(self):
        """Test get_shared_container_details_method."""
        await self.db.get_shared_container_details(
            "test-owner",
            "test-container"
        )
        self.db.conn.fetch.assert_awaited_once()
