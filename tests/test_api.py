"""Test sharing backend API functions."""


import asyncio
from types import SimpleNamespace


import unittest.mock
import asynctest
import aiohttp.web


from asyncpg import InterfaceError


from swift_x_account_sharing.api import (
    handle_dropped_connection,
    has_access_handler,
    access_details_handler,
    gave_access_handler,
    shared_details_handler,
    share_container_handler,
    edit_share_handler,
    delete_share_handler
)


class APITestClass(asynctest.TestCase):
    """Test the sharing backend public API."""

    def setUp(self):
        """Set up necessary mocks."""
        self.mock_request = SimpleNamespace(**{
            "app": {
                "db_conn": SimpleNamespace(**{
                    "add_share": asynctest.CoroutineMock(),
                    "edit_share": asynctest.CoroutineMock(),
                    "delete_share": asynctest.CoroutineMock(),
                    "get_access_list": asynctest.CoroutineMock(),
                    "get_shared_list": asynctest.CoroutineMock(),
                    "get_access_container_details": asynctest.CoroutineMock(),
                    "get_shared_container_details": asynctest.CoroutineMock(),
                }),
            },
            "query": {
                "user": "AUTH_example",
                "owner": "AUTH_otherexample",
                "container": "test-container-1",
                "access": "r,w,l",
                "address": "https://placeholder.os:443"
            },
            "match_info": {
                "container": "test",
                "user": "test",
                "owner": "test"
            }
        })

        self.json_mock = unittest.mock.MagicMock(
            aiohttp.web.json_response
        )
        self.patch_json_dump = unittest.mock.patch(
            "swift_x_account_sharing.api.aiohttp.web.json_response",
            new=self.json_mock
        )

        self.ensure_future_mock = unittest.mock.MagicMock(
            asyncio.ensure_future
        )
        self.patch_asyncio_ensure_future = unittest.mock.patch(
            "swift_x_account_sharing.api.asyncio.ensure_future",
            new=self.ensure_future_mock
        )

    async def test_handle_dropped_connection(self):
        """Test handling dropped connection."""
        self.mock_request.app["db_conn"] = SimpleNamespace(**{
            "erase": unittest.mock.Mock(),
            "open": asynctest.mock.Mock(),
        })
        with self.patch_asyncio_ensure_future:
            with self.assertRaises(aiohttp.web.HTTPServiceUnavailable):
                await handle_dropped_connection(self.mock_request)
            self.mock_request.app["db_conn"].erase.assert_called_once()
            self.mock_request.app["db_conn"].open.assert_called_once()

    async def test_endpoint_has_access_correct(self):
        """Test the has-access endpoint for conformity."""
        with self.patch_json_dump:
            await has_access_handler(self.mock_request)
            self.json_mock.assert_called_once()

    async def test_endpoint_access_details_correct(self):
        """Test the access-details endpoint for conformity."""
        with self.patch_json_dump:
            await access_details_handler(self.mock_request)
            self.json_mock.assert_called_once()

    async def test_endpoint_gave_access_correct(self):
        """Test the gave-access endpoint for conformity."""
        with self.patch_json_dump:
            await gave_access_handler(self.mock_request)
            self.json_mock.assert_called_once()

    async def test_endpoint_shared_details_correct(self):
        """Test the shared_details endpoint for conformity."""
        with self.patch_json_dump:
            await shared_details_handler(self.mock_request)
            self.json_mock.assert_called_once()

    async def test_endpoint_share_container_correct(self):
        """Test the share_container endpoint for conformity."""
        self.json_mock.return_value.status = 204
        with self.patch_json_dump:
            resp = await share_container_handler(self.mock_request)
            self.assertEqual(resp.status, 204)

    async def test_endpoint_edit_share_correct(self):
        """Test the edit_share endpoint for conformity."""
        with self.patch_json_dump:
            await edit_share_handler(self.mock_request)
            self.json_mock.assert_called_once()

    async def test_endpoint_delete_share_correct(self):
        """Test the delete_share endpoint for conformmity."""
        with self.patch_json_dump:
            resp = await delete_share_handler(self.mock_request)
            self.assertEqual(resp.status, 204)


