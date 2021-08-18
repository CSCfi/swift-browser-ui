"""Module for publishing directories / files in OS Swift."""
# Made with Python fire for easy creation, may be improved in the future.


import subprocess  # nosec
import os
import sys
import logging
import asyncio
import time


import swift_x_account_sharing_bind
import fire


logging.basicConfig(
    format="%(levelname)-8s %(asctime)s | %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
)


class Publish:
    """Share and publish Openstack Swift containers."""

    @staticmethod
    def _get_address():
        """Discover the address for the object storage."""
        ret = subprocess.getoutput(["swift auth"])
        ret = ret.split("\n")[0]
        ret = ret.split("=")[1]
        return ret

    async def _push_share(self, container, recipient, rights):
        """Wrap the async share_new_access function."""
        client_url = os.environ.get("SWIFT_X_ACCOUNT_SHARING_URL", None)
        if not client_url:
            logging.log(
                logging.ERROR,
                "Swift X Account sharing API environment variables %s%s",
                "haven't been sourced. Please source the file if it is ",
                "available, or download a new one from the storage UI.",
            )
        async with swift_x_account_sharing_bind.SwiftXAccountSharing(
            client_url
        ) as client:
            await client.share_new_access(
                os.environ.get("OS_PROJECT_ID", None),
                container,
                recipient,
                rights,
                self._get_address(),
            )

    def share(self, container, recipient, *args):
        """Share an existing container."""
        logging.log(logging.INFO, "share called")
        logging.log(logging.INFO, args)
        tenant = os.environ.get("OS_PROJECT_ID", None)
        if not tenant:
            logging.log(
                logging.ERROR,
                "Openstack RC file hasn't been sourced in the working %s%s",
                "environment. Please source an Openstack RC file to enable",
                " the use of Openstack tools.",
            )
            sys.exit(-1)
        command = ["swift", "post", container]
        rights = []
        # If read access is specified in arguments, grant read access.
        if "r" in args:
            command.append("--read-acl")
            command.append(recipient + ":*")
            rights.append("r")
            rights.append("l")
        # If write access is specified in arguments, grant write access.
        if "w" in args:
            command.append("--write-acl")
            command.append(recipient + ":*")
            rights.append("w")

        logging.log(logging.INFO, f"Running POST: {command}")
        subprocess.call(command)  # nosec

        asyncio.run(self._push_share(container, [recipient], rights))

    def publish(self, path, recipient, *args):
        """
        Upload and share a new container.

        Usage: publish [file or directory] [receiving project] [access (r, w)]
        """
        if not os.environ.get("OS_PROJECT_ID", None):
            logging.log(
                logging.ERROR,
                "Openstack RC file hasn't been sourced in the working %s%s",
                "environment. Please source an Openstack RC file to enable",
                " the use of Openstack tools.",
            )
            sys.exit(-1)

        container = "shared-upload-" + recipient + "-" + time.strftime("%Y%m%d-%H%M%S")

        subprocess.call(["swift", "upload", container, path])  # nosec

        self.share(container, recipient, *args)


if __name__ == "__main__":
    try:
        fire.Fire(Publish)
    except Exception as e:
        logging.log(logging.ERROR, f"An error ocurred{': ' if e else ''}{e}.")
