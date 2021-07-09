"""API handlers for swift-upload-runner."""


import aiohttp.web
import asyncio

from .common import get_auth_instance, get_upload_instance
from .common import parse_multipart_in
from .download import FileDownloadProxy, ContainerArchiveDownloadProxy
from .replicate import ObjectReplicationProxy


async def handle_get_object(request: aiohttp.web.Request) -> aiohttp.web.StreamResponse:
    """Handle a request for getting object content."""
    auth = get_auth_instance(request)

    download = FileDownloadProxy(auth)

    await download.a_begin_download(
        request.match_info["project"],
        request.match_info["container"],
        request.match_info["object_name"],
    )

    resp = aiohttp.web.StreamResponse()

    # Create headers
    resp.headers["Content-Type"] = await download.a_get_type()
    resp.headers["Content-Length"] = str(await download.a_get_size())

    await resp.prepare(request)

    # Create a task for writing the output into the StreamResponse
    await download.a_write_to_response(resp)

    return resp


async def handle_replicate_container(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Handle request to replicating a container from a source."""
    auth = get_auth_instance(request)

    project = request.match_info["project"]
    container = request.match_info["container"]

    source_project = request.query["from_project"]
    source_container = request.query["from_container"]

    replicator = ObjectReplicationProxy(
        auth, request.app["client"], project, container, source_project, source_container
    )

    asyncio.ensure_future(replicator.a_copy_from_container())

    return aiohttp.web.Response(status=202)


async def handle_replicate_object(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Handle a request to replicating an object from a source."""
    auth = get_auth_instance(request)

    project = request.match_info["project"]
    container = request.match_info["container"]

    source_project = request.query["from_project"]
    source_container = request.query["from_container"]
    source_object = request.query["from_object"]

    replicator = ObjectReplicationProxy(
        auth, request.app["client"], project, container, source_project, source_container
    )

    asyncio.ensure_future(replicator.a_copy_object(source_object))

    return aiohttp.web.Response(status=202)


async def handle_post_object_chunk(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Handle a request for posting an object chunk."""
    if "from_object" in request.query.keys():
        return await handle_replicate_object(request)
    if "from_container" in request.query.keys():
        return await handle_replicate_container(request)

    project = request.match_info["project"]
    container = request.match_info["container"]

    query, data = await parse_multipart_in(request)

    upload_session = await get_upload_instance(request, project, container, p_query=query)

    return await upload_session.a_add_chunk(query, data)


async def handle_get_object_chunk(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Handle a request for checking if a chunk exists."""
    get_auth_instance(request)

    project = request.match_info["project"]
    container = request.match_info["container"]

    try:
        # Infuriatingly resumable.js starts counting chunks from 1
        # thus, reducing said 1 from the resulting chunk number
        chunk_number = int(request.query["resumableChunkNumber"]) - 1
    except KeyError:
        raise aiohttp.web.HTTPBadRequest(reason="Malformed query string")

    upload_session = await get_upload_instance(request, project, container)

    return await upload_session.a_check_segment(chunk_number)


async def handle_post_object_options(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Handle options request for posting the object chunk."""
    resp = aiohttp.web.Response(
        headers={
            "Access-Control-Allow-Methods": "POST, OPTIONS, GET",
            "Access-Control-Max-Age": "84600",
        }
    )

    return resp


async def handle_get_container(
    request: aiohttp.web.Request,
) -> aiohttp.web.StreamResponse:
    """Handle a request for getting container contents as an archive."""
    if "resumableChunkNumber" in request.query.keys():
        return await handle_get_object_chunk(request)

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

    download = ContainerArchiveDownloadProxy(auth, project, container)

    await download.a_begin_container_download()

    # Create a task for writing the tarball into the StreamResponse
    await download.a_write_to_response(resp)

    return resp


async def handle_health_check(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Answer a service health check."""
    # Case degraded

    # Case nominal
    return aiohttp.web.json_response(
        {
            "status": "Ok",
        }
    )
