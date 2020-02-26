"""Server object and container download handlers using aiohttp."""


import os
import queue
import threading

import aiohttp.web

import keystoneauth1.session

import requests

from .common import generate_download_url


class FileDownloadProxy:
    """A class for a single proxied download."""

    def __init__(
            self,
            auth: keystoneauth1.session.Session,
            chunk_size=128 * 1024
    ):
        """."""
        # Establish a queue for the proxied file parts
        # Total queue size 128 * 256 * 1024 = 32MiB for now
        self.q = queue.Queue(
            maxsize=os.environ.get("SWIFT_UPLOAD_RUNNER_PROXY_Q_SIZE", 256)
        )
        # Save the swift service
        self.auth = auth
        self.t_dload = None
        self.t_write = None
        self.chunk_size = chunk_size
        # SwiftService is only necessary in case of container or object
        # downloads
        self.service = None

    def get_q(self):
        """Return the proxy queue."""
        return self.q

    def download_into_queue(
            self,
            project,
            container,
            object_name
    ):
        """Download object chunks from stream into the queue."""
        with requests.get(
            generate_download_url(
                self.auth.get_endpoint(service_type="object-store"),
                container=container,
                object_name=object_name
            ),
            headers={
                "X-Auth-Token": self.auth.get_token()
            },
            stream=True
        ) as req:
            for chunk in req.iter_content(chunk_size=self.chunk_size):
                if chunk:
                    self.q.put(chunk)
            # Concatenate None to queue as EOF
            self.q.put(None)

    async def a_read(self):
        """Read a chunk from the queue asynchronously."""
        # Blocks until the queue has something to read
        return self.q.get()

    def read(self):
        """Read a chunk from the queue."""
        # Blocks until the queue has something to read
        return self.q.get()

    async def a_begin_download(
            self,
            project,
            container,
            object_name
    ):
        """Begin the download process."""
        self.t_dload = threading.Thread(
            target=self.download_into_queue,
            args=(
                project,
                container,
                object_name
            ),
            daemon=True
        )
        self.t_dload.start()

    async def a_write_to_response(
            self,
            resp: aiohttp.web.StreamResponse
    ):
        """Get the response serving the file."""
        while True:
            chunk = await self.a_read()
            if not chunk:
                await resp.write_eof()
                return
            await resp.write(chunk)
