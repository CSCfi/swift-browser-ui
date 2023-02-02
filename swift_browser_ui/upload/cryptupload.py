"""Server upload propxy using aiohttp."""
import base64
import os
import logging
import asyncio
import typing
import secrets

import ssl
import certifi

import aiohttp
import aiohttp.web

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


class EncryptedUploadProxy:
    """A class for an encrypted file upload."""

    def __init__(
        self,
        session: dict,
        client: aiohttp.client.ClientSession,
    ) -> None:
        """."""
        self.client = client

        self.header_uploaded = False

        self.total_uploaded = 0
        self.current_uploaded = 0
        self.current_segment: int = 0

        self.project = ""
        self.container = ""
        self.object_name = ""
        self.total = 0
        self.total_segments = 0

        self.segment_id = secrets.token_urlsafe(32)

        self.done_chunks: typing.Set = set({})
        self.total_chunks = 0
        self.remainder_segment = 0
        self.remainder_chunk = 0
        self.remainder_chunks = 0

        self.endpoint: str = session["endpoint"]
        self.token: str = session["token"]

        self.host = common.get_download_host(
            self.endpoint,
            self.project,
        )

        self.have_closed = False

        self.chunk_cache: typing.Dict[
            int, typing.Tuple[bytes, aiohttp.web.WebSocketResponse]
        ] = {}
        self.q_cache: typing.List[asyncio.Queue] = []

        self.ws: aiohttp.web.WebSocketResponse

    def check_header(
        self,
    ) -> bool:
        return self.header_uploaded

    async def a_create_container(self) -> None:
        """Create the container required by the upload."""
        async with self.client.head(
            common.generate_download_url(self.host, self.container),
            headers={"Content-Length": "0", "X-Auth-Token": self.token},
            ssl=ssl_context,
        ) as resp_get:
            if resp_get.status != 204:
                async with self.client.put(
                    common.generate_download_url(self.host, self.container),
                    headers={"Content-Length": "0", "X-Auth-Token": self.token},
                    ssl=ssl_context,
                ) as resp_put:
                    if resp_put.status not in {201, 202}:
                        raise aiohttp.web.HTTPForbidden(
                            reason="Upload container creation failed."
                        )

        async with self.client.head(
            common.generate_download_url(self.host, f"{self.container}_segments"),
            headers={"Content-Length": "0", "X-Auth-Token": self.token},
            ssl=ssl_context,
        ) as resp_get:
            if resp_get.status != 204:
                async with self.client.put(
                    common.generate_download_url(
                        self.host,
                        f"{self.container}_segments",
                    ),
                    headers={"Content-Length": "0", "X-Auth-Token": self.token},
                    ssl=ssl_context,
                ) as resp_put:
                    if resp_put.status not in {201, 202}:
                        raise aiohttp.web.HTTPForbidden(
                            reason="Upload segment container creation failed."
                        )

    async def add_header(
        self,
        request: aiohttp.web.Request,
    ) -> aiohttp.web.Response:
        """Add header for the uploaded file."""
        self.project = request.match_info["project"]
        self.container = request.match_info["container"]
        self.object_name = request.match_info["object_name"]

        await self.a_create_container()

        self.total = int(request.query["total"])

        self.total_segments = -(self.total // -SEGMENT_SIZE)
        self.remainder_segment = self.total % SEGMENT_SIZE
        self.total_chunks = -(self.total // -CHUNK_SIZE)
        self.remainder_chunk = self.total % CHUNK_SIZE
        self.remainder_chunks = -(self.remainder_segment // -CHUNK_SIZE)

        LOGGER.debug(f"total: {self.total}")
        LOGGER.debug(f"segments: {self.total_segments}")
        LOGGER.debug(f"chunks: {self.total_chunks}")

        self.q_cache = [asyncio.Queue(maxsize=256) for _ in range(0, self.total_segments)]

        header = await request.content.read()
        b64_header = base64.standard_b64encode(header).decode("ascii")

        # Upload the header both to Vault and to Swift storage as failsafe during Vault introduction period
        await request.app[common.VAULT_CLIENT].put_header(
            self.project, self.container, self.object_name, b64_header
        )

        self.header_uploaded = True

        return aiohttp.web.Response(
            status=201,
        )

    async def add_manifest(
        self,
    ) -> aiohttp.web.Response:
        """Add file DLO manifest."""
        LOGGER.info(f"Add manifest for {self.object_name}.")
        async with self.client.put(
            common.generate_download_url(
                self.host,
                container=self.container,
                object_name=self.object_name,
            ),
            data=b"",
            headers={
                "X-Auth-Token": self.token,
                "X-Object-Manifest": f"{self.container}{common.SEGMENTS_CONTAINER}/{self.object_name}/{self.segment_id}/",
            },
            ssl=ssl_context,
        ) as resp:
            return aiohttp.web.Response(status=resp.status)

    async def get_next_chunk(
        self,
        ws: aiohttp.web.WebSocketResponse,
    ) -> None:
        """Schedule fetching of the next chunk in order."""
        if len(self.done_chunks) >= self.total_chunks:
            return
        await ws.send_json({"cmd": "nextChunk"})

    async def retry_chunk(
        self,
        ws: aiohttp.web.WebSocketResponse,
        iter: int,
    ) -> None:
        """Retry a chunk via websocket."""

    async def add_to_chunks(
        self,
        order: int,
        data: bytes,
        ws: aiohttp.web.WebSocketResponse,
    ):
        """Add a chunk to cache."""
        if order in self.done_chunks or order in self.chunk_cache:
            try:
                await self.get_next_chunk(ws)
            except ConnectionResetError:
                pass
            return
        self.chunk_cache[order] = (data, ws)

    async def set_ws(self, ws: aiohttp.web.WebSocketResponse):
        """Add instance WebSocket."""
        self.ws = ws

    def return_total_segments(self) -> int:
        """Get total segment amount."""
        return self.total_segments

    def get_segment_queue(self, i) -> asyncio.Queue:
        """Create and return an asyncio queue for segment."""
        return self.q_cache[i]

    async def slice_into_queue(
        self,
        segment: int,
        q: asyncio.Queue,
    ):
        """Slice an almost 5GiB segment from queue (short by 980 bytes)."""
        n_chunk = segment * SEGMENT_CHUNKS

        LOGGER.debug(f"Beginning from chunk {n_chunk}")
        LOGGER.debug(
            f"Continuing until chunk {segment * SEGMENT_CHUNKS + SEGMENT_CHUNKS}"
        )
        LOGGER.debug(f"Waiting for first chunk in segment {segment} to be available")

        while (segment * SEGMENT_CHUNKS) not in self.chunk_cache:
            await asyncio.sleep(0.05)
        LOGGER.debug(f"First segment in {segment} found")

        # Start the upload
        await q.put("BEGIN")

        seg_start = segment * SEGMENT_CHUNKS
        seg_end = segment * SEGMENT_CHUNKS + SEGMENT_CHUNKS
        if segment == self.total_segments - 1 and self.remainder_chunks:
            LOGGER.debug(f"Using {self.remainder_chunks} as chunk amount for last chunk.")
            seg_end = segment * SEGMENT_CHUNKS + self.remainder_chunks

        LOGGER.debug(f"Pushing chunks from {seg_start} until {seg_end} to queue.")

        for i in range(seg_start, seg_end):
            wait_count = 0
            while i not in self.chunk_cache:
                wait_count += 1
                await asyncio.sleep(0.05)
                # if handler has waited too long for the next chunk, ask for it again.
                # 10 seconds is considered too long
                if wait_count > 2000:
                    await self.retry_chunk(self.ws, i)
                    wait_count = 0
            self.done_chunks.add(i)
            chunk, ws = self.chunk_cache.pop(i)
            await q.put(chunk)
            LOGGER.debug(f"Put chunk {i} to the queue.")
            try:
                await self.get_next_chunk(ws)
            except ConnectionResetError:
                pass

        LOGGER.debug(f"Pushging eof for {self.object_name}.")

        await q.put("EOF")

    async def queue_generator(
        self,
        q: asyncio.Queue,
    ):
        """Consume the upload queue."""
        LOGGER.debug("Starting consumption of the queue.")
        chunk = await q.get()
        while chunk != "EOF":
            yield chunk
            chunk = await q.get()

    async def upload_segment(
        self,
        order: int,
    ) -> int:
        """Upload the segment with given ordering number."""
        # Fetch the queue from storage
        q = self.q_cache[order]
        headers = {
            "X-Auth-Token": self.token,
            "Content-Type": "application/swiftclient-segment",
        }
        # Wait until queue starts – first item isn't part of the data
        LOGGER.debug(f"Waiting for queue to start filling for segment {order}")
        await q.get()

        LOGGER.debug(f"Queue for segment {order} has been started, starting upload")

        async with self.client.put(
            common.generate_download_url(
                self.host,
                container=f"{self.container}{common.SEGMENTS_CONTAINER}",
                object_name=f"{self.object_name}/{self.segment_id}/{(order + 1):08d}",
            ),
            data=self.queue_generator(q),
            headers=headers,
            timeout=UPL_TIMEOUT,
            ssl=ssl_context,
        ) as resp:
            LOGGER.info(f"Segment {order} finished with status {resp.status}")

        if self.total_segments - 1 == order:
            LOGGER.info("Closing websocket after finishing last segment.")
            self.have_closed = True
            if self.ws is not None:
                await self.ws.send_json({"cmd": "canClose"})

        return resp.status
