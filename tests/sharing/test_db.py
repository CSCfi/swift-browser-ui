"""Test sharing backend database functions."""


import unittest
import unittest.mock
from types import SimpleNamespace

import asynctest
import asynctest.mock
import asyncpg

from swift_browser_ui.sharing.db import DBConn
import datetime


class DBConnTestClass(asynctest.TestCase):
    """Test database connection class code."""

    def setUp(self):
        """Set up necessary mocks."""
        self.asyncpg_pool_mock = SimpleNamespace(
            **{
                "close": asynctest.mock.CoroutineMock(),
                "terminate": unittest.mock.Mock(),
            }
        )

        self.asyncpg_pool_mock = asynctest.CoroutineMock(
            return_value=self.asyncpg_pool_mock,
        )
        self.patch_asyncpg_pool = unittest.mock.patch(
            "swift_browser_ui.sharing.db.asyncpg.create_pool",
            new=self.asyncpg_pool_mock,
        )

        self.asyncpg_connect_mock_connection_error = asynctest.CoroutineMock(
            side_effect=ConnectionError
        )
        self.patch_asyncpg_pool_connection_error = unittest.mock.patch(
            "swift_browser_ui.sharing.db.asyncpg.create_pool",
            new=self.asyncpg_connect_mock_connection_error,
        )

        self.asyncpg_connect_mock_invalid_pwd = asynctest.CoroutineMock(
            side_effect=asyncpg.InvalidPasswordError("Invalid")
        )
        self.patch_asyncpg_pool_invalid_password = unittest.mock.patch(
            "swift_browser_ui.sharing.db.asyncpg.create_pool",
            new=self.asyncpg_connect_mock_invalid_pwd,
        )

        self.os_environ_mock = unittest.mock.Mock(return_value=True)
        self.patch_os_environ_get = unittest.mock.patch(
            "swift_browser_ui.sharing.db.os.environ.get", new=self.os_environ_mock
        )

        self.asyncio_sleep_mock = asynctest.CoroutineMock(side_effect=Exception)
        self.patch_asyncio_sleep = unittest.mock.patch(
            "swift_browser_ui.sharing.db.asyncio.sleep", new=self.asyncio_sleep_mock
        )

        self.db = DBConn()

    def test_db_erase(self):
        """Test connection erase method."""
        mock_terminate = asynctest.mock.CoroutineMock()
        self.db.pool = SimpleNamespace(**{"terminate": mock_terminate})
        self.db.erase()
        mock_terminate.assert_called_once()
        self.assertIsNone(self.db.pool)

    async def test_db_open(self):
        """Test database connection open method."""
        with self.patch_asyncpg_pool, self.patch_os_environ_get:
            await self.db.open()
            self.assertIsNotNone(self.db.pool)
            self.asyncpg_pool_mock.assert_awaited_once()
            self.os_environ_mock.assert_called()

    async def test_db_connection_error(self):
        """Test database when connection fails."""
        with self.patch_asyncpg_pool_connection_error, self.patch_asyncio_sleep, self.patch_os_environ_get:
            with self.assertRaises(Exception):
                await self.db.open()
                self.asyncpg_connect_mock_connection_error.assert_called()
                self.asyncio_sleep_mock.assert_awaited_once()
                self.assertIsNone(self.db.pool)

    async def test_db_invalid_password(self):
        """Test database when password is invalid."""
        with self.patch_asyncpg_pool_invalid_password, self.patch_asyncio_sleep, self.patch_os_environ_get:
            with self.assertRaises(Exception):
                await self.db.open()
                self.asyncpg_connect_mock_invalid_pwd.assert_called()
                self.asyncio_sleep_mock.assert_awaited_once()
                self.assertIsNone(self.db.pool)

    async def test_db_connection_close(self):
        """Test closing the database connection."""
        with self.patch_asyncpg_pool, self.patch_os_environ_get:
            await self.db.open()
            await self.db.close()
            self.db.pool.close.assert_awaited_once()


