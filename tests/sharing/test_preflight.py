"""Module for testing preflight handling middleware."""


import asynctest
import aiohttp


from swift_browser_ui.sharing.preflight import handle_delete_preflight


class PreflightHandlerTestCase(asynctest.TestCase):
    """Preflight handler test case."""

    async def test_handle_delete_preflight(self):
        """Test handle_delete_preflight handler function."""
        resp = await handle_delete_preflight(None)
        self.assertEqual(
            resp.headers["Access-Control-Allow-Methods"],
            "POST, OPTIONS, DELETE"
        )
        self.assertEqual(
            resp.headers["Access-Control-Max-age"],
            "84600"
        )
        self.assertIsInstance(resp, aiohttp.web.Response)
