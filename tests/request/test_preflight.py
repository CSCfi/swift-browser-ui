"""Module for preflight.py tests."""


import asynctest
import aiohttp


from swift_browser_ui.request.preflight import handle_delete_preflight


class HandleDeletePreflightTestCase(asynctest.TestCase):
    """Test case for testing preflight function."""

    async def test_handle_delete_preflight(self):
        """Test handle_delete_preflight handler."""
        resp = await handle_delete_preflight(None)
        self.assertIsInstance(resp, aiohttp.web.Response)
        self.assertEqual(
            resp.headers["Access-Control-Allow-Methods"],
            "POST, OPTIONS, DELETE"
        )
        self.assertEqual(
            resp.headers["Access-Control-Max-Age"],
            "84600"
        )
