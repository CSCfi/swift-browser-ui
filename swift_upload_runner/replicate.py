"""Container and object replication handlers using aiohttp."""


import logging

import aiohttp.web
import aiohttp.client

import keystoneauth1.session

import swift_upload_runner.common as common


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class ObjectReplicationProxy():
    """A class for replicating objects."""

    def __init__(
            self,
            auth: keystoneauth1.session.Session,
            client: aiohttp.client.ClientSession,
            project: str,
            container: str,
            source_project: str,
            source_container: str,
    ):
        """."""
        self.project = project
        self.container = container

        self.source_project = source_project
        self.source_container = source_container

        self.auth = auth
        self.host: str = common.get_download_host(self.auth, self.project)
        self.source_host: str = common.get_download_host(
            self.auth,
            self.source_project
        )

    async def a_generate_object_from_reader(
            self,
            resp: aiohttp.client.ClientResponse
    ):
        """Generate uploaded object chunks from a response."""
        chunk = await resp.content.read(1048576)

        while chunk:
            yield chunk
            chunk = await resp.content.read(1048576)

    async def a_generate_object_segment_from_reader(
            self,
            resp: aiohttp.client.ClientResponse
    ):
        """Generate next uploaded object segment from a response."""
        # Yield at max 5GiB of information in a segment
        for i in range(0, 5120):
            chunk = await resp.content.read(1048576)
            if not chunk:
                break
            yield chunk

    async def a_create_container(
            self,
            segmented=False
    ):
        """Create the container required by the upload."""
        container = \
            f"{self.container}_segments" if segmented else self.container
        LOGGER.debug(f"Creating container {container}")
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
        LOGGER.debug(f"Created container {container}")

    async def a_copy_object(
            self,
            object_name
    ):
        """Copy an object from a location."""
        # Get the object stream handle
        async with self.client.get(
                common.generate_download_url(
                    self.source_host,
                    container=self.source_container,
                    object_name=object_name
                ),
                headers={
                    "X-Auth-Token": self.auth.get_token()
                }
        ) as resp_g:
            # If the source object doesn't exist, abort
            if resp_g.status != 200:
                raise aiohttp.web.HTTPBadRequest(
                    reason="Couldn't fetch the source object."
                )
            LOGGER.debug(f"Got stream handle for {object_name}")

            # Ensure that the upload container exists
            await self.a_create_container()

            headers = {
                "X-Auth-Token": self.auth.get_token()
            }

            length = int(resp_g.headers["Content-Length"])

            # Copy over metadata headers
            for i in resp_g.headers:
                if "Meta" in resp_g.headers[i]:
                    headers[i] = resp_g.headers[i]

            # If the object fits into the 5GiB limit imposed by Swift
            if length <= 5368709120:
                LOGGER.debug(f"Copying object {object_name} in full.")
                headers["Content-Length"] = str(length)
                headers["Content-Type"] = resp_g.headers["Content-Type"]
                headers["ETag"] = resp_g.headers["ETag"]
                async with self.client.put(
                        common.generate_download_url(
                            self.host,
                            self.container,
                            object_name
                        ),
                        data=self.a_generate_object_from_response(resp_g),
                        headers=headers
                ) as resp_p:
                    if resp_p.status == 408:
                        raise aiohttp.web.HTTPRequestTimeout()
                LOGGER.debug(f"Success in copying object {object_name}")
            else:
                # Ensure the segment container exists, since performing
                # segmented upload
                LOGGER.debug(f"Copying object {object_name} in segments.")
                await self.a_create_container(segmented=True)
                total_chunks = length // 5368709120 + 1
                size_left = length

                LOGGER.debug(f"Copying in total {total_chunks} chunks")

                for i in range(0, total_chunks):
                    async with self.client.put(
                            common.generate_download_url(
                                self.host,
                                container=f"{self.container}_segments",
                                object_name=f"{object_name}/{i:08d}"
                            ),
                            data=self.a_generate_object_segment_from_reader(
                                resp_g
                            ),
                            headers={
                                "X-Auth-Token": self.auth.get_token(),
                                "Content-Length": (
                                    size_left if size_left > 5368709120
                                    else 5368709120
                                ),
                                "Content-Type":
                                    "application/swiftclient-segment"
                            }
                    ) as resp:
                        if resp.status == 408:
                            raise aiohttp.web.HTTPRequestTimeout()
                        size_left -= 5368709120
                        LOGGER.debug(f"Copied chunk {i}")
                        LOGGER.debug(f"{size_left} bytes left")

                LOGGER.debug("Uploading manifest")
                # Add manifest headers
                manifest = f"{self.container}_segments/{object_name}/"
                headers["X-Object-Manifest"]: manifest
                # Create manifest file
                async with self.client.put(
                        common.generate_download_url(
                            self.host,
                            container=self.container,
                            object_name=object_name
                        ),
                        data=b"",
                        headers=headers
                ) as resp:
                    if resp.status != 201:
                        raise aiohttp.web.HTTPInternalServerError(
                            reason="Manifest creation failure."
                        )
                LOGGER.debug(f"Uploaded manifest for {object_name}")

    async def a_copy_from_container(self):
        """Copy objects from a source container."""
        async with self.client.get(
                common.generate_download_url(
                    self.source_host,
                    container=self.source_container,
                ),
                headers={
                    "X-Auth-Token": self.auth.get_token()
                }
        ) as resp:
            if resp.status != 200:
                raise aiohttp.web.HTTPBadRequest(
                    reason="Couldn't fetch the source container"
                )
                LOGGER.debug("Got container object listing")
                objects = await resp.text()
                objects = objects.rstrip().lstrip().split("\n")
                for i in objects:
                    self.a_copy_object(i)
