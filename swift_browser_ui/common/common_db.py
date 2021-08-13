"""Module for swift_browser_ui common database functions."""


import logging
import os
import asyncio

import aiohttp.web


LOGGER = logging.getLogger("swift_browser_ui.common.common_db")
LOGGER.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


def handle_dropped_connection(request: aiohttp.web.Request) -> None:
    """Handle dropped database connection."""
    LOGGER.log(logging.ERROR, "Lost database connection, reconnecting...")
    request.app["db_conn"].erase()
    asyncio.ensure_future(request.app["db_conn"].open())
    raise aiohttp.web.HTTPServiceUnavailable(reason="No database connection.")
