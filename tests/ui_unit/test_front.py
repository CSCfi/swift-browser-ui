"""Module for testing ``swift_browser_ui.front``."""


import unittest
import os
import time
import aiohttp_session

from aiohttp.test_utils import AioHTTPTestCase

from swift_browser_ui.ui.server import servinit


class FrontendTestCase(
    AioHTTPTestCase,
):
    """Test frontend."""

    async def get_application(self):
        """Retrieve web Application for test."""
        return await servinit()

    @staticmethod
    def return_true(_):
        """."""
        return True

    async def test_browse(self):
        """Test /browse handler."""
        session_return = aiohttp_session.Session(
            "test-identity",
            new=True,
            data={},
        )
        session_return["at"] = time.time()
        session_return["token"] = "placeholder"
        session_return["uname"] = "placeholder"
        session_return["projects"] = "placeholder"
        aiohttp_session_get_session_mock = unittest.mock.AsyncMock()
        aiohttp_session_get_session_mock.return_value = session_return
        p_get_sess = unittest.mock.patch(
            "swift_browser_ui.ui.front.aiohttp_session.get_session",
            aiohttp_session_get_session_mock,
        )
        patch_setd = unittest.mock.patch(
            "swift_browser_ui.ui.front.setd",
            new={"static_directory": os.getcwd() + "/swift_browser_ui_frontend/dist"},
        )
        with patch_setd, p_get_sess:
            response = await self.client.request("GET", "/browse")
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers["Content-type"], "text/html")

    async def test_index(self):
        """Test / handler."""
        session_return = aiohttp_session.Session(
            "test-identity",
            new=True,
            data={},
        )
        session_return["at"] = time.time()
        session_return["token"] = "placeholder"
        session_return["projects"] = "placeholder"
        aiohttp_session_get_session_mock = unittest.mock.AsyncMock()
        aiohttp_session_get_session_mock.return_value = session_return
        p_get_sess = unittest.mock.patch(
            "swift_browser_ui.ui.front.aiohttp_session.get_session",
            aiohttp_session_get_session_mock,
        )
        patch_setd = unittest.mock.patch(
            "swift_browser_ui.ui.front.setd",
            new={
                "static_directory": os.getcwd() + "/swift_browser_ui_frontend/dist",
                "oidc_enabled": True,
                "sdconnect_enabled": False,
            },
        )
        with patch_setd, p_get_sess:
            response = await self.client.request("GET", "/")
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers["Content-type"], "text/html")

    async def test_loginpassword(self):
        """Test /loginpassword handler."""
        session_return = aiohttp_session.Session(
            "test-identity",
            new=True,
            data={},
        )
        session_return["at"] = time.time()
        session_return["token"] = "placeholder"
        session_return["projects"] = "placeholder"
        aiohttp_session_get_session_mock = unittest.mock.AsyncMock()
        aiohttp_session_get_session_mock.return_value = session_return
        p_get_sess = unittest.mock.patch(
            "swift_browser_ui.ui.front.aiohttp_session.get_session",
            aiohttp_session_get_session_mock,
        )
        patch_setd = unittest.mock.patch(
            "swift_browser_ui.ui.front.setd",
            new={
                "static_directory": os.getcwd() + "/swift_browser_ui_frontend/dist",
                "oidc_enabled": True,
                "sdconnect_enabled": False,
            },
        )
        with patch_setd, p_get_sess:
            response = await self.client.request("GET", "/loginpassword")
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers["Content-type"], "text/html")
