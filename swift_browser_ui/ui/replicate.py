"""Container and object replication handlers using aiohttp."""

import base64
import logging
import math
import os
from typing import Any

import aiohttp.web
import botocore.exceptions

import swift_browser_ui.common.vault_client

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

# Recommended 100MiB single copy limit
SINGLE_COPY_SIZE = 100 * 1024 * 1024
DEFAULT_PART_SIZE = 50 * 1024 * 1024
# See limits https://docs.aws.amazon.com/AmazonS3/latest/userguide/qfacts.html
MAX_PART_COUNT = 10000


class ObjectReplicator:
    """A class for replicating objects."""

    def __init__(
        self,
        s3client: Any,
        vault: swift_browser_ui.common.vault_client.VaultClient,
        project: str,
        bucket: str,
        source_project: str,
        source_bucket: str,
        project_name: str = "",
        source_project_name: str = "",
    ) -> None:
        """."""
        self.s3client = s3client
        self.vault = vault
        self.project = project
        self.bucket = bucket
        self.source_project = source_project
        self.source_bucket = source_bucket
        self.project_name = project_name
        self.source_project_name = source_project_name

    async def create_destination_bucket(self) -> None:
        """Create destination bucket required for copying."""
        # Destination bucket should not already exist
        try:
            await self.s3client.head_bucket(Bucket=self.bucket)
            raise aiohttp.web.HTTPConflict(text="Bucket already exists")
        except botocore.exceptions.ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                # Create the destination bucket
                try:
                    await self.s3client.create_bucket(Bucket=self.bucket)
                    LOGGER.info(f"Created destination bucket {self.bucket}")
                except botocore.exceptions.ClientError:
                    raise aiohttp.web.HTTPInternalServerError(
                        text="Failed to create destination bucket"
                    )
            elif error_code == "403":
                raise aiohttp.web.HTTPConflict(
                    text="Bucket already exists (Access denied)"
                )
            else:
                raise aiohttp.web.HTTPInternalServerError(
                    text="Cannot create destination bucket"
                )

    async def _multipart_copy(self, obj):
        """Make a multipart copy of an object."""
        size = obj["Size"]
        upload_id = (
            await self.s3client.create_multipart_upload(
                Bucket=self.bucket, Key=obj["Key"]
            )
        )["UploadId"]

        part_size = DEFAULT_PART_SIZE
        if size > part_size * MAX_PART_COUNT:
            part_size = math.ceil(size / MAX_PART_COUNT)
        parts = []
        part_number = 1
        byte_position = 0

        try:
            while byte_position < size:
                last_byte = min(byte_position + part_size - 1, size - 1)

                part = await self.s3client.upload_part_copy(
                    Bucket=self.bucket,
                    Key=obj["Key"],
                    CopySource={"Bucket": self.source_bucket, "Key": obj["Key"]},
                    CopySourceRange=f"bytes={byte_position}-{last_byte}",
                    PartNumber=part_number,
                    UploadId=upload_id,
                )

                parts.append(
                    {"ETag": part["CopyPartResult"]["ETag"], "PartNumber": part_number}
                )

                byte_position += part_size
                part_number += 1

            await self.s3client.complete_multipart_upload(
                Bucket=self.bucket,
                Key=obj["Key"],
                UploadId=upload_id,
                MultipartUpload={"Parts": parts},
            )
        except Exception:
            await self.s3client.abort_multipart_upload(
                Bucket=self.bucket, Key=obj["Key"], UploadId=upload_id
            )
            raise

    async def _replicate_object(self, obj) -> None:
        """Copy header and object."""
        key = obj["Key"]

        if obj["Size"] <= SINGLE_COPY_SIZE:
            try:
                await self.s3client.copy_object(
                    CopySource={"Bucket": self.source_bucket, "Key": key},
                    Bucket=self.bucket,
                    Key=key,
                )
            except Exception as e:
                LOGGER.exception(f"Failed to copy {key}: {e}")
        else:
            try:
                await self._multipart_copy(obj)
            except Exception as e:
                LOGGER.exception(f"Failed to multipart-copy {key}: {e}")

        if ".c4gh" in key and self.project_name:
            LOGGER.debug(f"Copying the header for encrypted object {key}")
            header = await self.vault.get_header(
                self.project_name,
                self.source_bucket,
                key,
                owner=self.source_project_name,
            )
            # Skip adding header if header was empty
            if header:
                await self.vault.put_header(self.project_name, self.bucket, key, header)

    async def replicate_objects(self) -> None:
        """Copy all bucket objects."""
        await self.check_public_key()
        try:
            paginator = self.s3client.get_paginator("list_objects_v2")

            async for page in paginator.paginate(Bucket=self.source_bucket):
                for obj in page.get("Contents", []):
                    await self._replicate_object(obj)
            LOGGER.info(f"Replication task for {self.source_bucket} finished")
        finally:
            await self.remove_public_key()

    async def check_public_key(self) -> None:
        """Check that the source project public key is whitelisted."""
        if self.project_name:
            pubkey = await self.vault.get_public_key(self.project_name)
            LOGGER.debug(
                f"Add public key of {self.project_name} temporarily for re-encryption."
            )
            await self.vault.put_whitelist_key(
                self.project_name, "crypt4gh", base64.urlsafe_b64decode(pubkey)
            )

    async def remove_public_key(self) -> None:
        """Remove the project public key from whitelist if it's been added."""
        if self.project_name:
            await self.vault.remove_whitelist_key(self.project_name)
