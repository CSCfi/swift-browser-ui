"""Container and object replication handlers using aiohttp."""


import logging
import os
import ssl
import typing

import aiohttp.client
import aiohttp.web
import certifi

from swift_browser_ui.upload import common

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())


# The replication process needs a generous timeout, due to aiohttp having
# a default value of 5 minutes. This is too low for the replication
# process, as the segments can be up to 5 GiB in size.
# The new value is approx 4.5 hours.
REPL_TIMEOUT = 16384


class ObjectReplicationProxy:
    """A class for replicating objects."""

    def __init__(
        self,
        session: dict,
        client: aiohttp.client.ClientSession,
        project: str,
        container: str,
        source_project: str,
        source_container: str,
    ) -> None:
        """."""
        self.project = project
        self.container = container

        self.source_project = source_project
        self.source_container = source_container

        self.client = client

        self.endpoint: str = session["endpoint"]
        self.token: str = session["token"]
        self.host: str = common.get_download_host(self.endpoint, self.project)
        self.source_host: str = common.get_download_host(
            self.endpoint, self.source_project
        )

    async def a_generate_object_from_reader(
        self, resp: aiohttp.client.ClientResponse
    ) -> typing.AsyncGenerator:
        """Generate uploaded object chunks from a response."""
        number = 0
        while True:
            chunk = await resp.content.read(1048576)
            if not chunk:
                break
            yield chunk
            number += 1
        LOGGER.debug("Response stream complete.")

    async def a_create_container(self, segmented: bool = False) -> None:
        """Create the container required by the upload."""
        container = f"{self.container}_segments" if segmented else self.container
        LOGGER.debug(f"Creating container {container}")
        async with self.client.put(
            common.generate_download_url(self.host, container),
            headers={"Content-Length": str(0), "X-Auth-Token": self.token},
            ssl=ssl_context,
        ) as resp:
            if resp.status not in {201, 202}:
                raise aiohttp.web.HTTPForbidden(reason="Upload container creation failed")
        LOGGER.debug(f"Created container {container}")

    async def a_sync_object_segments(self, manifest: str) -> str:
        """Get object segments."""
        async with self.client.get(
            common.generate_download_url(
                self.source_host, container=manifest.split("/")[0]
            ),
            headers={
                "X-Auth-Token": self.token,
                "Accept-Encoding": "identity",
            },
            timeout=REPL_TIMEOUT,
            ssl=ssl_context,
        ) as resp:
            if resp.status == 404:
                raise aiohttp.web.HTTPNotFound(reason="Segment container not found")
            if resp.status == 403:
                raise aiohttp.web.HTTPForbidden(
                    reason="Segment container access not allowed"
                )
            prefix = manifest.replace(manifest.split("/")[0], "").lstrip("/")
            LOGGER.debug(f"Segment prefix: {prefix}")
            segments_str = await resp.text()
            segments_list = segments_str.lstrip().rstrip().split("\n")
            LOGGER.debug(f"Segments before filtering: {segments_list}")

            def filter_with_prefix(segment):
                return prefix in segment

            segments = list(filter(filter_with_prefix, segments_list))

        LOGGER.debug(f"Got following segments: {segments}")

        for segment in segments:
            from_url = common.generate_download_url(
                self.source_host, container=manifest.split("/")[0], object_name=segment
            )
            LOGGER.debug(f"Getting segment from url: {from_url}")
            async with self.client.get(
                from_url,
                headers={
                    "X-Auth-Token": self.token,
                    "Accept-Encoding": "identity",
                },
                timeout=REPL_TIMEOUT,
                ssl=ssl_context,
            ) as resp_g:
                length = int(resp_g.headers["Content-Length"])
                headers = {"X-Auth-Token": self.token}

                if resp_g.status not in {200, 201, 202}:
                    raise aiohttp.web.HTTPNotFound(reason="Segment not found")
                LOGGER.debug(f"Copying segment {segment}")
                headers["Content-Length"] = str(length)
                headers["Content-Type"] = resp_g.headers["Content-Type"]
                if "ETag" in resp_g.headers:
                    headers["ETag"] = resp_g.headers["ETag"]
                else:
                    LOGGER.error("ETag missing, maybe segments file empty")
                    raise aiohttp.web.HTTPUnprocessableEntity(
                        reason="ETag missing, maybe segments file empty"
                    )

                to_url = common.generate_download_url(
                    self.host, container=f"{self.container}_segments", object_name=segment
                )
                LOGGER.debug(f"Posting segment to url: {to_url}")
                async with self.client.put(
                    to_url,
                    data=self.a_generate_object_from_reader(resp_g),
                    headers=headers,
                    timeout=REPL_TIMEOUT,
                    ssl=ssl_context,
                ) as resp_p:
                    LOGGER.debug(f"Segment {segment} status {resp_p.status}")
                    if resp_p.status == 408:
                        raise aiohttp.web.HTTPRequestTimeout()
                    if resp_p.status not in {201, 202}:
                        raise aiohttp.web.HTTPBadRequest(reason="Segment upload failed")
                LOGGER.debug(f"Success in copying segment {segment}")

        new_manifest = manifest.replace(
            manifest.split("/")[0], f"{self.container}_segments"
        )
        return new_manifest

    async def a_copy_object(self, object_name: str) -> None:
        """Copy an object from a location."""
        # Get the object stream handle
        async with self.client.get(
            common.generate_download_url(
                self.source_host, container=self.source_container, object_name=object_name
            ),
            headers={
                "X-Auth-Token": self.token,
                "Accept-Encoding": "identity",
            },
            timeout=REPL_TIMEOUT,
            ssl=ssl_context,
        ) as resp_g:
            # If the source object doesn't exist, abort
            if resp_g.status != 200:
                raise aiohttp.web.HTTPBadRequest(reason="Source object fetch failed")
            LOGGER.debug(f"Got stream handle for {object_name}")

            # Ensure that the upload container exists
            await self.a_create_container()

            LOGGER.debug(f"Got headers: {resp_g.headers}")

            headers = {"X-Auth-Token": self.token}

            # Copy over metadata headers
            for i in resp_g.headers:
                if "X-Object-Meta-Usertags" in i:
                    headers[i] = resp_g.headers[i]

            # Ensure the segment container exists, since performing
            # segmented upload
            LOGGER.debug(f"Copying object {object_name}")
            await self.a_create_container(segmented=True)

            manifest = await self.a_sync_object_segments(
                resp_g.headers["X-Object-Manifest"]
            )

            LOGGER.debug("Uploading manifest")
            # Add manifest headers
            headers["X-Object-Manifest"] = manifest
            # Create manifest file
            async with self.client.put(
                common.generate_download_url(
                    self.host, container=self.container, object_name=object_name
                ),
                data=b"",
                headers=headers,
                timeout=REPL_TIMEOUT,
                ssl=ssl_context,
            ) as resp:
                if resp.status != 201:
                    raise aiohttp.web.HTTPInternalServerError(
                        reason="Object manifest creation failed"
                    )
            LOGGER.debug(f"Uploaded manifest for {object_name}")

    async def a_copy_from_container(self) -> None:
        """Copy objects from a source container."""
        LOGGER.debug(f"Fetching objects from container {self.source_container}")
        container_url = common.generate_download_url(
            self.source_host, container=self.source_container
        )
        LOGGER.debug(f"Container url: {container_url}")
        async with self.client.get(
            common.generate_download_url(
                self.source_host,
                container=self.source_container,
            ),
            headers={"X-Auth-Token": self.token},
            timeout=REPL_TIMEOUT,
            ssl=ssl_context,
        ) as resp:
            if resp.status != 200:
                LOGGER.debug(f"Container fetch failed with status {resp.status}")
                raise aiohttp.web.HTTPBadRequest(reason="Source container fetch failed")
            LOGGER.debug("Got container object listing")
            objects_text = await resp.text()
            objects_list = objects_text.rstrip().lstrip().split("\n")
            for i in objects_list:
                await self.a_copy_object(i)
