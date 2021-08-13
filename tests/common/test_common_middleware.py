"""Module for testing swift_browser_ui common middlewares."""


import types
import unittest.mock

import asynctest
import aiohttp.web

import asyncpg.exceptions

import swift_browser_ui.common.common_middleware as middle


class CommonMiddlewareTestCase(asynctest.TestCase):
    """Common midleware unit test class"""

    def setUp(self):
        self.mock_request = types.SimpleNamespace(
            **{
                "headers": {"origin": "http://localhost:8080"},
                "app": {"db_conn": types.SimpleNamespace(**{"conn": None})},
                "path": "/test",
            }
        )
        self.app_mock = {}
        self.mock_handler = asynctest.CoroutineMock(return_value=aiohttp.web.Response())
        super().setUp()

    async def test_add_cors(self):
        """Test CORS header addition middleware."""
        resp = await middle.add_cors(self.mock_request, self.mock_handler)
        self.assertEqual(
            resp.headers["Access-Control-Allow-Origin"],
            self.mock_request.headers["origin"],
        )

    async def test_check_db_conn_nonexistent(self):
        """Test database connection guard on failure."""
        self.mock_request.app["db_conn"].conn = None
        with self.assertRaises(aiohttp.web.HTTPServiceUnavailable):
            await middle.check_db_conn(self.mock_request, self.mock_handler)

    async def test_check_db_conn_existing(self):
        """Test database connection guard on success."""
        self.mock_request.app["db_conn"].conn = "placeholder"
        resp = await middle.check_db_conn(self.mock_request, self.mock_handler)
        self.assertIsInstance(resp, aiohttp.web.Response)

    async def test_check_db_conn_no_database(self):
        """Test database connection guard middleware without database."""
        self.mock_request.app["db_conn"] = None
        resp = await middle.check_db_conn(self.mock_request, self.mock_handler)
        self.assertIsInstance(resp, aiohttp.web.Response)

    async def test_catch_uniqueness_error(self):
        """Test uniqueness error catch middleware."""
        unique_violating_handler = asynctest.CoroutineMock(
            side_effect=asyncpg.exceptions.UniqueViolationError
        )
        with self.assertRaises(aiohttp.web.HTTPConflict):
            await middle.catch_uniqueness_error(
                self.mock_request, unique_violating_handler
            )


class HandleValidateAuthTest(asynctest.TestCase):
    """Auth middleware tests."""

    async def test_handle_validate_authentication_success(self):
        """Test authentication validation handler success."""
        t_singature_mock = asynctest.CoroutineMock()
        t_signature_patch = unittest.mock.patch(
            "swift_browser_ui.common.signature.test_signature", t_singature_mock
        )

        handler_mock = asynctest.CoroutineMock()
        request_mock = types.SimpleNamespace(
            **{
                "app": {
                    "tokens": ["awefi"],
                },
                "query": {"signature": "a", "valid": "b"},
                "match_info": {},
                "url": types.SimpleNamespace(**{"path": "c"}),
                "path": "/health",
            }
        )

        with t_signature_patch:
            await middle.handle_validate_authentication(request_mock, handler_mock)

    async def test_handle_validate_authentication_failure(self):
        """Test authentication validation handler failure."""
        handler_mock = asynctest.CoroutineMock()
        request_mock = types.SimpleNamespace(
            **{
                "query": {"signature": "a", "vali": "b"},
                "match_info": {},
                "url": types.SimpleNamespace(**{"path": "c"}),
                "path": "/health",
            }
        )
        with self.assertRaises(aiohttp.web.HTTPClientError):
            await middle.handle_validate_authentication(request_mock, handler_mock)
