"""Test sharing backend API functions."""


from types import SimpleNamespace

import unittest
import unittest.mock
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
    handle_user_add_token,
    handle_user_delete_token,
    handle_user_list_tokens,
    handle_health_check,
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
                            "add_token": unittest.mock.AsyncMock(),
                            "edit_share": unittest.mock.AsyncMock(),
                            "delete_share": unittest.mock.AsyncMock(),
                            "delete_container_shares": unittest.mock.AsyncMock(),
                            "get_access_list": unittest.mock.AsyncMock(),
                            "get_shared_list": unittest.mock.AsyncMock(),
                            "get_access_container_details": unittest.mock.AsyncMock(),
                            "get_shared_container_details": unittest.mock.AsyncMock(),
                            "get_tokens": unittest.mock.AsyncMock([]),
                            "revoke_token": unittest.mock.AsyncMock(),
                            "prune_tokens": unittest.mock.AsyncMock(),
                            "pool": None,
                        }
                    ),
                },
                "query": {
                    "user": "AUTH_example",
                    "owner": "AUTH_otherexample",
                    "container": "test-container-1",
                    "access": "r,w,l",
                    "address": "https://placeholder.os:443",
                    "token": "user_token",
                },
                "match_info": {
                    "container": "test",
                    "user": "test",
                    "owner": "test",
                    "project": "test",
                    "id": "test",
                },
                "post": unittest.mock.AsyncMock(return_value={}),
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

        # Also test delete_share endpoint leads to bulk unshare without user key
        with self.patch_json_dump:
            alt_mock_request = self.mock_request
            del alt_mock_request.query["user"]
            resp = await delete_share_handler(alt_mock_request)
            self.assertEqual(resp.status, 204)

    async def test_endpoint_delete_container_shares_correct(self):
        """Test the delete_container_shares endpoint for conformity."""
        with self.patch_json_dump:
            resp = await delete_container_shares_handler(self.mock_request)
            self.assertEqual(resp.status, 204)

    async def test_endpoint_handle_user_add_token(self):
        """Test the handle_user_add_token endpoint for conformity."""
        with self.patch_json_dump:
            resp = await handle_user_add_token(self.mock_request)
            self.assertEqual(resp.status, 200)

        # Also test when no token is present in query
        del self.mock_request.query["token"]
        with self.patch_json_dump:
            with self.assertRaises(aiohttp.web.HTTPBadRequest):
                await handle_user_add_token(self.mock_request)

    async def test_endpoint_handle_user_delete_token(self):
        """Test the handle_user_delete_token endpoint for conformity."""
        with self.patch_json_dump:
            resp = await handle_user_delete_token(self.mock_request)
            self.assertEqual(resp.status, 200)

    async def test_endpoint_handle_user_list_tokens(self):
        """Test the handle_user_list_tokens endpoint for conformity."""
        with self.patch_json_dump:
            await handle_user_list_tokens(self.mock_request)
            self.json_mock.assert_called_once()

    async def test_endpoint_handle_health_check(self):
        """Test the handle_health_check endpoint for conformity."""
        with self.patch_json_dump:
            await handle_health_check(self.mock_request)

        self.mock_request.app["db_conn"].pool = {}
        with self.patch_json_dump:
            await handle_health_check(self.mock_request)

        del self.mock_request.app["db_conn"].pool
        with self.patch_json_dump:
            await handle_health_check(self.mock_request)

        calls = [
            unittest.mock.call({"status": "Ok"}),
            unittest.mock.call({"status": "Degraded", "degraded": ["database"]}),
        ]
        self.json_mock.assert_has_calls(calls)
