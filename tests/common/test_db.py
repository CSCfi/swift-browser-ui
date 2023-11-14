"""Test common database functions."""


import datetime
import unittest
from types import SimpleNamespace

import asyncpg


import swift_browser_ui.common.db


class TestDBConvenienceFunctions(unittest.IsolatedAsyncioTestCase):
    """Test convenience functions for the databases."""

    def setUp(self):
        """Set up necessary mocks."""

        self.mock_db = SimpleNamespace(
            **{
                "open": unittest.mock.AsyncMock(),
                "close": unittest.mock.AsyncMock(),
            }
        )

        self.mock_db_class_init = unittest.mock.Mock(return_value=self.mock_db)

        self.mock_app_no_db = {
            "db_class": self.mock_db_class_init,
        }
        self.mock_app_db = {
            "db_conn": self.mock_db,
        }

    async def test_db_graceful_start(self):
        """Test database graceful start function."""

        await swift_browser_ui.common.db.db_graceful_start(self.mock_app_no_db)

        self.assertIn("db_conn", self.mock_app_no_db)
        self.mock_db_class_init.assert_called_once()
        self.mock_db.open.assert_called_once()

    async def test_db_graceful_close(self):
        """Test database graceful close function."""

        await swift_browser_ui.common.db.db_graceful_close(self.mock_app_db)

        self.mock_db.close.assert_called_once()


class BaseDBConnTestClass(unittest.IsolatedAsyncioTestCase):
    """Base class for database connection tests."""

    def setUp(self):
        """Set up necessary mocks."""

        self.connection_transaction_mock = unittest.mock.MagicMock(
            asyncpg.Connection.transaction
        )

        self.asyncpg_pool_mock = unittest.mock.AsyncMock(
            return_value=SimpleNamespace(
                **{
                    "close": unittest.mock.AsyncMock(),
                    "terminate": unittest.mock.Mock(),
                }
            ),
        )
        self.patch_asyncpg_pool = unittest.mock.patch(
            "swift_browser_ui.common.db.asyncpg.create_pool",
            new=self.asyncpg_pool_mock,
        )

        self.asyncpg_connect_mock_connection_error = unittest.mock.AsyncMock(
            side_effect=ConnectionError
        )
        self.patch_asyncpg_pool_connection_error = unittest.mock.patch(
            "swift_browser_ui.common.db.asyncpg.create_pool",
            new=self.asyncpg_connect_mock_connection_error,
        )

        self.asyncpg_connect_mock_invalid_pwd = unittest.mock.AsyncMock(
            side_effect=asyncpg.InvalidPasswordError("Invalid")
        )
        self.patch_asyncpg_pool_invalid_password = unittest.mock.patch(
            "swift_browser_ui.common.db.asyncpg.create_pool",
            new=self.asyncpg_connect_mock_invalid_pwd,
        )

        self.os_environ_mock = unittest.mock.Mock(return_value=True)
        self.patch_os_environ_get = unittest.mock.patch(
            "swift_browser_ui.common.db.os.environ.get", new=self.os_environ_mock
        )

        self.asyncio_sleep_mock = unittest.mock.AsyncMock(side_effect=Exception)
        self.patch_asyncio_sleep = unittest.mock.patch(
            "swift_browser_ui.common.db.sleep_random", new=self.asyncio_sleep_mock
        )


class TestBaseDB(BaseDBConnTestClass):
    """Test common db functions available in the base class."""

    def setUp(self):
        super().setUp()
        # Using UploadDBConn, as it's the barebones version without any
        # additional methods
        self.db = swift_browser_ui.common.db.SharingDBConn()

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


class RequestDBConnTestClass(BaseDBConnTestClass):
    """Test request database connection class code."""

    def setUp(self):
        """Set up required mocks."""
        super().setUp()

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

        self.db = swift_browser_ui.common.db.RequestDBConn()
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


class SharingDBConnTestClass(BaseDBConnTestClass):
    """Test sharing database connection class code."""

    def setUp(self):
        """Set up required mocks."""

        super().setUp()

        mock_date = datetime.datetime(2020, 7, 15, 12, 25, 26, 791901)

        class AsyncpgConnectionMock:
            fetch = unittest.mock.AsyncMock(
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
            fetchrow = unittest.mock.AsyncMock(
                return_value={
                    "r_read": True,
                    "r_write": True,
                    "container": "test-container",
                    "sharingdate": mock_date,
                    "container_owner": "test-owner",
                    "recipient": "test-recipient",
                    "address": "test-address",
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
                            "sharingdate": mock_date,
                            "address": "test-address",
                            "r_read": True,
                            "r_write": True,
                        }
                    ]
                ),
                "fetchrow": unittest.mock.AsyncMock(
                    return_value={
                        "r_read": True,
                        "r_write": True,
                        "container": "test-container",
                        "sharingdate": mock_date,
                        "container_owner": "test-owner",
                        "recipient": "test-recipient",
                        "address": "test-address",
                    }
                ),
                "acquire": self.AsyncpgConnectionMock,
            }
        )

        self.db = swift_browser_ui.common.db.SharingDBConn()
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
