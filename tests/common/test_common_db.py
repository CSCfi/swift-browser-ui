"""Module for testing common database functions."""


import unittest.mock
import asyncio
import types

import aiohttp.web
import asynctest

import swift_browser_ui.common.common_db as db


class HandleDroppedTestClass(asynctest.TestCase):
    """Test class for dropped connection handling."""

    def setUp(self):
        """Set up necessary mocks."""
        self.mock_request = types.SimpleNamespace(
            **{
                "app": {
                    "db_conn": types.SimpleNamespace(
                        **{
                            "erase": unittest.mock.Mock(),
                            "open": asynctest.mock.Mock(),
                        }
                    ),
                },
            }
        )

        self.ensure_future_mock = unittest.mock.MagicMock(asyncio.ensure_future)
        self.patch_asyncio_ensure_future = unittest.mock.patch(
            "swift_browser_ui.sharing.db.asyncio.ensure_future",
            new=self.ensure_future_mock,
        )

    async def test_handle_dropped_connection(self):
        """Test handling dropped connection."""
        with self.patch_asyncio_ensure_future:
            with self.assertRaises(aiohttp.web.HTTPServiceUnavailable):
                await db.handle_dropped_connection(self.mock_request)
            self.mock_request.app["db_conn"].erase.assert_called_once()
            self.mock_request.app["db_conn"].open.assert_called_once()
