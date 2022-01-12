"""Test swift_browser_ui.upload.server module."""


import unittest
import aiohttp.web

import swift_browser_ui.upload.server


class ServerTestClass(unittest.IsolatedAsyncioTestCase):
    """Test swift_browser_ui.upload.server module functions."""

    async def test_servinit(self):
        """Test servinit function."""
        app = await swift_browser_ui.upload.server.servinit()

        self.assertIsInstance(app, aiohttp.web.Application)
