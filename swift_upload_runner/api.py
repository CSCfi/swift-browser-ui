"""API handlers for swift-upload-runner."""


import aiohttp.web
# import asyncio

from .common import get_auth_instance
from .download import FileDownloadProxy


async def handle_get_object(
        request: aiohttp.web.Request
) -> aiohttp.web.StreamResponse:
    """Handle a request for getting object content."""
    auth = get_auth_instance(request)

    download = FileDownloadProxy(auth)

    await download.a_begin_download(
        request.match_info["project"],
        request.match_info["container"],
        request.match_info["object_name"]
    )

    resp = aiohttp.web.StreamResponse()
    await resp.prepare(request)

    # Create a task for writing the output into the StreamResponse
    await download.a_write_to_response(resp)

    return resp
