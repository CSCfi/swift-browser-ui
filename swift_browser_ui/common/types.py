"""Common types in swift_browser_ui project."""


import typing

import aiohttp.web

AiohttpHandler = typing.Callable[
    [aiohttp.web.Request],
    typing.Coroutine[typing.Awaitable, typing.Any, aiohttp.web.Response],
]
