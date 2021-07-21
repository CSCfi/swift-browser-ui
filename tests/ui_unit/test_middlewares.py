"""Module for testing ``swift_browser_ui.middlewares``."""


import unittest
import os

from aiohttp.web import HTTPUnauthorized, HTTPForbidden, HTTPNotFound
from aiohttp.web import Response, HTTPClientError, FileResponse
import asynctest

from swift_browser_ui.ui.middlewares import error_middleware
from swift_browser_ui.ui.front import index


async def return_401_handler(with_exception):
    """Return an HTTP401 error."""
    if with_exception:
        raise HTTPUnauthorized()
    return Response(status=401)


async def return_403_handler(with_exception):
    """Return an HTTP403 error."""
    if with_exception:
        raise HTTPForbidden()
    return Response(status=403)


async def return_404_handler(with_exception):
    """Return or raise an HTTP404 error."""
    if with_exception:
        raise HTTPNotFound()
    return Response(status=404)


async def return_400_handler(with_exception):
    """Return or raise an HTTP400 error."""
    if with_exception:
        raise HTTPClientError()
    return Response(status=400)


class MiddlewareTestClass(asynctest.TestCase):
    """Testing the error middleware."""

    async def test_401_return(self):
        """Test 401 middleware when the 401 status is returned."""
        patch_setd = unittest.mock.patch(
            "swift_browser_ui.ui.middlewares.setd",
            new={"static_directory": os.getcwd() + "/swift_browser_ui_frontend/dist"},
        )
        with patch_setd:
            resp = await error_middleware(None, return_401_handler)
            self.assertEqual(resp.status, 401)
            self.assertIsInstance(resp, Response)

    async def test_401_exception(self):
        """Test 401 middleware when the 401 status is risen."""
        patch_setd = unittest.mock.patch(
            "swift_browser_ui.ui.middlewares.setd",
            new={"static_directory": os.getcwd() + "/swift_browser_ui_frontend/dist"},
        )
        with patch_setd:
            resp = await error_middleware(True, return_401_handler)
            self.assertEqual(resp.status, 401)
            self.assertIsInstance(resp, Response)

    async def test_403_return(self):
        """Test 403 middleware when the 403 status is returned."""
        patch_setd = unittest.mock.patch(
            "swift_browser_ui.ui.middlewares.setd",
            new={"static_directory": os.getcwd() + "/swift_browser_ui_frontend/dist"},
        )
        with patch_setd:
            resp = await error_middleware(None, return_403_handler)
            self.assertEqual(resp.status, 403)
            self.assertIsInstance(resp, Response)

    async def test_403_exception(self):
        """Test 403 middleware when the 403 status is risen."""
        patch_setd = unittest.mock.patch(
            "swift_browser_ui.ui.middlewares.setd",
            new={"static_directory": os.getcwd() + "/swift_browser_ui_frontend/dist"},
        )
        with patch_setd:
            resp = await error_middleware(True, return_403_handler)
            self.assertEqual(resp.status, 403)
            self.assertIsInstance(resp, Response)

    async def test_404_return(self):
        """Test 404 middleware when the 404 status is returned."""
        patch_setd = unittest.mock.patch(
            "swift_browser_ui.ui.middlewares.setd",
            new={"static_directory": os.getcwd() + "/swift_browser_ui_frontend/dist"},
        )
        with patch_setd:
            resp = await error_middleware(None, return_404_handler)
            self.assertEqual(resp.status, 404)
            self.assertIsInstance(resp, Response)

    async def test_404_exception(self):
        """Test 404 middlewrae when the 404 status is risen."""
        patch_setd = unittest.mock.patch(
            "swift_browser_ui.ui.middlewares.setd",
            new={"static_directory": os.getcwd() + "/swift_browser_ui_frontend/dist"},
        )
        with patch_setd:
            resp = await error_middleware(True, return_404_handler)
            self.assertEqual(resp.status, 404)
            self.assertIsInstance(resp, Response)

    async def test_error_middleware_no_error(self):
        """Test the general error middleware with correct status."""
        patch_setd = unittest.mock.patch(
            "swift_browser_ui.ui.middlewares.setd",
            new={"static_directory": os.getcwd() + "/swift_browser_ui_frontend/dist"},
        )
        with patch_setd:
            resp = await error_middleware(None, index)
            self.assertEqual(resp.status, 200)
            self.assertIsInstance(resp, FileResponse)

    async def test_error_middleware_non_handled_raise(self):
        """Test the general error middleware with other status code."""
        patch_setd = unittest.mock.patch(
            "swift_browser_ui.ui.middlewares.setd",
            new={"static_directory": os.getcwd() + "/swift_browser_ui_frontend/dist"},
        )
        with self.assertRaises(HTTPClientError), patch_setd:
            await error_middleware(True, return_400_handler)
