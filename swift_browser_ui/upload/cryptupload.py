"""Server upload propxy using aiohttp."""


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

        self.endpoint: str = session["endpoint"]
        self.token: str = session["token"]

        self.host = common.get_download_host(
            self.endpoint,
            self.project,
        )

        self.chunk_cache: typing.Dict[int, typing.Tuple[bytes, aiohttp.web.WebSocketResponse]] = {}
        self.q_cache: typing.List[asyncio.Queue] = []

    def check_header(
        self,
    ) -> bool:
        return self.header_uploaded

    async def add_header(
        self,
        request: aiohttp.web.Request,
    ) -> aiohttp.web.Response:
        """Add header for the uploaded file."""
        self.project = request.match_info["project"]
        self.container = request.match_info["container"]
        self.object_name = request.match_info["object_name"]

        self.total = int(request.query["total"])

        self.total_segments = -(self.total // -SEGMENT_SIZE)
        self.remainder_segment = self.total % SEGMENT_SIZE
        self.total_chunks = -(self.total // -CHUNK_SIZE)
        self.remainder_chunk = self.total % CHUNK_SIZE

        LOGGER.info(f"total: {self.total}")
        LOGGER.info(f"segments: {self.total_segments}")
        LOGGER.info(f"chunks: {self.total_chunks}")

        self.q_cache = [
            asyncio.Queue(maxsize=256) for _ in range(0, self.total_segments)
        ]

        header = await request.content.read()

        resp = await self.client.put(
            common.generate_download_url(
                self.host,
                container=self.container,
                object_name=f"{common.SEGMENTS_PREFIX}{self.object_name}/{self.segment_id}/{0:08d}"
            ),
            data=header,
            headers={
                "X-Auth-Token": self.token,
                "Content-Type": "application/swiftclient-segment",
            },
            timeout=UPL_TIMEOUT,
            ssl=ssl_context,
        )
        if resp.status == 408:
            raise aiohttp.web.HTTPRequestTimeout()
        LOGGER.debug(f"Successfully uploaded header for {self.object_name}.")

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
                object_name=common.DATA_PREFIX + self.object_name,
            ),
            data=b"",
            headers={
                "X-Auth-Token": self.token,
                "X-Object-Manifest": f"{self.container}/{common.SEGMENTS_PREFIX}{self.object_name}",
            },
            ssl=ssl_context,
        ) as resp:
            return aiohttp.web.Response(
                status=resp.status
            )

    async def add_to_chunks(
        self,
        order: int,
        data: bytes,
        ws: aiohttp.web.WebSocketResponse,
    ):
        """Add a chunk to cache."""
        if order in self.done_chunks or order in self.chunk_cache:
            LOGGER.info(f"Skipping ready chunk {order}.")
            await ws.send_str("nextChunk")
            return
        self.chunk_cache[order] = (data, ws)

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
        n_chunk = segment * 81885

        LOGGER.info(f"Beginning from chunk {n_chunk}")
        LOGGER.info(f"Continuing until chunk {segment * 81885 + 81885}")

        LOGGER.info(f"Waiting for first chunk in segment {segment} to be available")
        while (segment * 81885) not in self.chunk_cache:
            await asyncio.sleep(0.05)
        LOGGER.info(f"First segment in {segment} found")

        # Start the upload
        await q.put("BEGIN")

        for i in range(
            segment * 81885,
            segment * 81885 + 81885
        ):
            while i not in self.chunk_cache:
                LOGGER.info(f"Waiting 1 sec for chunk {i}")
                await asyncio.sleep(1)
            self.done_chunks.add(i)
            chunk, ws = self.chunk_cache.pop(i)
            LOGGER.info(f"Queuing chunk {i} with length of {len(chunk)}")
            LOGGER.info(f"Asking for next chunk after consuming chunk {i}.")
            await ws.send_str("nextChunk")
            await q.put(chunk)

        await q.put("EOF")

    async def queue_generator(
        self,
        q: asyncio.Queue,
    ):
        """Consume the upload queue."""
        LOGGER.info("Starting consumption of the queue.")
        chunk = await q.get()
        while chunk != "EOF":
            LOGGER.info("Yielding next chunk.")
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
            "Content-Length": "5368708140",
        }
        if order == self.total_segments - 1 and self.remainder_segment:
            headers["Content-Length"] = str(self.remainder_segment)

        # Wait until queue starts – first item isn't part of the data
        LOGGER.info(f"Waiting for queue to start filling for segment {order}")
        cmd = await q.get()
        LOGGER.info(f"{cmd}")

        LOGGER.info(f"Queue for segment {order} has been started, starting upload")

        resp = await self.client.put(
            common.generate_download_url(
                self.host,
                container=self.container,
                object_name=f"{common.SEGMENTS_PREFIX}{self.object_name}/{self.segment_id}/{(order + 1):08d}",
            ),
            data=self.queue_generator(q),
            headers=headers,
            timeout=UPL_TIMEOUT,
            ssl=ssl_context,
        )
        LOGGER.info(f"Segment {order} finished with status {resp.status}")
        return resp.status
