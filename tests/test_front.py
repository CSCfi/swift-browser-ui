"""Module for testing ``swift_browser_ui.front``."""


import unittest
import os

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from swift_browser_ui.server import servinit


class FrontendTestCase(AioHTTPTestCase):
    """Test frontend."""

    async def get_application(self):
        """Retrieve web Application for test."""
        return await servinit()

    @staticmethod
    def return_true(_):
        """."""
        return True

    @unittest_run_loop
    async def test_browse(self):
        """Test /browse handler."""
        patch_setd = unittest.mock.patch("swift_browser_ui.front.setd", new={
            "static_directory": os.getcwd() + "/swift_browser_ui_frontend"
        })
        patch_check = unittest.mock.patch(
            "swift_browser_ui.front.session_check",
            new=self.return_true
        )
        with patch_setd, patch_check:
            response = await self.client.request("GET", "/browse")
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers["Content-type"],
                             "text/html")

    @unittest_run_loop
    async def test_index(self):
        """Test / handler."""
        patch_setd = unittest.mock.patch("swift_browser_ui.front.setd", new={
            "static_directory": os.getcwd() + "/swift_browser_ui_frontend"
        })
        patch_check = unittest.mock.patch(
            "swift_browser_ui.front.session_check",
            new=self.return_true
        )
        with patch_setd, patch_check:
            response = await self.client.request("GET", "/")
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers["Content-type"],
                             "text/html")
