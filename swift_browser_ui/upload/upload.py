"""Server object upload handlers using aiohttp."""


import asyncio
import logging
import os
import ssl
import typing

import aiohttp.client
import aiohttp.web
import certifi

from swift_browser_ui.upload import common

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


# The upload process needs a generous timeout, due to aiohttp having a
# default limit of 5 minutes. This is too low for the purposes of the upload.
# The new value is approx 9 hours.
UPL_TIMEOUT = 32768


class ResumableFileUploadProxy:
    """A class for a single proxied upload."""

    def __init__(
        self,
        session: typing.Dict[str, typing.Any],
        query: typing.Dict[str, typing.Any],
        match: typing.Dict[str, typing.Any],
        client: aiohttp.client.ClientSession,
    ) -> None:
        """."""
        self.q: asyncio.PriorityQueue = asyncio.PriorityQueue(
            maxsize=int(os.environ.get("SWIFT_UPLOAD_RUNNER_PROXY_Q_SIZE", 3))
        )
        # Set of chunks that are already uploaded
        self.done_chunks: typing.Set[int] = set({})

        # Get project and container from match_info
        self.project = match["project"]
        self.container = match["container"]

        # Get file information from the query string
        self.chunk_size: int = int(query["resumableChunkSize"])
        self.total_size: int = int(query["resumableTotalSize"])
        self.total_chunks: int = int(query["resumableTotalChunks"])
        self.content_type: str = query["resumableType"]
        self.ident: str = query["resumableIdentifier"]
        self.filename: str = query["resumableFilename"]
        # Will use the relative path for object names
        self.path: str = query["resumableRelativePath"]

        self.total_uploaded = 0

        # Save the auth session information
        self.endpoint: str = session["endpoint"]
        LOGGER.info(f"Using endpoint: {self.endpoint}")
        self.host: str = common.get_download_host(
            self.endpoint,
            self.project,
        )
        self.token: str = session["token"]
        self.url: str = common.generate_download_url(
            self.host, container=self.container, object_name=self.path
        )

        # Get an aiohttp client
        self.client: aiohttp.client.ClientSession = client

        # declare concatenated upload coroutine
        self.coro_upload: typing.Awaitable[typing.Any]

        # If file is sized under 5GiB, the upload is not segmented
        self.segmented: bool = False
        if self.total_size >= 5368709120:
            self.segmented = True

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

    async def a_check_container(
        self,
    ) -> None:
        """Check if the container is allowed."""
        async with self.client.head(
            common.generate_download_url(self.host, self.container),
            headers={"X-Auth-Token": self.token},
            ssl=ssl_context,
        ) as resp:
            if resp.status != 204:
                if self.project not in self.endpoint:
                    raise aiohttp.web.HTTPBadRequest(
                        reason="No access to shared container"
                    )
                await self.a_create_container()

    async def a_check_segment(
        self,
        chunk_number: int,
    ) -> aiohttp.web.Response:
        """Check the existence of a segment."""
        # Check the existence of the object in the container first
        # Will also work with a manifest file, thus working with segmented
        # uploads as well
        async with self.client.head(
            self.url, headers={"X-Auth-Token": self.token}, ssl=ssl_context
        ) as request:
            if request.status == 200:
                return aiohttp.web.Response(status=200)

        if chunk_number in self.done_chunks:
            return aiohttp.web.Response(status=200)

        return aiohttp.web.HTTPNoContent(reason="Chunk not yet uploaded")

    async def a_add_manifest(
        self,
    ) -> None:
        """Add manifest file after segmented upload finish."""
        path = self.path
        manifest = f"{self.container}{common.SEGMENTS_CONTAINER}/{path}/"
        LOGGER.info(f"Add manifest to {manifest}.")
        async with self.client.put(
            common.generate_download_url(
                self.host, container=self.container, object_name=self.path
            ),
            data=b"",
            headers={
                "X-Auth-Token": self.token,
                "X-Object-Manifest": manifest,
            },
            ssl=ssl_context,
        ) as resp:
            if resp.status != 201:
                raise aiohttp.web.HTTPBadRequest()

    async def a_add_chunk(
        self, query: typing.Dict[str, typing.Any], chunk_reader: aiohttp.MultipartReader
    ) -> aiohttp.web.Response:
        """Add a chunk to the upload."""
        # Resumablejs begins counting from 1
        chunk_number = (query["resumableChunkNumber"]) - 1

        if chunk_number in self.done_chunks:
            return aiohttp.web.Response(status=200)

        LOGGER.debug(f"Adding chunk {chunk_number}")
        await self.q.put(
            (
                # Using chunk number as priority, enabling out-of-order chunks
                chunk_number,
                {"query": query, "data": chunk_reader},
            )
        )

        if not self.done_chunks:
            LOGGER.debug("Scheduling upload coroutine")
            self.coro_upload = asyncio.ensure_future(self.upload_file())

        if chunk_number + 1 == self.total_chunks:
            LOGGER.debug("Waiting for upload to finish")
            await self.coro_upload
        else:
            await self.a_wait_for_chunk(chunk_number)

        return aiohttp.web.Response(status=201)

    async def upload_file(self) -> None:
        """Upload the file with concatenated segments."""
        if not self.segmented:
            async with self.client.put(
                self.url,
                data=self.generate_from_queue(),
                headers={
                    "X-Auth-Token": self.token,
                    "Content-Length": str(self.total_size),
                    "Content-Type": str(self.content_type),
                },
                timeout=UPL_TIMEOUT,
                ssl=ssl_context,
            ) as resp:
                if resp.status == 408:
                    raise aiohttp.web.HTTPRequestTimeout()
                if resp.status == 411:
                    raise aiohttp.web.HTTPLengthRequired()
                if resp.status == 422:
                    raise aiohttp.web.HTTPUnprocessableEntity()
                else:
                    return

        # Otherwise segmented upload
        segment_number: int = 0
        path = self.path
        while len(self.done_chunks) < self.total_chunks:
            async with self.client.put(
                common.generate_download_url(
                    self.host,
                    container=f"{self.container}{common.SEGMENTS_CONTAINER}",
                    object_name=f"""{path}/{segment_number:08d}""",
                ),
                data=self.generate_from_queue(),
                headers={
                    "X-Auth-Token": self.token,
                    "Content-Type": "application/swiftclient-segment",
                },
                timeout=UPL_TIMEOUT,
                ssl=ssl_context,
            ) as resp:
                if resp.status == 408:
                    raise aiohttp.web.HTTPRequestTimeout()
                if self.total_uploaded == self.total_size:
                    await self.a_add_manifest()
                LOGGER.debug(f"Success in uploding chunk {segment_number}")
            segment_number += 1
        return

    async def generate_from_queue(self) -> typing.AsyncGenerator:
        """Generate the response data from the internal queue."""
        LOGGER.debug("Generating upload data from a queue.")

        initial_uploaded = self.total_uploaded

        while len(self.done_chunks) < self.total_chunks:
            chunk_number, segment = await self.q.get()

            if chunk_number in self.done_chunks:
                continue

            LOGGER.debug(f"Got chunk from chunk {chunk_number}")

            chunk_reader = segment["data"]
            chunk = await chunk_reader.read_chunk()
            while chunk:
                yield chunk
                chunk = await chunk_reader.read_chunk()

            LOGGER.debug(f"Chunk {chunk_number} exhausted.")

            self.total_uploaded += int(segment["query"]["resumableCurrentChunkSize"])
            self.done_chunks.add(chunk_number)

            # In case of a segmented upload cut the chunk at 1GiB or over
            if self.segmented and self.total_uploaded - initial_uploaded >= 1073741824:
                break

    async def a_wait_for_chunk(self, chunk_number: int) -> None:
        """Wait asynchronously for a chunk to be written to the upload."""
        LOGGER.debug(f"Waiting for chunk {chunk_number}")
        while True:
            if chunk_number in self.done_chunks:
                LOGGER.debug(f"Waited for chunk {chunk_number}")
                return
            # Unfortunate busywaiting for now
            await asyncio.sleep(0.25)

    def get_q(self) -> asyncio.PriorityQueue:
        """Return the proxy queue."""
        return self.q

    def get_segmented(self) -> bool:
        """Check if the upload is segmented."""
        return self.segmented

    def write(self) -> None:
        """Write one chunk of binary data to the upload."""
