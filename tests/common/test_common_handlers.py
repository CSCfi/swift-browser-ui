"""Module for testing common handlers."""


import unittest
import aiohttp

import swift_browser_ui.common.common_handlers


class PreflightHandlerTestCase(unittest.IsolatedAsyncioTestCase):
    """Preflight handler test case."""

    async def test_handle_delete_preflight(self):
        """Test handle_delete_preflight handler function."""
        resp = await swift_browser_ui.common.common_handlers.handle_delete_preflight(None)
        self.assertEqual(
            resp.headers["Access-Control-Allow-Methods"], "POST, OPTIONS, DELETE"
        )
        self.assertEqual(resp.headers["Access-Control-Max-age"], "84600")
        self.assertIsInstance(resp, aiohttp.web.Response)