class APILostDatabaseConnectionClass(asynctest.TestCase):
    """Test the sharing backend API upon database failure."""

    def setUp(self):
        """Set up necessary mocks."""
        self.mock_request = SimpleNamespace(**{
            "app": {
                "db_conn":
                    SimpleNamespace(**{
                        "get_access_list": asynctest.mock.Mock(
                            side_effect=InterfaceError('Lost connection')
                        ),
                        "get_access_container_details": asynctest.mock.Mock(
                            side_effect=InterfaceError('Lost connection')
                        ),
                        "get_shared_list": asynctest.mock.Mock(
                            side_effect=InterfaceError('Lost connection')
                        ),
                        "get_shared_container_details": asynctest.mock.Mock(
                            side_effect=InterfaceError('Lost connection')
                        ),
                        "add_share": asynctest.mock.Mock(
                            side_effect=InterfaceError('Lost connection')
                        ),
                        "edit_share": asynctest.mock.Mock(
                            side_effect=InterfaceError('Lost connection')
                        ),
                        "delete_share": asynctest.mock.Mock(
                            side_effect=InterfaceError('Lost connection')
                        ),
                    })
            },
            "query": {
                "user": "AUTH_example",
                "owner": "AUTH_otherexample",
                "container": "test-container-1",
                "access": "r,w,l",
                "address": "https://placeholder.os:443"
            },
            "match_info": {
                "container": "test",
                "user": "test",
                "owner": "test"
            }
        })

        self.handle_dropped_connection_mock = unittest.mock.Mock(
            side_effect=aiohttp.web.HTTPServiceUnavailable(
                reason="No database connection."
            )
        )
        self.patch_handle_dropped_connection = unittest.mock.patch(
            "swift_x_account_sharing.api.handle_dropped_connection",
            new=self.handle_dropped_connection_mock
        )

    async def test_endpoint_has_access_interface_error(self):
        """Test the has-access endpoint for dropped connection."""
        with self.patch_handle_dropped_connection:
            with self.assertRaises(aiohttp.web.HTTPServiceUnavailable):
                await has_access_handler(self.mock_request)
        self.handle_dropped_connection_mock.assert_called_once()

    async def test_endpoint_access_details_interface_error(self):
        """Test the access-details endpoint for dropped connection."""
        with self.patch_handle_dropped_connection:
            with self.assertRaises(aiohttp.web.HTTPServiceUnavailable):
                await access_details_handler(self.mock_request)
        self.handle_dropped_connection_mock.assert_called_once()

    async def test_endpoint_gave_access_interface_error(self):
        """Test the gave-access endpoint for dropped connection."""
        with self.patch_handle_dropped_connection:
            with self.assertRaises(aiohttp.web.HTTPServiceUnavailable):
                await gave_access_handler(self.mock_request)
        self.handle_dropped_connection_mock.assert_called_once()

    async def test_endpoint_shared_details_interface_error(self):
        """Test the shared-details endpoint for dropped connection."""
        with self.patch_handle_dropped_connection:
            with self.assertRaises(aiohttp.web.HTTPServiceUnavailable):
                await shared_details_handler(self.mock_request)
        self.handle_dropped_connection_mock.assert_called_once()

    async def test_endpoint_add_share_interface_error(self):
        """Test the add-share endpoint for dropped connection."""
        with self.patch_handle_dropped_connection:
            with self.assertRaises(aiohttp.web.HTTPServiceUnavailable):
                await share_container_handler(self.mock_request)
        self.handle_dropped_connection_mock.assert_called_once()

    async def test_endpoint_edit_share_interface_error(self):
        """Test the add-share endpoint for dropped connection."""
        with self.patch_handle_dropped_connection:
            with self.assertRaises(aiohttp.web.HTTPServiceUnavailable):
                await edit_share_handler(self.mock_request)
        self.handle_dropped_connection_mock.assert_called_once()

    async def test_endpoint_delete_share_interface_error(self):
        """Test the add-share endpoint for dropped connection."""
        with self.patch_handle_dropped_connection:
            with self.assertRaises(aiohttp.web.HTTPServiceUnavailable):
                await delete_share_handler(self.mock_request)
        self.handle_dropped_connection_mock.assert_called_once()
