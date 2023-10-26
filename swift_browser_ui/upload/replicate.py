"""Container and object replication handlers using aiohttp."""


import base64
import logging
import os
import ssl
import typing

import aiohttp.client
import aiohttp.web
import certifi

import swift_browser_ui.common.vault_client
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
        session: typing.Dict[str, typing.Any],
        client: aiohttp.client.ClientSession,
        vault: swift_browser_ui.common.vault_client.VaultClient,
        project: str,
        container: str,
        source_project: str,
        source_container: str,
        project_name: str = "",
        source_project_name: str = "",
    ) -> None:
        """."""
        self.project = project
        self.container = container
        self.vault = vault

        self.source_project = source_project
        self.source_container = source_container

        self.project_name = project_name
        self.source_project_name = source_project_name

        self.client = client

        self.endpoint: str = session["endpoint"]
        self.token: str = session["token"]
        self.host: str = common.get_download_host(self.endpoint, self.project)
        self.source_host: str = common.get_download_host(
            self.endpoint, self.source_project
        )

    async def a_ensure_container(self, segmented: bool = False) -> None:
        """Ensure that the container required for copying exists."""
        container = f"{self.container}_segments" if segmented else self.container
        LOGGER.debug(f"Checking container {container}.")
        async with self.client.head(
            common.generate_download_url(self.host, container),
            headers={"X-Auth-Token": self.token},
            ssl=ssl_context,
        ) as resp:
            if resp.status in {200, 201, 202, 204}:
                LOGGER.info(f"Container '{container}' already exists.")
                raise aiohttp.web.HTTPConflict(reason="Container already exists.")
            if resp.status == 404:
                pass
            else:
                raise aiohttp.web.HTTPBadRequest(reason="No access to container.")

        async with self.client.put(
            common.generate_download_url(self.host, container),
            headers={"X-Auth-Token": self.token},
            ssl=ssl_context,
        ) as resp:
            if resp.status == 409:
                LOGGER.info(f"Container name '{container}' already in use.")
                raise aiohttp.web.HTTPConflict(reason="Container name already in use.")
            if resp.status not in {201, 202, 204, 200}:
                LOGGER.info(f"Container name '{container}' couldn't be created.")
                raise aiohttp.web.HTTPBadRequest(reason="Copy container creation failed.")

        LOGGER.info(f"Created container '{container}'.")

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

            def filter_with_prefix(segment: str) -> bool:
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
                    data=resp_g.content.iter_chunked(65564),
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

            LOGGER.debug(f"Got headers: {resp_g.headers}")

            headers = {"X-Auth-Token": self.token}

            length = int(resp_g.headers["Content-Length"])

            # Copy over metadata headers
            for i in resp_g.headers:
                if "X-Object-Meta-Usertags" in i:
                    headers[i] = resp_g.headers[i]

            if "X-Object-Manifest" not in resp_g.headers:
                LOGGER.info(f"Copying object {object_name} in full.")
                headers["Content-Length"] = str(length)
                headers["Content-Type"] = resp_g.headers["Content-Type"]
                if "ETag" in resp_g.headers:
                    headers["ETag"] = resp_g.headers["ETag"]
                else:
                    LOGGER.error("ETag missing, maybe segments file empty")
                    raise aiohttp.web.HTTPUnprocessableEntity(
                        reason="ETag missing, maybe segments file empty"
                    )
                async with self.client.put(
                    common.generate_download_url(self.host, self.container, object_name),
                    data=resp_g.content.iter_chunked(65564),
                    headers=headers,
                    timeout=REPL_TIMEOUT,
                    ssl=ssl_context,
                ) as resp_p:
                    if resp_p.status == 408:
                        raise aiohttp.web.HTTPRequestTimeout()
                    if resp_p.status not in {201, 202}:
                        raise aiohttp.web.HTTPBadRequest(
                            reason="Object segment upload failed"
                        )
                LOGGER.debug(f"Success in copying object {object_name}")
            else:
                # Ensure the segment container exists, since performing
                # segmented upload
                LOGGER.debug(f"Copying object {object_name} in segments.")

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

            if ".c4gh" in object_name and self.source_project_name and self.project_name:
                LOGGER.debug(f"Copying the header for encrypted object {object_name}")
                header = await self.vault.get_header(
                    self.project_name,
                    self.source_container,
                    object_name,
                    owner=self.source_project_name,
                )
                await self.vault.put_header(
                    self.project_name, self.container, object_name, header
                )

    async def check_public_key(self) -> None:
        """Check that the source project public key is whitelisted."""
        if self.project_name and self.source_project_name:
            pubkey = await self.vault.get_public_key(self.project_name)
            LOGGER.debug(
                f"Add public key of {self.project_name} temporarily for re-encryption."
            )
            await self.vault.put_whitelist_key(
                self.project_name, "crypt4gh", base64.urlsafe_b64decode(pubkey)
            )

    async def remove_public_key(self) -> None:
        """Remove the project public key from whitelist if it's been added."""
        if self.project_name and self.source_project_name:
            await self.vault.remove_whitelist_key(self.project_name)

    async def a_copy_single_object(self, object_name: str) -> None:
        """Only copy a single object."""
        await self.check_public_key()

        try:
            await self.a_copy_object(object_name)
        finally:
            await self.remove_public_key()

    async def a_get_container_page(self, marker: str = "") -> list[str]:
        """Get a single page of objects from a container."""
        async with self.client.get(
            common.generate_download_url(
                self.source_host,
                container=self.source_container,
            ),
            headers={"X-Auth-Token": self.token},
            params={"marker": marker} if marker else None,
            timeout=REPL_TIMEOUT,
            ssl=ssl_context,
        ) as resp:
            if resp.status >= 400:
                LOGGER.debug(f"Container fetch failed with status {resp.status}")
                raise aiohttp.web.HTTPBadRequest(
                    reason="Could not fetch source container."
                )

            if resp.status == 200:
                ret = await resp.text()
                return ret.rstrip().lstrip().split("\n")

            return []

    async def a_copy_from_container(self) -> None:
        """Copy objects from a source container."""
        LOGGER.debug(f"Fetching objects from container {self.source_container}")
        container_url = common.generate_download_url(
            self.source_host, container=self.source_container
        )
        LOGGER.debug(f"Container url: {container_url}")

        # Page through all the objects in a container
        to_copy: list[str] = []
        page = await self.a_get_container_page()
        while page:
            to_copy = to_copy + page
            page = await self.a_get_container_page(to_copy[-1])

        await self.check_public_key()

        try:
            for obj in to_copy:
                await self.a_copy_object(obj)
        finally:
            await self.remove_public_key()
