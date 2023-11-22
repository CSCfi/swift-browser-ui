"""Class for session crypt upload/download websocket."""


import asyncio
import base64
import logging
import os
import secrets
import ssl
import typing

import aiohttp.client
import aiohttp.web
import certifi
import msgpack

import swift_browser_ui.common.vault_client as vault_client
import swift_browser_ui.upload.common as common

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

UPL_TIMEOUT = 32768

# Size constants for upload data are derived from encryption schema, crypt4gh
SEGMENT_SIZE = 5368708140
SEGMENT_CHUNKS = 81885
CHUNK_SIZE = 65564

# Use an approx 10 MiB queue for each upload by default
CRYPTUPLOAD_Q_DEPTH = int(os.environ.get("SWIFTUI_UPLOAD_RUNNER_Q_DEPTH", 160))


class FileUpload:
    """Class for handling the upload of a single file."""

    def __init__(
        self,
        client: aiohttp.client.ClientSession,
        vault: vault_client.VaultClient,
        session: typing.Dict[str, typing.Any],
        socket: aiohttp.web.WebSocketResponse,
        project: str,
        container: str,
        name: str,
        path: str,
        total: int,
        owner: str = "",
        owner_name: str = "",
    ):
        """."""
        self.session = session
        self.client = client
        self.vault = vault
        self.socket = socket

        self.project = project
        self.container = container
        self.path = path
        self.name = name
        self.total = total

        self.owner = owner
        self.owner_name = owner_name

        # Initialize backend generated values
        self.segment_id = secrets.token_urlsafe(32)
        self.done_chunks: typing.Set = set({})
        self.endpoint = self.session["endpoint"]
        self.token = self.session["token"]
        self.host = common.get_download_host(
            self.endpoint,
            self.owner if self.owner else self.project,
        )
        self.chunk_cache: typing.Dict[int, bytes] = {}
        self.failed: bool = False
        self.finished: bool = False

        # Calculate upload parameters
        self.total_segments: int = -(self.total // -SEGMENT_SIZE)
        self.remainder_segment: int = self.total % SEGMENT_SIZE
        self.total_chunks: int = -(self.total // -CHUNK_SIZE)
        self.remainder_chunks: int = -(self.remainder_segment // -CHUNK_SIZE)

        self.tasks: typing.List[asyncio.Task] = []

        LOGGER.debug(f"total: {self.total}")
        LOGGER.debug(f"segments: {self.total_segments}")
        LOGGER.debug(f"chunks: {self.total_chunks}")

    async def wait_for_cache(self) -> bool:
        """Block until the cache has enough space available."""
        while len(self.chunk_cache) > CRYPTUPLOAD_Q_DEPTH:
            if self.finished:
                return False
            await asyncio.sleep(0.1)
        return True

    async def add_header(self, header: bytes) -> None:
        """Add header for the file."""
        if not await self.a_create_container():
            await self.socket.send_bytes(
                msgpack.packb(
                    {
                        "command": "abort",
                        "container": self.container,
                        "object": self.path,
                        "reason": "Could not create or access the container.",
                    }
                )
            )
            self.failed = True

        b64_header = base64.standard_b64encode(header).decode("ascii")

        # Upload the header both to Vault and to Swift storage as failsafe during Vault introduction period
        await self.vault.put_header(
            self.name,
            self.container,
            self.path,
            b64_header,
            owner=self.owner_name,
        )

        self.tasks = [
            asyncio.create_task(self.upload_segment(i))
            for i in range(0, self.total_segments)
        ]

        await self.start_upload()

    async def start_upload(self):
        """Tell the frontend to start the file upload."""
        await self.socket.send_bytes(
            msgpack.packb(
                {
                    "command": "start_upload",
                    "container": self.container,
                    "object": self.path,
                }
            )
        )

    async def retry_chunk(self, order):
        """Retry a failed chunk."""
        await self.socket.send_bytes(
            msgpack.packb(
                {
                    "command": "retry_chunk",
                    "container": self.container,
                    "object": self.path,
                    "order": order,
                }
            )
        )

    async def add_to_chunks(
        self,
        order: int,
        data: bytes,
    ):
        """Add a chunk to cache."""
        if order in self.done_chunks or order in self.chunk_cache:
            return

        self.chunk_cache[order] = data

    async def a_create_container(self) -> bool:
        """Create the container required by the upload."""
        for container in {self.container, f"{self.container}_segments"}:
            async with self.client.head(
                common.generate_download_url(self.host, container),
                headers={"Content-Length": "0", "X-Auth-Token": self.token},
                ssl=ssl_context,
            ) as resp_get:
                if resp_get.status != 204:
                    async with self.client.put(
                        common.generate_download_url(self.host, container),
                        headers={"Content-Length": "0", "X-Auth-Token": self.token},
                        ssl=ssl_context,
                    ) as resp_put:
                        if resp_put.status not in {201, 202}:
                            return False
        return True

    async def slice_segment(self, segment: int):
        """Slice a ~5GiB segment from queue."""
        seg_start = segment * SEGMENT_CHUNKS
        seg_end = seg_start + SEGMENT_CHUNKS
        if segment == self.total_segments - 1 and self.total_chunks:
            # In case of the object size > SEGMENT_SIZE,
            # there are some variances between calculated variables
            # which can cause some missing chunks.
            # Using total_chunks for last segment's chunk amount
            # is more accurate than remainder_chunks
            LOGGER.debug(f"Using {self.total_chunks} as chunk amount for last segment.")
            seg_end = self.total_chunks
        LOGGER.debug(f"Consuming chunks {seg_start} through {seg_end}")

        # Start the upload
        LOGGER.debug(f"Generator yielding chunks from {seg_start} until {seg_end}.")
        for i in range(seg_start, seg_end):
            wait_count = 0
            while i not in self.chunk_cache:
                wait_count += 1
                await asyncio.sleep(0.1)
                # If handler has waited for too long for the next chunk, retry
                # Currently 60 seconds is considered too long
                if wait_count > 600:
                    try:
                        await self.retry_chunk(i)
                        wait_count = 0
                    except ConnectionResetError:
                        pass
            self.done_chunks.add(i)
            chunk = self.chunk_cache.pop(i)
            yield chunk

        # Finally yield eof
        yield b""
        return

    async def upload_segment(self, order: int) -> int:
        """Upload the segment with given ordering number."""
        seg_start = order * SEGMENT_CHUNKS
        # Wait until first chunk is available in cache, before starting the request
        LOGGER.debug(f"Waiting until first chunk in segment {order} is available.")
        while (seg_start) not in self.chunk_cache:
            await asyncio.sleep(0.1)
        LOGGER.debug(f"Got first chunk for segment {order}. Starting upload...")

        headers = {
            "X-Auth-Token": self.token,
            "Content-Type": "application/swiftclient-segment",
        }

        async with self.client.put(
            common.generate_download_url(
                self.host,
                container=f"{self.container}{common.SEGMENTS_CONTAINER}",
                object_name=f"{self.path}/{self.segment_id}/{(order + 1):08d}",
            ),
            data=self.slice_segment(order),
            headers=headers,
            timeout=UPL_TIMEOUT,
            ssl=ssl_context,
        ) as resp:
            LOGGER.info(f"Segment {order} finished with status {resp.status}.")

        if self.total_segments - 1 == order:
            LOGGER.info("Informing client that file was finished.")
            await self.socket.send_bytes(
                msgpack.packb(
                    {
                        "command": "success",
                        "container": self.container,
                        "object": self.path,
                    }
                )
            )
            self.finished = True

        return resp.status

    async def finish_upload(self):
        """Finalize the upload."""
        await asyncio.gather(*self.tasks)

        LOGGER.info(f"Add manifest for {self.path}.")
        async with self.client.put(
            common.generate_download_url(
                self.host,
                container=self.container,
                object_name=self.path,
            ),
            data=b"",
            headers={
                "X-Auth-Token": self.token,
                "X-Object-Manifest": f"{self.container}{common.SEGMENTS_CONTAINER}/{self.path}/{self.segment_id}/",
                "Content-Length": "0",
            },
            ssl=ssl_context,
        ) as resp:
            return aiohttp.web.Response(status=resp.status)

    async def abort_upload(self):
        """Abort the upload."""
        await self.socket.send_bytes(
            msgpack.packb(
                {
                    "command": "abort",
                    "container": self.container,
                    "object": self.path,
                    "reason": "cancel",
                }
            )
        )

        for task in self.tasks:
            if not task.done():
                task.cancel()
        asyncio.gather(*self.tasks)

        # Delete segments that might've been uploaded
        headers = {
            "X-Auth-Token": self.token,
            "Content-Type": "application/swiftclient-segment",
        }
        delete_tasks = [
            asyncio.create_task(
                self.client.delete(
                    common.generate_download_url(
                        self.host,
                        container=f"{self.container}{common.SEGMENTS_CONTAINER}",
                        object_name=f"{self.path}/{self.segment_id}/{(segment + 1):08d}",
                    ),
                    headers=headers,
                    ssl=ssl_context,
                )
            )
            for segment in range(0, self.total_segments)
        ]
        delete_resps = await asyncio.gather(*delete_tasks)
        delete_results = [resp.status for resp in delete_resps]
        LOGGER.info(f"Segment deletions finished with statuses: {delete_results}")


class UploadSession:
    """Class for handling upload websocket."""

    def __init__(
        self, request: aiohttp.web.Request, session: typing.Dict[str, typing.Any]
    ):
        """."""
        self.client: aiohttp.client.ClientSession = request.app["client"]
        self.vault: vault_client.VaultClient = request.app[common.VAULT_CLIENT]
        self.project: str = request.match_info["project"]
        self.session = session

        self.uploads: typing.Dict[str, typing.Dict[str, FileUpload]] = {}
        self.ws: aiohttp.web.WebSocketResponse | None = None

    def set_ws(self, ws: aiohttp.web.WebSocketResponse):
        """Set the websocket for the upload session."""
        self.ws = ws

    async def handle_begin_upload(self, msg: typing.Dict[str, typing.Any]) -> None:
        """Handle the upload start."""
        container: str = str(msg["container"])
        path: str = str(msg["object"])
        name: str = str(msg["name"])
        owner: str = ""
        owner_name: str = ""
        if "owner" in msg:
            owner = str(msg["owner"])
        if "owner_name" in msg:
            owner_name = str(msg["owner_name"])
        total = int(msg["total"])

        if container in self.uploads and path in self.uploads[container] and self.ws:
            await self.ws.send_bytes(
                msgpack.packb(
                    {
                        "command": "abort",
                        "container": container,
                        "object": path,
                        "reason": "Object is already being uploaded.",
                    }
                )
            )
            return

        if container not in self.uploads:
            self.uploads[container] = {}

        # We can ignore typing for self.ws, as these functions are only called after messages
        self.uploads[container][path] = FileUpload(
            self.client,
            self.vault,
            self.session,
            self.ws,  # type: ignore
            self.project,
            container,
            name,
            path,
            total,
            owner,
            owner_name,
        )

        await self.uploads[container][path].add_header(bytes(msg["data"]))

    async def handle_upload_chunk(self, msg: typing.Dict[str, typing.Any]):
        """Handle the addition of a new chunk."""
        container: str = str(msg["container"])
        path: str = str(msg["object"])

        await self.uploads[container][path].add_to_chunks(
            int(msg["order"]),
            bytes(msg["data"]),
        )

    async def handle_upload_chunks(self, msg: typing.Dict[str, typing.Any]):
        """Handle the addition of multiple new chunks."""
        container: str = str(msg["container"])
        path: str = str(msg["object"])

        for chunk in msg["chunks"]:
            await self.uploads[container][path].add_to_chunks(
                int(chunk["order"]),
                bytes(chunk["data"]),
            )

        if (
            container in self.uploads
            and path in self.uploads[container]
            and await self.uploads[container][path].wait_for_cache()
            and self.ws is not None
        ):
            await self.ws.send_bytes(
                msgpack.packb(
                    {
                        "command": "next",
                        "container": container,
                        "object": path,
                    }
                )
            )

    async def handle_finish_upload(self, msg: typing.Dict[str, typing.Any]):
        """Handle the upload end."""
        container: str = str(msg["container"])
        path: str = str(msg["object"])

        await self.uploads[container][path].finish_upload()
        self.uploads[container].pop(path)

    async def handle_close(self):
        """Gracefully close all ongoing uploads."""
        abort_tasks = []
        for container in self.uploads:
            for file in self.uploads[container]:
                abort_tasks.append(
                    asyncio.create_task(self.uploads[container][file].abort_upload())
                )
        await asyncio.gather(*abort_tasks)


def get_encrypted_upload_session(
    request: aiohttp.web.Request,
) -> UploadSession:
    """Return the specific encrypted upload session for the project."""
    session = common.get_session_id(request)
    project = request.match_info["project"]

    if project in request.app[session]["enuploads"]:
        LOGGER.debug(f"Returning an existing upload session for id {session}.")
        return request.app[session]["enuploads"][project]
    else:
        LOGGER.debug(f"Opening a new upload session for id {session}.")
        upload_session = UploadSession(request, request.app[session])
        request.app[session]["enuploads"][project] = upload_session
        return upload_session
