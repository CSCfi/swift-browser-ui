"""Server object upload handlers using aiohttp."""


import os
import typing
import asyncio
import logging

import aiohttp.web
import aiohttp.client

import keystoneauth1.session

import swift_upload_runner.common as common

import ssl
import certifi


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
        auth: keystoneauth1.session.Session,
        query: dict,
        match: dict,
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

        # Save the swift service
        self.auth = auth

        # Get an aiohttp client
        self.client: aiohttp.client.ClientSession = client

        # declare concatenated upload coroutine
        self.coro_upload: typing.Awaitable[typing.Any]

        # Get object storage host
        self.host: str = common.get_download_host(self.auth, self.project)
        self.url: str = common.generate_download_url(
            self.host, container=self.container, object_name=self.path
        )

        # If file is sized under 5GiB, the upload is not segmented
        self.segmented: bool = False
        if self.total_size >= 5368709120:
            self.segmented = True

    async def a_create_container(self, segmented: bool = False) -> None:
        """Create the container required by the upload."""
        container = f"{self.container}_segments" if segmented else self.container
        async with self.client.put(
            common.generate_download_url(
                common.get_download_host(self.auth, self.project), container
            ),
            headers={"Content-Length": str(0), "X-Auth-Token": self.auth.get_token()},
            ssl=ssl_context,
        ) as resp:
            if resp.status not in {201, 202}:
                raise aiohttp.web.HTTPForbidden(reason="Upload container creation failed")

    async def a_check_container(
        self,
    ) -> None:
        """Check if the container is allowed."""
        async with self.client.head(
            common.generate_download_url(
                common.get_download_host(self.auth, self.project), self.container
            ),
            headers={"X-Auth-Token": self.auth.get_token()},
            ssl=ssl_context,
        ) as resp:
            if resp.status != 204:
                if self.project != self.auth.get_project_id():
                    raise aiohttp.web.HTTPBadRequest(
                        reason="No access to shared container"
                    )
                await self.a_create_container()
        if self.segmented:
            async with self.client.head(
                common.generate_download_url(
                    common.get_download_host(self.auth, self.project),
                    f"{self.container}_segments",
                ),
                headers={"X-Auth-Token": self.auth.get_token()},
                ssl=ssl_context,
            ) as resp:
                if resp.status != 204:
                    if self.project != self.auth.get_project_id():
                        raise aiohttp.web.HTTPBadRequest(
                            reason="No access to shared segments"
                        )
                    await self.a_create_container(segmented=True)

    async def a_check_segment(
        self,
        chunk_number: int,
    ) -> aiohttp.web.Response:
        """Check the existence of a segment."""
        # Check the existence of the object in the container first
        # Will also work with a manifest file, thus working with segmented
        # uploads as well
        async with self.client.head(
            self.url, headers={"X-Auth-Token": self.auth.get_token()}, ssl=ssl_context
        ) as request:
            if request.status == 200:
                return aiohttp.web.Response(status=200)

        if chunk_number in self.done_chunks:
            return aiohttp.web.Response(status=200)

        raise aiohttp.web.HTTPNotFound(reason="Chunk not yet uploaded")

    async def a_add_manifest(
        self,
    ) -> None:
        """Add manifest file after segmented upload finish."""
        manifest = f"{self.container}_segments/{self.path}/"
        LOGGER.info(f"Add manifest to {self.container}_segments.")
        async with self.client.put(
            common.generate_download_url(
                self.host, container=self.container, object_name=self.path
            ),
            data=b"",
            headers={
                "X-Auth-Token": self.auth.get_token(),
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
                    "X-Auth-Token": self.auth.get_token(),
                    "Content-Length": str(self.total_size),
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
        while len(self.done_chunks) < self.total_chunks:
            async with self.client.put(
                common.generate_download_url(
                    self.host,
                    container=self.container + "_segments",
                    object_name=f"""{self.path}/{segment_number:08d}""",
                ),
                data=self.generate_from_queue(),
                headers={
                    "X-Auth-Token": self.auth.get_token(),
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
