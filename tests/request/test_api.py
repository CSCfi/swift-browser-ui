"""Module for testing sharing request API functions."""


import unittest
import unittest.mock
from types import SimpleNamespace

import aiohttp


from swift_browser_ui.request.api import (
    handle_share_request_post,
    handle_user_owned_request_listing,
    handle_user_made_request_listing,
    handle_container_request_listing,
    handle_user_share_request_delete,
    handle_user_add_token,
    handle_user_delete_token,
    handle_user_list_tokens,
    handle_health_check,
)


class APITestClass(unittest.IsolatedAsyncioTestCase):
    """Test class for testing API functions."""

    def setUp(self):
        """Set up necessary mocks."""
        self.mock_request = SimpleNamespace(
            **{
                "app": {
                    "db_conn": SimpleNamespace(
                        **{
                            "add_request": unittest.mock.AsyncMock(),
                            "add_token": unittest.mock.AsyncMock(),
                            "get_request_owned": unittest.mock.AsyncMock(),
                            "get_request_made": unittest.mock.AsyncMock(),
                            "get_request_container": unittest.mock.AsyncMock(),
                            "delete_request": unittest.mock.AsyncMock(),
                            "get_tokens": unittest.mock.AsyncMock([]),
                            "revoke_token": unittest.mock.AsyncMock(),
                            "pool": None,
                        }
                    )
                },
                "query": {"owner": "AUTH_otherexample", "token": "user_token"},
                "match_info": {
                    "container": "test",
                    "user": "test",
                    "project": "test",
                    "id": "test",
                },
                "post": unittest.mock.AsyncMock(return_value={}),
            }
        )

        self.json_mock = unittest.mock.MagicMock(aiohttp.web.json_response)
        self.patch_json_dump = unittest.mock.patch(
            "swift_browser_ui.request.api.aiohttp.web.json_response", new=self.json_mock
        )

    async def test_endpoint_share_request_post_correct(self):
        """Test the share_request_post endpoint for conformity."""
        with self.patch_json_dump:
            await handle_share_request_post(self.mock_request)
            self.json_mock.assert_called_once()

    async def test_endpoint_user_owned_request_listing_correct(self):
        """Test the user_owned_request_listing endpoint for conformity."""
        with self.patch_json_dump:
            await handle_user_owned_request_listing(self.mock_request)
            self.json_mock.assert_called_once()

    async def test_endpoint_user_made_request_listing(self):
        """Test the user_made_request_listing endpoint for conformity."""
        with self.patch_json_dump:
            await handle_user_made_request_listing(self.mock_request)
            self.json_mock.assert_called_once()

    async def test_endpoint_container_request_listing(self):
        """Test the container_request_listing endpoint for conformity."""
        with self.patch_json_dump:
            await handle_container_request_listing(self.mock_request)
            self.json_mock.assert_called_once()

    async def test_endpoint_user_share_request_delete(self):
        """Test the user_share_request_delete endpoint for conformity."""
        with self.patch_json_dump:
            resp = await handle_user_share_request_delete(self.mock_request)
            self.assertEqual(resp.status, 200)

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
