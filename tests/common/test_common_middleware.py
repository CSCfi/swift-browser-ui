"""Module for testing swift_browser_ui common middlewares."""


import types

import asynctest
import aiohttp.web

import asyncpg.exceptions

import swift_browser_ui.common.common_middleware


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
        self.mock_handler = asynctest.CoroutineMock(return_value=aiohttp.web.Response())
        super().setUp()

    async def test_add_cors(self):
        """Test CORS header addition middleware."""
        resp = await swift_browser_ui.common.common_middleware.add_cors(
            self.mock_request, self.mock_handler
        )
        self.assertEqual(
            resp.headers["Access-Control-Allow-Origin"],
            self.mock_request.headers["origin"],
        )

    async def test_check_db_conn_nonexistent(self):
        """Test database connection guard on failure."""
        self.mock_request.app["db_conn"].conn = None
        with self.assertRaises(aiohttp.web.HTTPServiceUnavailable):
            await swift_browser_ui.common.common_middleware.check_db_conn(
                self.mock_request, self.mock_handler
            )

    async def test_check_db_conn_existing(self):
        """Test database connection guard on success."""
        self.mock_request.app["db_conn"].conn = "placeholder"
        resp = await swift_browser_ui.common.common_middleware.check_db_conn(
            self.mock_request, self.mock_handler
        )
        self.assertIsInstance(resp, aiohttp.web.Response)

    async def test_check_db_conn_no_database(self):
        """Test database connection guard middleware without database."""
        self.mock_request.app["db_conn"] = None
        resp = await swift_browser_ui.common.common_middleware.check_db_conn(
            self.mock_request, self.mock_handler
        )
        self.assertIsInstance(resp, aiohttp.web.Response)

    async def test_catch_uniqueness_error(self):
        """Test uniqueness error catch middleware."""
        unique_violating_handler = asynctest.CoroutineMock(
            side_effect=asyncpg.exceptions.UniqueViolationError
        )
        with self.assertRaises(aiohttp.web.HTTPConflict):
            await swift_browser_ui.common.common_middleware.catch_uniqueness_error(
                self.mock_request, unique_violating_handler
            )
