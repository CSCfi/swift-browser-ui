"""Module for testing ``swift_browser_ui.middlewares``."""


import unittest
import os

from aiohttp.web import HTTPUnauthorized, HTTPForbidden, HTTPNotFound
from aiohttp.web import Response, HTTPClientError, FileResponse

import swift_browser_ui.ui.middlewares
from swift_browser_ui.ui.front import index

import tests.common.mockups


async def return_401_handler(with_exception):
    """Return an HTTP401 error."""
    if with_exception:
        raise HTTPUnauthorized()
    return FileResponse(
        status=401, path=f"{os.getcwd()}/swift_browser_ui_frontend/dist/401.html"
    )


async def return_403_handler(with_exception):
    """Return an HTTP403 error."""
    if with_exception:
        raise HTTPForbidden()
    return FileResponse(
        status=403, path=f"{os.getcwd()}/swift_browser_ui_frontend/dist/403.html"
    )


async def return_404_handler(with_exception):
    """Return or raise an HTTP404 error."""
    if with_exception:
        raise HTTPNotFound()
    return FileResponse(
        status=404, path=f"{os.getcwd()}/swift_browser_ui_frontend/dist/404.html"
    )


async def return_400_handler(with_exception):
    """Return or raise an HTTP400 error."""
    if with_exception:
        raise HTTPClientError()
    return FileResponse(
        status=400, path=f"{os.getcwd()}/swift_browser_ui_frontend/dist/400.html"
    )


async def return_200_handler(_):
    """Return a successful response."""
    return Response(status=200, body=b"OK")


class MiddlewareTestClass(tests.common.mockups.APITestBase):
    """Testing the error middleware."""

    def setUp(self):
        """."""
        super().setUp()
        self.p_get_sess = unittest.mock.patch(
            "swift_browser_ui.ui.middlewares.aiohttp_session.get_session",
            self.aiohttp_session_get_session_mock,
        )

    async def test_check_session(self):
        """Test session expiration middleware."""
        with self.p_get_sess:
            ret = await swift_browser_ui.ui.middlewares.check_session(
                self.mock_request,
                return_200_handler,
            )
        self.assertEqual(ret.status, 200)

    async def test_check_session_fail_expired(self):
        """Test session expiration middleware with expired session."""
        self.mock_request.path = "/api/test-projct/test-container"
        self.session_return["at"] = 0

        with self.p_get_sess, self.assertRaises(HTTPUnauthorized):
            await swift_browser_ui.ui.middlewares.check_session(
                self.mock_request,
                return_200_handler,
            )

    async def test_check_session_fail_no_raise(self):
        """Test session expiration middleware with route that shouldn't fail."""
        self.mock_request.path = "/login"
        with self.p_get_sess:
            ret = await swift_browser_ui.ui.middlewares.check_session(
                self.mock_request,
                return_200_handler,
            )
        self.assertEqual(ret.status, 200)

    async def test_401_return(self):
        """Test 401 middleware when the 401 status is returned."""
        resp = await swift_browser_ui.ui.middlewares.error_middleware(
            None, return_401_handler
        )
        self.assertEqual(resp.status, 401)
        self.assertIsInstance(resp, FileResponse)

    async def test_401_exception(self):
        """Test 401 middleware when the 401 status is risen."""
        resp = await swift_browser_ui.ui.middlewares.error_middleware(
            True, return_401_handler
        )
        self.assertEqual(resp.status, 401)
        self.assertIsInstance(resp, FileResponse)

    async def test_403_return(self):
        """Test 403 middleware when the 403 status is returned."""
        resp = await swift_browser_ui.ui.middlewares.error_middleware(
            None, return_403_handler
        )
        self.assertEqual(resp.status, 403)
        self.assertIsInstance(resp, FileResponse)

    async def test_403_exception(self):
        """Test 403 middleware when the 403 status is risen."""
        resp = await swift_browser_ui.ui.middlewares.error_middleware(
            True, return_403_handler
        )
        self.assertEqual(resp.status, 403)
        self.assertIsInstance(resp, FileResponse)

    async def test_404_return(self):
        """Test 404 middleware when the 404 status is returned."""
        resp = await swift_browser_ui.ui.middlewares.error_middleware(
            None, return_404_handler
        )
        self.assertEqual(resp.status, 404)
        self.assertIsInstance(resp, FileResponse)

    async def test_404_exception(self):
        """Test 404 middlewrae when the 404 status is risen."""
        resp = await swift_browser_ui.ui.middlewares.error_middleware(
            True, return_404_handler
        )
        self.assertEqual(resp.status, 404)
        self.assertIsInstance(resp, FileResponse)

    async def test_error_middleware_no_error(self):
        """Test the general error middleware with correct status."""
        patch_setd = unittest.mock.patch(
            "swift_browser_ui.ui.middlewares.setd",
            new={"static_directory": os.getcwd() + "/swift_browser_ui_frontend/dist"},
        )
        with patch_setd:
            resp = await swift_browser_ui.ui.middlewares.error_middleware(None, index)
            self.assertEqual(resp.status, 200)
            self.assertIsInstance(resp, FileResponse)

    async def test_error_middleware_non_handled_raise(self):
        """Test the general error middleware with other status code."""
        with self.assertRaises(HTTPClientError):
            await swift_browser_ui.ui.middlewares.error_middleware(
                True, return_400_handler
            )
