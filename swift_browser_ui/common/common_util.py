"""Module for swift_browser_ui common utility functions."""


import asyncio
import os
import random

import aiohttp.web


async def read_in_keys(app: aiohttp.web.Application) -> None:
    """Read in keys to the application."""
    keys = os.environ.get("SWIFT_UI_API_AUTH_TOKENS", None)
    app["tokens"] = keys.split(",") if keys is not None else []
    if app["tokens"]:
        app["tokens"] = [token.encode("utf-8") for token in app["tokens"]]


async def sleep_random() -> None:
    """Sleep a random time."""
    return await asyncio.sleep(random.randint(2, 5))  # nosec  # noqa: S311
