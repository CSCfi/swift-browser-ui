"""API handlers for swift-upload-runner."""


import logging
import typing
import aiohttp.web
import asyncio
import base64
import json
import os


from swift_browser_ui.upload.common import (
    get_encrypted_upload_instance,
    get_session_id,
    get_upload_instance,
    parse_multipart_in,
)
from swift_browser_ui.upload.download import (
    FileDownloadProxy,
    ContainerArchiveDownloadProxy,
)
from swift_browser_ui.upload.replicate import ObjectReplicationProxy


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


async def handle_get_object(request: aiohttp.web.Request) -> aiohttp.web.StreamResponse:
    """Handle a request for getting object content."""
    session = get_session_id(request)

    download = FileDownloadProxy(request.app[session])

    await download.a_begin_download(
        request.match_info["project"],
        request.match_info["container"],
        request.match_info["object_name"],
    )

    resp = aiohttp.web.StreamResponse()

    # Create headers
    resp.headers["Content-Type"] = await download.a_get_type()
    resp.headers["Content-Length"] = str(await download.a_get_size())

    if "origin" in request.headers:
        resp.headers["Access-Control-Allow-Origin"] = request.headers["origin"]

    await resp.prepare(request)

    # Create a task for writing the output into the StreamResponse
    await download.a_write_to_response(resp)

    return resp


async def handle_replicate_container(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Handle request to replicating a container from a source."""
    session = get_session_id(request)

    project = request.match_info["project"]
    container = request.match_info["container"]

    source_project = request.query["from_project"]
    source_container = request.query["from_container"]

    replicator = ObjectReplicationProxy(
        request.app[session],
        request.app["client"],
        project,
        container,
        source_project,
        source_container,
    )

    asyncio.ensure_future(replicator.a_copy_from_container())

    return aiohttp.web.Response(status=202)


async def handle_replicate_object(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Handle a request to replicating an object from a source."""
    session = get_session_id(request)

    project = request.match_info["project"]
    container = request.match_info["container"]

    source_project = request.query["from_project"]
    source_container = request.query["from_container"]
    source_object = request.query["from_object"]

    replicator = ObjectReplicationProxy(
        request.app[session],
        request.app["client"],
        project,
        container,
        source_project,
        source_container,
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
    _: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Handle options request for posting the object chunk."""
    resp = aiohttp.web.Response(
        headers={
            "Access-Control-Allow-Methods": "POST, OPTIONS, GET",
            "Access-Control-Max-Age": "84600",
        }
    )

    return resp


async def handle_upload_encrypted_object_options(
    _: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Handle options for uploading an encrypted object."""
    resp = aiohttp.web.Response(
        headers={
            "Access-Control-Allow-Methods": "GET, PUT, OPTIONS",
            "Access-Control-Max-Age": "84600",
        }
    )
    return resp


async def handle_upload_encrypted_object(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Handle uploading an object spliced into segments."""
    upload_session = await get_encrypted_upload_instance(request)
    return await upload_session.add_header(request)


async def handle_upload_encrypted_object_ws(
    request: aiohttp.web.Request,
) -> aiohttp.web.WebSocketResponse:
    """Handle uploading object data as a websocket."""
    upload_session = await get_encrypted_upload_instance(request)

    getter_tasks: typing.List[asyncio.Task] = []
    slicer_tasks: typing.List[asyncio.Task] = []
    upload_tasks: typing.List[asyncio.Task] = []

    ws = aiohttp.web.WebSocketResponse()
    await ws.prepare(request)

    LOGGER.info(f"Upload websocket opened for {request.url.path}")

    await upload_session.set_ws(ws)

    async for msg in ws:
        if msg.type == "close":
            await asyncio.gather(*(getter_tasks + slicer_tasks + upload_tasks))
            LOGGER.info(f"Closing the websocket for {request.url.path}")
            await ws.close()
        if msg.data == "startPull":
            # Pull 256 chunks initially
            LOGGER.debug("Starting upload content pull through websocket.")
            getter_tasks = [
                asyncio.create_task(upload_session.get_next_chunk(ws))
                for _ in range(0, 96)
            ]
            slicer_tasks = [
                asyncio.create_task(
                    upload_session.slice_into_queue(
                        i, upload_session.get_segment_queue(i)
                    )
                )
                for i in range(0, upload_session.return_total_segments())
            ]
            upload_tasks = [
                asyncio.create_task(upload_session.upload_segment(i))
                for i in range(0, upload_session.return_total_segments())
            ]
        else:
            m = json.loads(msg.data)
            i = m["iter"]
            # LOGGER.info(f"Adding chunk number {i}")
            c = base64.b64decode(m["chunk"])
            # upload_session.add_to_chunks((i, c))
            await upload_session.add_to_chunks(
                i,
                c,
                ws,
            )

    LOGGER.info(f"Upload finished for {request.url.path} – pushing manifest.")
    await upload_session.add_manifest()
    return ws


async def handle_get_container(
    request: aiohttp.web.Request,
) -> aiohttp.web.StreamResponse:
    """Handle a request for getting container contents as an archive."""
    if "resumableChunkNumber" in request.query.keys():
        return await handle_get_object_chunk(request)

    session = get_session_id(request)

    resp = aiohttp.web.StreamResponse()

    project = request.match_info["project"]
    container = request.match_info["container"]

    # Create headers
    resp.headers["Content-Type"] = "application/x-tar"
    # Don't give content length, as the content length depends on
    # compressibility
    # Suggest {project_name}-{container}.tar as file name
    disp_header = f'attachment; filename="{project}-{container}.tar"'
    resp.headers["Content-Disposition"] = disp_header

    await resp.prepare(request)

    download = ContainerArchiveDownloadProxy(request.app[session], project, container)

    await download.a_begin_container_download()

    # Create a task for writing the tarball into the StreamResponse
    await download.a_write_to_response(resp)

    return resp


async def handle_health_check(_: aiohttp.web.Request) -> aiohttp.web.Response:
    """Answer a service health check."""
    # Case degraded

    # Case nominal
    return aiohttp.web.json_response(
        {
            "status": "Ok",
        }
    )
