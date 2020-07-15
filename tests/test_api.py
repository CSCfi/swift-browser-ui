"""Module for testing sharing request API functions."""


import unittest
from types import SimpleNamespace


import aiohttp
import asynctest
from asyncpg import InterfaceError


from swift_sharing_request.api import (
    handle_share_request_post,
    handle_user_owned_request_listing,
    handle_user_made_request_listing,
    handle_container_request_listing,
    handle_user_share_request_delete
)


class APITestClass(asynctest.TestCase):
    """Test class for testing API functions."""

    def setUp(self):
        """Set up necessary mocks."""
        self.mock_request = SimpleNamespace(**{
            "app": {
                "db_conn":
                    SimpleNamespace(**{
                        "add_request": asynctest.mock.CoroutineMock(),
                        "get_request_owned": asynctest.mock.CoroutineMock(),
                        "get_request_made": asynctest.mock.CoroutineMock(),
                        "get_request_container":
                            asynctest.mock.CoroutineMock(),
                        "delete_request": asynctest.mock.CoroutineMock(),
                    })
            },
            "query": {
                "owner": "AUTH_otherexample",
            },
            "match_info": {
                "container": "test",
                "user": "test",
            }
        })

        self.json_mock = unittest.mock.MagicMock(
            aiohttp.web.json_response
        )
        self.patch_json_dump = unittest.mock.patch(
            "swift_sharing_request.api.aiohttp.web.json_response",
            new=self.json_mock
        )

    async def test_endpoint_has_access_correct(self):
        """Test the has-access endpoint for conformity."""
        with self.patch_json_dump:
            await handle_share_request_post(self.mock_request)
            self.json_mock.assert_called_once()

    async def test_endpoint_access_details_correct(self):
        """Test the access-details endpoint for conformity."""
        with self.patch_json_dump:
            await handle_user_owned_request_listing(self.mock_request)
            self.json_mock.assert_called_once()

    async def test_endpoint_gave_access_correct(self):
        """Test the gave-access endpoint for conformity."""
        with self.patch_json_dump:
            await handle_user_made_request_listing(self.mock_request)
            self.json_mock.assert_called_once()

    async def test_endpoint_shared_details_correct(self):
        """Test the shared_details endpoint for conformity."""
        with self.patch_json_dump:
            await handle_container_request_listing(self.mock_request)
            self.json_mock.assert_called_once()

    async def test_endpoint_share_container_correct(self):
        """Test the share_container endpoint for conformity."""
        self.json_mock.return_value.status = 200
        with self.patch_json_dump:
            resp = await handle_user_share_request_delete(self.mock_request)
            print(resp)


class APITestLostDatabaseConnection(asynctest.TestCase):
    """Test request backend API in database failure."""

    def setUp(self):
        """Set up necessary mocks."""
        self.mock_request = SimpleNamespace(**{
            "app": {
                "db_conn":
                    SimpleNamespace(**{
                        "add_request": asynctest.mock.Mock(
                            side_effect=InterfaceError('Lost connection')
                        ),
                        "get_request_owned": asynctest.mock.Mock(
                            side_effect=InterfaceError('Lost connection')
                        ),
                        "get_request_made": asynctest.mock.Mock(
                            side_effect=InterfaceError('Lost connection')
                        ),
                        "get_request_container": asynctest.mock.Mock(
                            side_effect=InterfaceError('Lost connection')
                        ),
                        "delete_request": asynctest.mock.Mock(
                            side_effect=InterfaceError('Lost connection')
                        ),
                    })
            },
            "query": {
                "owner": "test-owner"
            },
            "match_info": {
                "container": "test-container",
                "user": "test-user",
            }
        })

        self.handle_dropped_connection_mock = unittest.mock.Mock(
            side_effect=aiohttp.web.HTTPServiceUnavailable(
                reason="No database connection."
            )
        )
        self.patch_handle_dropped_connection = unittest.mock.patch(
            "swift_sharing_request.api.handle_dropped_connection",
            new=self.handle_dropped_connection_mock
        )

    async def test_endpoint_has_access_interface_error(self):
        """Test the has-access endpoint for dropped connection."""
        with self.patch_handle_dropped_connection:
            with self.assertRaises(aiohttp.web.HTTPServiceUnavailable):
                await handle_share_request_post(self.mock_request)
        self.handle_dropped_connection_mock.assert_called_once()

    async def test_endpoint_access_details_interface_error(self):
        """Test the access-details endpoint for dropped connection."""
        with self.patch_handle_dropped_connection:
            with self.assertRaises(aiohttp.web.HTTPServiceUnavailable):
                await handle_user_owned_request_listing(self.mock_request)
        self.handle_dropped_connection_mock.assert_called_once()

    async def test_endpoint_gave_access_interface_error(self):
        """Test the gave-access endpoint for dropped connection."""
        with self.patch_handle_dropped_connection:
            with self.assertRaises(aiohttp.web.HTTPServiceUnavailable):
                await handle_user_made_request_listing(self.mock_request)
        self.handle_dropped_connection_mock.assert_called_once()

    async def test_endpoint_shared_details_interface_error(self):
        """Test the shared-details endpoint for dropped connection."""
        with self.patch_handle_dropped_connection:
            with self.assertRaises(aiohttp.web.HTTPServiceUnavailable):
                await handle_container_request_listing(self.mock_request)
        self.handle_dropped_connection_mock.assert_called_once()

    async def test_endpoint_add_share_interface_error(self):
        """Test the add-share endpoint for dropped connection."""
        with self.patch_handle_dropped_connection:
            with self.assertRaises(aiohttp.web.HTTPServiceUnavailable):
                await handle_user_share_request_delete(self.mock_request)
        self.handle_dropped_connection_mock.assert_called_once()
