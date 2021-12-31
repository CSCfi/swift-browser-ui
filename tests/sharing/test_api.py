"""Test sharing backend API functions."""


from types import SimpleNamespace


import unittest
import aiohttp.web


from swift_browser_ui.sharing.api import (
    has_access_handler,
    access_details_handler,
    gave_access_handler,
    shared_details_handler,
    share_container_handler,
    edit_share_handler,
    delete_share_handler,
    delete_container_shares_handler,
)


class APITestClass(unittest.IsolatedAsyncioTestCase):
    """Test the sharing backend public API."""

    def setUp(self):
        """Set up necessary mocks."""
        self.mock_request = SimpleNamespace(
            **{
                "app": {
                    "db_conn": SimpleNamespace(
                        **{
                            "add_share": unittest.mock.AsyncMock(),
                            "edit_share": unittest.mock.AsyncMock(),
                            "delete_share": unittest.mock.AsyncMock(),
                            "delete_container_shares": unittest.mock.AsyncMock(),
                            "get_access_list": unittest.mock.AsyncMock(),
                            "get_shared_list": unittest.mock.AsyncMock(),
                            "get_access_container_details": unittest.mock.AsyncMock(),
                            "get_shared_container_details": unittest.mock.AsyncMock(),
                        }
                    ),
                },
                "query": {
                    "user": "AUTH_example",
                    "owner": "AUTH_otherexample",
                    "container": "test-container-1",
                    "access": "r,w,l",
                    "address": "https://placeholder.os:443",
                },
                "match_info": {"container": "test", "user": "test", "owner": "test"},
            }
        )

        self.json_mock = unittest.mock.MagicMock(aiohttp.web.json_response)
        self.patch_json_dump = unittest.mock.patch(
            "swift_browser_ui.sharing.api.aiohttp.web.json_response", new=self.json_mock
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

    async def test_endpoint_delete_container_shares_correct(self):
        """Test the delete_container_shares endpoint for conformity."""
        with self.patch_json_dump:
            resp = await delete_container_shares_handler(self.mock_request)
            self.assertEqual(resp.status, 204)
