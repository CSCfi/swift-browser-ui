"""API handlers for swift-upload-runner."""


import aiohttp.web
# import asyncio

from .common import get_auth_instance
from .download import FileDownloadProxy, ContainerArchiveDownloadProxy


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

    # Create headers
    resp.headers["Content-Type"] = download.get_type()
    resp.headers["Content-Length"] = str(download.get_size())

    await resp.prepare(request)

    # Create a task for writing the output into the StreamResponse
    await download.a_write_to_response(resp)

    return resp


async def handle_get_container(
        request: aiohttp.web.Request
) -> aiohttp.web.StreamResponse:
    """Handle a request for getting container contents as an archive."""
    auth = get_auth_instance(request)

    resp = aiohttp.web.StreamResponse()

    project = request.match_info["project"]
    container = request.match_info["container"]

    # Create headers
    resp.headers["Content-Type"] = "binary/octet-stream"
    # Don't give content length, as the content length depends on
    # compressibility
    # Suggest {project_name}-{container}.tar as file name
    disp_header = f'attachment; filename="{project}-{container}.tar"'
    resp.headers["Content-Disposition"] = disp_header

    await resp.prepare(request)

    download = ContainerArchiveDownloadProxy(
        auth,
        project,
        container
    )

    await download.a_begin_container_download()

    # Create a task for writing the tarball into the StreamResponse
    await download.a_write_to_response(resp)

    return resp
