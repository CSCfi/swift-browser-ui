"""Test sharing backend API functions."""


from types import SimpleNamespace


import unittest.mock
import asynctest
import aiohttp.web


from swift_x_account_sharing.api import (
    has_access_handler,
    access_details_handler,
    gave_access_handler,
    shared_details_handler,
    share_container_handler,
    # unshare_container_handler
)


from swift_x_account_sharing.dict_db import InMemDB


class APITestClass(asynctest.TestCase):
    """Test the sharing backend public API."""

    def setUp(self):
        """Set up necessary mocks."""
        self.mock_request = SimpleNamespace(**{
            "app": {
                "db_conn":
                    unittest.mock.MagicMock(InMemDB)()
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
            print(resp)
            self.assertEqual(resp.status, 204)

    # async def test_endpoint_unshare_container_correct(self):
    #     """Test the unshare_container endpoint for conformmity."""
    #     with self.patch_json_dump:
    #         resp = await unshare_container_handler(self.mock_request)
    #         self.assertEqual(resp.status, 204)
