"""Server object upload handlers using aiohttp."""


import os
import typing
import asyncio

import aiohttp.web
import aiohttp.client

import keystoneauth1.session

import swift_upload_runner.common as common


class ResumableFileUploadProxy:
    """A class for a single proxied upload."""

    def __init__(
            self,
            auth: keystoneauth1.session.Session,
            query: dict,
            match: dict,
            client: aiohttp.client.ClientSession
    ):
        """."""
        self.q: asyncio.PriorityQueue = asyncio.PriorityQueue(
            maxsize=int(
                os.environ.get("SWIFT_UPLOAD_RUNNER_PROXY_Q_SIZE", 3)
            )
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
        self.coro_upload: asyncio.Task

        # Get object storage host
        self.host: str = common.get_download_host(self.auth, self.project)
        self.url: str = common.generate_download_url(
            self.host,
            container=self.container,
            object_name=self.path
        )

        # If file is sized under 5GiB, the upload is not segmented
        self.segmented: bool = False
        if self.total_size >= 5368709120:
            self.segmented = True

    async def a_sync_segments(
            self
    ):
        """Synchronize segments from storage."""
        async with self.client.get(
            common.generate_download_url(
                common.get_download_host(self.auth, self.project),
                self.container + "_segments"
            ),
            headers={
                "X-Auth-Token": self.auth.get_token()
            }
        ) as resp:
            if resp.status in {200}:
                segments = await resp.text
                segments = segments.rstrip().lstrip().split("\n")
                segments = filter(
                    lambda i,
                    path=self.path: path in i, segments
                )
                if segments:
                    for segment in segments:
                        self.done_chunks.add(int(segment.split("/")[-1]))

    async def a_create_container(
            self,
            segmented=False
    ):
        """Create the container required by the upload."""
        container = \
            f"{self.container}_segments" if segmented else self.container
        async with self.client.put(
                common.generate_download_url(
                    common.get_download_host(self.auth, self.project),
                    container
                ),
                headers={
                    "Content-Length": str(0),
                    "X-Auth-Token": self.auth.get_token()
                }
        ) as resp:
            if resp.status not in {201, 202}:
                raise aiohttp.web.HTTPForbidden(
                    reason="Can't create the upload container."
                )

    async def a_check_container(
            self,
    ):
        """Check if the container is allowed."""
        async with self.client.head(
                common.generate_download_url(
                    common.get_download_host(self.auth, self.project),
                    self.container
                ),
                headers={
                    "X-Auth-Token": self.auth.get_token()
                }
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
                    f"{self.container}_segments"
                ),
                headers={
                    "X-Auth-Token": self.auth.get_token()
                }
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
            self.url,
            headers={
                "X-Auth-Token": self.auth.get_token()
            }
        ) as request:
            if request.status == 200:
                return aiohttp.web.Response(status=200)

        if chunk_number in self.done_chunks:
            return aiohttp.web.Response(status=200)

        raise aiohttp.web.HTTPNotFound(reason="Chunk not yet uploaded")

    async def a_add_manifest(
            self,
    ):
        """Add manifest file after segmented upload finish."""
        manifest = f"{self.container}_segments/{self.path}/"
        async with self.client.put(
            common.generate_download_url(
                self.host,
                container=self.container,
                object_name=self.path
            ),
            data=b"",
            headers={
                "X-Auth-Token": self.auth.get_token(),
                "X-Object-Manifest": manifest
            }
        ) as resp:
            if resp.status != 201:
                raise aiohttp.web.HTTPBadRequest()

    async def a_add_chunk(
            self,
            query: typing.Dict[str, typing.Any],
            chunk_reader: aiohttp.MultipartReader
    ) -> aiohttp.web.Response:
        """Add a chunk to the upload."""
        # Resumablejs begins counting from 1
        chunk_number = (query["resumableChunkNumber"]) - 1

        if chunk_number in self.done_chunks:
            return aiohttp.web.Response(status=200)

        if self.segmented:
            async with self.client.put(
                common.generate_download_url(
                    self.host,
                    container=self.container + "_segments",
                    object_name=f"""{self.path}/{chunk_number:08d}"""
                ),
                data=chunk_reader,
                headers={
                    "X-Auth-Token": self.auth.get_token(),
                    "Content-Length": query["resumableCurrentChunkSize"],
                    "Content-Type": "application/swiftclient-segment",
                }
            ) as resp:
                if resp.status == 408:
                    raise aiohttp.web.HTTPRequestTimeout()
                self.total_uploaded += int(query["resumableCurrentChunkSize"])
                if self.total_uploaded == self.total_size:
                    await self.a_add_manifest()
                self.done_chunks.add(chunk_number)
                return aiohttp.web.Response(status=201)
        else:
            await self.q.put((
                # Using chunk number as priority, to handle chunks in any
                # order
                chunk_number,
                {"query": query, "data": chunk_reader}
            ))

            if not self.done_chunks:
                self.coro_upload = asyncio.create_task(self.client.put(
                    self.url,
                    data=self.generate_from_queue(),
                    headers={
                        "X-Auth-Token": self.auth.get_token(),
                        "Content-Length": query["resumableTotalSize"]
                    }
                ))

            await self.a_wait_for_chunk(chunk_number)
            return aiohttp.web.Response(status=201)

    async def generate_from_queue(self):
        """Generate the response data form the internal queue."""
        while True:
            chunk_number, segment = await self.q.get()

            chunk_reader = segment["data"]
            chunk = await chunk_reader.read_chunk()
            while chunk:
                yield chunk
                chunk = await chunk_reader.read_chunk()

            self.total_uploaded += \
                segment["query"]["resumableCurrentChunkSize"]
            self.done_chunks.add(chunk_number)

            if (
                    len(self.done_chunks) ==
                    segment["query"]["resumableTotalChunks"]
            ):
                await self.coro_upload
                break

    async def a_wait_for_chunk(
            self,
            chunk_number: int
    ):
        """Wait asynchronously for a chunk to be written to the upload."""
        while True:
            if chunk_number in self.done_chunks:
                break
            # Unfortunate busywaiting for now
            await asyncio.sleep(0.25)

    def get_q(self) -> asyncio.PriorityQueue:
        """Return the proxy queue."""
        return self.q

    def get_segmented(self) -> bool:
        """Check if the upload is segmented."""
        return self.segmented

    def write(self):
        """Write one chunk of binary data to the upload."""
