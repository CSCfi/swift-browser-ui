"""API handlers for swift-upload-runner."""


import asyncio
import logging
import os
import time
import typing

import aiohttp.web
import msgpack

import swift_browser_ui.upload.cryptupload as cryptupload
from swift_browser_ui.common.vault_client import VaultClient
from swift_browser_ui.upload.common import (
    VAULT_CLIENT,
    get_encrypted_upload_session,
    get_session_id,
    get_upload_instance,
    parse_multipart_in,
)
from swift_browser_ui.upload.download import (
    ContainerArchiveDownloadProxy,
    FileDownloadProxy,
)
from swift_browser_ui.upload.replicate import ObjectReplicationProxy

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

CRYPTUPLOAD_Q_DEPTH = int(os.environ.get("SWIFTUI_UPLOAD_RUNNER_Q_DEPTH", 96))


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

    # Ensure that both containers exist
    await replicator.a_ensure_container()
    await replicator.a_ensure_container(segmented=True)

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

    # Ensure that both containers exist
    await replicator.a_ensure_container()
    await replicator.a_ensure_container(segmented=True)

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
            "Access-Control-Allow-Headers": "Content-Type",
        }
    )
    return resp


async def handle_whitelist_options(
    _: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Handle options for editing project whitelist."""
    resp = aiohttp.web.Response(
        headers={
            "Access-Control-Allow-Methods": "GET, PUT, DELETE, OPTIONS",
            "Access-Control-Max-Age": "84600",
            "Access-Control-Allow-Headers": "Content-Type",
        }
    )
    return resp


async def handle_upload_ws(
    request: aiohttp.web.Request,
) -> aiohttp.web.WebSocketResponse:
    """Handle parallel file upload data via a websocket."""
    upload_session: cryptupload.UploadSession = get_encrypted_upload_session(request)

    ws = aiohttp.web.WebSocketResponse()
    await ws.prepare(request)

    LOGGER.info(f"Upload session websocket opened for {request.url.path}")

    async for msg in ws:
        if msg.type == "close":
            await upload_session.handle_close()
            LOGGER.info(f"Closing the websocket for {request.url.path}")
            await ws.close()

        # Open msgpack and handle message
        try:
            msg_unpacked: typing.Dict[str, typing.Any] = msgpack.loads(msg.data)

            if msg_unpacked["command"] == "add_header":
                await upload_session.handle_begin_upload(msg_unpacked)
            if msg_unpacked["command"] == "add_chunk":
                await upload_session.handle_upload_chunk(msg_unpacked)
            if msg_unpacked["command"] == "cancel":
                await upload_session.handle_close()
        except ValueError:
            LOGGER.error("Received an empty message.")
            LOGGER.debug(msg.data)
        except msgpack.exceptions.ExtraData:
            LOGGER.error("Extra data in message.")
            LOGGER.debug(msg.data)
        except msgpack.exceptions.FormatError:
            LOGGER.error("Incorrectly formatted message.")
            LOGGER.error(msg.data)

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


async def handle_health_check(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Answer a service health check for the upload runner and vault client."""
    start_time = time.time()
    vault_client: VaultClient = request.app[VAULT_CLIENT]
    try:
        vault_status = await vault_client.get_sys_health()
    except Exception:
        vault_status = "Error"
    end_time = time.time()

    return aiohttp.web.json_response(
        {
            "upload-runner": {"status": "Ok"},
            "vault-instance": {"status": vault_status},
            "start-time": start_time,
            "end-time": end_time,
        }
    )


async def handle_project_key(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Answer project specific encryption keys."""
    vault_client: VaultClient = request.app[VAULT_CLIENT]
    project = request.match_info["project"]
    public_key = await vault_client.get_public_key(project)

    return aiohttp.web.Response(
        text=public_key,
    )


async def handle_object_header(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """GET the header for an object."""
    vault_client: VaultClient = request.app[VAULT_CLIENT]
    project = request.match_info["project"]
    container = request.match_info["container"]
    obj = request.match_info["object_name"]
    if "owner" in request.query:
        owner = request.query["owner"]
        header = await vault_client.get_header(project, container, obj, owner)
    else:
        header = await vault_client.get_header(project, container, obj)

    return aiohttp.web.Response(
        text=header,
    )


async def handle_project_whitelist(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Whitelist a project's public key."""
    vault_client: VaultClient = request.app[VAULT_CLIENT]
    project = request.match_info["project"]
    flavor = request.query.get("flavor", "crypt4gh")
    public_key = await request.read()

    await vault_client.put_whitelist_key(project, flavor, public_key)

    return aiohttp.web.HTTPNoContent()


async def handle_delete_project_whitelist(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Delete the project's whitelisted key."""
    vault_client: VaultClient = request.app[VAULT_CLIENT]
    project = request.match_info["project"]
    await vault_client.remove_whitelist_key(project)

    return aiohttp.web.HTTPNoContent()


async def handle_batch_add_sharing_whitelist(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Add projects in sharing whitelist in batch."""
    vault_client: VaultClient = request.app[VAULT_CLIENT]
    project = request.match_info["project"]
    container = request.match_info["container"]

    receivers = await request.json()

    for receiver in receivers:
        await vault_client.put_project_whitelist(
            project,
            receiver["name"],
            container,
            receiver["id"],
        )

    return aiohttp.web.HTTPNoContent()


async def handle_batch_remove_sharing_whitelist(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Remove projects from sharing whitelist in batch."""
    vault_client: VaultClient = request.app[VAULT_CLIENT]
    project = request.match_info["project"]
    container = request.match_info["container"]

    receivers = await request.json()

    for receiver in receivers:
        await vault_client.remove_project_whitelist(
            project,
            receiver,
            container,
        )

    return aiohttp.web.HTTPNoContent()


async def handle_check_sharing_whitelist(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Check if a project is in the sharing whitelist."""
    vault_client: VaultClient = request.app[VAULT_CLIENT]
    project = request.match_info["project"]
    container = request.match_info["container"]
    receiver = request.match_info["receiver"]

    resp = await vault_client.get_project_whitelist(project, receiver, container)

    if resp is not None:
        return aiohttp.web.json_response(resp)
    return aiohttp.web.HTTPNoContent()
