"""Test swift_browser_ui.upload.server module."""


import aiohttp.web
import asynctest

import swift_browser_ui.upload.server


class ServerTestClass(asynctest.TestCase):
    """Test swift_browser_ui.upload.server module functions."""

    async def test_servinit(self):
        """Test servinit function."""
        app = await swift_browser_ui.upload.server.servinit()

        self.assertIsInstance(app, aiohttp.web.Application)
