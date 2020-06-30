"""Module for testing the service middleware."""


from types import SimpleNamespace


import asynctest
import aiohttp.web
from asyncpg import UniqueViolationError


from swift_x_account_sharing.db import DBConn
from swift_x_account_sharing.middleware import (
    add_cors,
    check_db_conn,
    catch_uniqueness_error
)


class MiddlewareTestCase(asynctest.TestCase):
    """Middleware test case class."""

    def setUp(self):
        """Set up necessary mocks."""
        self.mock_request = SimpleNamespace(**{
            "headers": {
                "origin": "http://localhost:8080"
            },
            "app": {
                "db_conn": DBConn()
            },
            "path": "/test"
        })
        self.mock_handler = asynctest.CoroutineMock(
            return_value=aiohttp.web.Response()
        )

    async def test_add_cors(self):
        """Test CORS header addition middleware."""
        resp = await add_cors(self.mock_request, self.mock_handler)
        self.assertEqual(
            resp.headers["Access-Control-Allow-Origin"],
            self.mock_request.headers["origin"]
        )

    async def test_check_db_conn_nonexistent(self):
        """Test database connection guard on failure."""
        with self.assertRaises(aiohttp.web.HTTPServiceUnavailable):
            await check_db_conn(self.mock_request, self.mock_handler)

    async def test_check_db_conn_existing(self):
        """Test database connection guard on success."""
        self.mock_request.app["db_conn"].conn = "placeholder"
        resp = await check_db_conn(self.mock_request, self.mock_handler)
        self.assertIsInstance(resp, aiohttp.web.Response)

    async def test_catch_uniqueness_error(self):
        """Test uniqueness error catch middleware."""
        unique_violating_handler = asynctest.CoroutineMock(
            side_effect=UniqueViolationError
        )
        with self.assertRaises(aiohttp.web.HTTPConflict):
            await catch_uniqueness_error(
                self.mock_request,
                unique_violating_handler
            )