class DBMethodTestCase(asynctest.TestCase):
    """Test database query methods."""

    def setUp(self):
        """Set up required mocks."""
        self.connection_transaction_mock = asynctest.MagicMock(
            asyncpg.Connection.transaction
        )
        mock_date = datetime.datetime(2020, 7, 15, 12, 25, 26, 791901)

        class AsyncpgConnectionMock:
            fetch = asynctest.CoroutineMock(
                return_value=[
                    {
                        "container": "test-container",
                        "container_owner": "test-owner",
                        "recipient": "test-receiver",
                        "sharingdate": mock_date,
                        "address": "test-address",
                        "r_read": True,
                        "r_write": True,
                    }
                ]
            )
            fetchrow = asynctest.CoroutineMock(
                return_value={
                    "r_read": True,
                    "r_write": True,
                    "container": "test-container",
                    "sharingdate": "15 July 2020",
                    "container_owner": "test-owner",
                    "recipient": "test-recipient",
                    "address": "test-address",
                }
            )
            execute = asynctest.CoroutineMock()
            transaction = self.connection_transaction_mock

            def __init__(self):
                """."""

            async def __aenter__(self, *args, **kwargs):
                """."""
                return self

            async def __aexit__(self, *args, **kwargs):
                """."""

        self.AsyncpgConnectionMock = AsyncpgConnectionMock

        self.asyncpg_pool_mock = SimpleNamespace(
            **{
                "fetch": asynctest.CoroutineMock(
                    return_value=[
                        {
                            "container": "test-container",
                            "container_owner": "test-owner",
                            "recipient": "test-receiver",
                            "sharingdate": mock_date,
                            "address": "test-address",
                            "r_read": True,
                            "r_write": True,
                        }
                    ]
                ),
                "fetchrow": asynctest.CoroutineMock(
                    return_value={
                        "r_read": True,
                        "r_write": True,
                        "container": "test-container",
                        "sharingdate": "15 July 2020",
                        "container_owner": "test-owner",
                        "recipient": "test-recipient",
                        "address": "test-address",
                    }
                ),
                "acquire": self.AsyncpgConnectionMock,
            }
        )

        self.db = DBConn()
        self.db.pool = self.asyncpg_pool_mock

    async def test_add_share(self):
        """Test add_share method."""
        await self.db.add_share(
            "test-owner",
            "test-container",
            ["test-user1", "test-user2", "test-user3", "test-user4"],
            ["r"],
            "http://test-address/",
        )
        self.AsyncpgConnectionMock.execute.assert_awaited()

    async def test_edit_share(self):
        """Test edit_share method."""
        await self.db.edit_share(
            "test-owner",
            "test-container",
            ["test-user1", "test-user2", "test-user3", "test-user4"],
            ["r"],
        )
        self.AsyncpgConnectionMock.execute.assert_awaited()

    async def test_delete_share(self):
        """Test delete_share method."""
        await self.db.delete_share(
            "test-owner", "test-container", ["test-user1", "test-user2", "test-user3"]
        )
        self.AsyncpgConnectionMock.execute.assert_awaited()

    async def test_delete_container_shares(self):
        """Test delete_container_shares method."""
        await self.db.delete_container_shares("test-owner", "test-container")
        self.AsyncpgConnectionMock.execute.assert_awaited()

    async def test_get_access_list(self):
        """Test get_access_list method."""
        await self.db.get_access_list("test-user")
        self.db.pool.fetch.assert_awaited_once()

    async def test_get_shared_list(self):
        """Test get_shared_list method."""
        await self.db.get_shared_list("test-user")
        self.db.pool.fetch.assert_awaited_once()

    async def test_get_access_container_details(self):
        """Test get_access_container_details method."""
        await self.db.get_access_container_details(
            "test-user", "test-owner", "test-container"
        )
        self.db.pool.fetchrow.assert_awaited_once()

    async def test_get_shared_container_details(self):
        """Test get_shared_container_details_method."""
        await self.db.get_shared_container_details("test-owner", "test-container")
        self.db.pool.fetch.assert_awaited_once()
