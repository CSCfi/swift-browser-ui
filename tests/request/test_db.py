"""Test request backend database functions."""


import datetime
import unittest
from types import SimpleNamespace

import asyncpg


from swift_browser_ui.request.db import DBConn


class DBConnTestClass(unittest.IsolatedAsyncioTestCase):
    """Test database connection class code."""

    def setUp(self):
        """Set up necessary mocks."""
        self.asyncpg_pool_mock = SimpleNamespace(
            **{
                "close": unittest.mock.AsyncMock(),
                "terminate": unittest.mock.Mock(),
            }
        )

        self.asyncpg_pool_mock = unittest.mock.AsyncMock(
            return_value=self.asyncpg_pool_mock,
        )
        self.patch_asyncpg_pool = unittest.mock.patch(
            "swift_browser_ui.request.db.asyncpg.create_pool",
            new=self.asyncpg_pool_mock,
        )

        self.asyncpg_connect_mock_connection_error = unittest.mock.AsyncMock(
            side_effect=ConnectionError
        )
        self.patch_asyncpg_pool_connection_error = unittest.mock.patch(
            "swift_browser_ui.request.db.asyncpg.create_pool",
            new=self.asyncpg_connect_mock_connection_error,
        )

        self.asyncpg_connect_mock_invalid_pwd = unittest.mock.AsyncMock(
            side_effect=asyncpg.InvalidPasswordError("Invalid")
        )
        self.patch_asyncpg_pool_invalid_password = unittest.mock.patch(
            "swift_browser_ui.request.db.asyncpg.create_pool",
            new=self.asyncpg_connect_mock_invalid_pwd,
        )

        self.os_environ_mock = unittest.mock.Mock(return_value=True)
        self.patch_os_environ_get = unittest.mock.patch(
            "swift_browser_ui.request.db.os.environ.get", new=self.os_environ_mock
        )

        self.asyncio_sleep_mock = unittest.mock.AsyncMock(side_effect=Exception)
        self.patch_asyncio_sleep = unittest.mock.patch(
            "swift_browser_ui.request.db.asyncio.sleep", new=self.asyncio_sleep_mock
        )

        self.db = DBConn()

    def test_db_erase(self):
        """Test connection erase method."""
        mock_terminate = unittest.mock.Mock()
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


class DBMethodTestCase(unittest.IsolatedAsyncioTestCase):
    """Test database query methods."""

    def setUp(self):
        """Set up required mocks."""
        self.connection_transaction_mock = unittest.mock.MagicMock(
            asyncpg.Connection.transaction
        )

        class AsyncpgConnectionMock:
            fetch = unittest.mock.AsyncMock(
                return_value=[
                    {
                        "container": "test-container",
                        "container_owner": "test-owner",
                        "recipient": "test-receiver",
                        "created": datetime.datetime(2017, 1, 1),
                    }
                ]
            )
            fetchrow = unittest.mock.AsyncMock(
                return_value={
                    "container": "test-container",
                    "container_owner": "test-owner",
                    "recipient": "test-receiver",
                    "created": datetime.datetime(2017, 1, 1),
                }
            )
            execute = unittest.mock.AsyncMock()
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
                "fetch": unittest.mock.AsyncMock(
                    return_value=[
                        {
                            "container": "test-container",
                            "container_owner": "test-owner",
                            "recipient": "test-receiver",
                            "created": datetime.datetime(2017, 1, 1),
                        }
                    ]
                ),
                "fetchrow": unittest.mock.AsyncMock(
                    return_value={
                        "container": "test-container",
                        "container_owner": "test-owner",
                        "recipient": "test-receiver",
                        "created": datetime.datetime(2017, 1, 1),
                    }
                ),
                "acquire": self.AsyncpgConnectionMock,
            }
        )

        self.db = DBConn()
        self.db.pool = self.asyncpg_pool_mock

    async def test_add_request(self):
        """Test add_request method."""
        await self.db.add_request("test-user", "test-container", "test-owner")
        self.AsyncpgConnectionMock.execute.assert_awaited()

    async def test_get_request_owned(self):
        """Test get_request_owned method."""
        await self.db.get_request_owned("test-user")
        self.db.pool.fetch.assert_awaited()

    async def test_get_request_made(self):
        """Test get_request_made method."""
        await self.db.get_request_made("test-user")
        self.db.pool.fetch.assert_awaited()

    async def test_get_request_container(self):
        """Test get_request_container method."""
        await self.db.get_request_container("test-container")
        self.db.pool.fetch.assert_awaited()

    async def test_delete_request(self):
        """Test delete_request method."""
        await self.db.delete_request(
            "test-container",
            "test-owner",
            "test-user",
        )
        self.AsyncpgConnectionMock.execute.assert_awaited()
