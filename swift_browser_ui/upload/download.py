"""Server object and container download handlers using aiohttp."""


import os
import queue
import threading
import typing
import tarfile
import time
import asyncio
import logging

import aiohttp.web

import keystoneauth1.session

import requests

from .common import generate_download_url, get_path_from_list
from .common import get_download_host


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


# Unlike other classes, download uses python-requests for fetching objects
# to simplify threading. Thus, timing out is not the default behavior.


class FileDownloadProxy:
    """A class for a single proxied download."""

    def __init__(
        self, auth: keystoneauth1.session.Session, chunk_size: int = 128 * 1024
    ) -> None:
        """."""
        # Establish a queue for the proxied file parts
        # Total queue size 128 * 256 * 1024 = 32MiB for now
        self.q: queue.Queue = queue.Queue(
            maxsize=int(os.environ.get("SWIFT_UPLOAD_RUNNER_PROXY_Q_SIZE", 256))
        )
        # Save the swift service
        self.auth = auth
        self.t_dload: typing.Optional[threading.Thread] = None
        self.t_write: typing.Optional[threading.Thread] = None
        self.chunk_size: int = chunk_size
        self.content_type: str
        self.size: int
        self.chksum: str
        self.mtime: int

    def get_q(self) -> queue.Queue:
        """Return the proxy queue."""
        return self.q

    def get_type(self) -> str:
        """Return the incoming file type."""
        return self.content_type

    def get_size(self) -> int:
        """Return the incoming file size."""
        return self.size

    def get_chksum(self) -> typing.Optional[str]:
        """Return the checksum."""
        return self.chksum

    async def a_get_type(self) -> str:
        """Return the eventual incoming file type."""
        try:
            return self.get_type()
        except AttributeError:
            await asyncio.sleep(0.01)
            return await self.a_get_type()

    async def a_get_size(self) -> int:
        """Return the eventual incoming file size."""
        try:
            return self.get_size()
        except AttributeError:
            await asyncio.sleep(0.01)
            return await self.a_get_size()

    async def a_get_checksum(self) -> typing.Optional[str]:
        """Return the eventual checksum."""
        try:
            return self.get_chksum()
        except AttributeError:
            await asyncio.sleep(0.01)
            return await self.a_get_checksum()

    def get_mtime(self) -> int:
        """Return the time of last modification."""
        return self.mtime

    def download_into_queue(self, project: str, container: str, object_name: str) -> None:
        """Download object chunks from stream into the queue."""
        LOGGER.info(
            f"Downloading from project {project}, "
            f"from container {container}, "
            f"the file {object_name}"
        )
        with requests.get(
            generate_download_url(
                get_download_host(self.auth, project),
                container=container,
                object_name=object_name,
            ),
            headers={
                "X-Auth-Token": self.auth.get_token(),
                "Accept-Encoding": "identity",
            },
            stream=True,
            verify=True,
        ) as req:
            LOGGER.info(f"Request headers: {req.headers}")
            try:
                self.content_type = req.headers["Content-Type"]
            except KeyError:
                self.content_type = "binary/octet-stream"
            if "ETag" in req.headers:
                self.chksum = req.headers["ETag"]
            else:
                LOGGER.error("ETag missing, maybe segments file empty")
                raise aiohttp.web.HTTPUnprocessableEntity(
                    reason="ETag missing, maybe segments file empty"
                )
            self.mtime = int(float(req.headers["X-Timestamp"]))
            self.size = int(req.headers["Content-Length"])
            for chunk in req.iter_content(chunk_size=self.chunk_size):
                if chunk:
                    self.q.put(chunk)
            # Concatenate NUL to queue as EOF
            self.q.put(b"")

    async def a_read(self) -> bytes:
        """Read a chunk from the queue asynchronously."""
        # Blocks until the queue has something to read
        while True:
            try:
                return self.q.get(block=False)
            except queue.Empty:
                await asyncio.sleep(0.01)

    def read(self) -> bytes:
        """Read a chunk from the queue."""
        # Blocks until the queue has something to read
        return self.q.get()

    async def a_begin_download(
        self, project: str, container: str, object_name: str
    ) -> None:
        """Begin the download process."""
        self.begin_download(project, container, object_name)

    def begin_download(self, project: str, container: str, object_name: str) -> None:
        """Begin the download process."""
        self.t_dload = threading.Thread(
            target=self.download_into_queue,
            args=(project, container, object_name),
            daemon=True,
        )
        self.t_dload.start()

    async def a_write_to_response(self, resp: aiohttp.web.StreamResponse) -> None:
        """Get the response serving the file."""
        while True:
            chunk = await self.a_read()
            if not chunk:
                await resp.write_eof()
                return
            await resp.write(chunk)


class TarInputWrapper:
    """Wrap the file download proxy for tar to treat as a binary file."""

    def __init__(
        self,
        auth: keystoneauth1.session.Session,
        project: str,
        container: str,
        object_name: str,
    ) -> None:
        """."""
        # Initialize the download class
        self.dload = FileDownloadProxy(auth)

        self.project = project
        self.container = container
        self.object_name = object_name

        self.last_chunk: bytes

    def get_dload(self) -> FileDownloadProxy:
        """Return the specific download instance."""
        return self.dload

    def begin_download(self) -> None:
        """Begin download and block until received headers."""
        self.dload.begin_download(self.project, self.container, self.object_name)

        # Will block until first chunk is received
        self.last_chunk = self.dload.read()

    def read(self, length: int) -> bytes:
        """Read function mimicking BytesIO read."""
        ret: bytes = self.last_chunk[:length]

        if len(ret) < length:
            # If couldn't get a whole chunk, pop next chunk from queue
            remainder = length - len(ret)
            self.last_chunk = self.dload.read()
            # Read remaining bytes recursively
            ret += self.read(remainder)
        else:
            # Slice off the returned part
            self.last_chunk = self.last_chunk[length:]

        return ret


class TarQueueWrapper:
    """Wrap queue.Queue class for tar to treat as a binary file."""

    def __init__(self) -> None:
        """."""
        self.q: queue.Queue = queue.Queue(
            maxsize=int(os.environ.get("SWIFT_UPLOAD_RUNNER_PROXY_Q_SIZE", 1024))
        )

    def write(self, payload: bytes = None) -> None:
        """Emulate BytesIO write function to be used with tarfile."""
        self.q.put(payload)

    def read(self) -> bytes:
        """Read next chunk."""
        return self.q.get()

    def get_q(
        self,
    ) -> queue.Queue:
        """Return the queue."""
        return self.q

    async def a_read(self) -> bytes:
        """Asynchronously read next chunk."""
        while True:
            try:
                return self.q.get(block=False)
            except queue.Empty:
                await asyncio.sleep(0.01)


class ContainerArchiveDownloadProxy:
    """Class for downloading a whole container as an archive."""

    def __init__(
        self,
        auth: keystoneauth1.session.Session,
        project: str,
        container: str,
        chunk_size: int = 128 * 1024,
    ) -> None:
        """."""
        self.auth = auth
        self.download_queue: queue.Queue = queue.Queue(maxsize=3)

        self.output_queue = TarQueueWrapper()

        self.project = project
        self.container = container
        self.chunk_size = chunk_size

        self.archive: tarfile.TarFile
        self.fs: dict

        self.archiving_thread: threading.Thread
        self.downloader_thread: threading.Thread

    @staticmethod
    def _filter_by_root(
        root: str,
        item: typing.List[str],
    ) -> bool:
        """Check if the file derives from fs root."""
        return item[0] == root

    @staticmethod
    def _parse_archive_fs(
        to_parse: typing.List[typing.List[str]],  # list of file paths
        path_prefix: str = "",
    ) -> dict:
        """Parse a list of paths into a dict representing a filesystem."""
        ret_fs: dict = {}
        for path in to_parse:
            LOGGER.info(f"working path: {path}")
            # Path of zero means an incorrect input
            if len(path) == 0:
                raise ValueError("Tried to archive a file without a name")
            # Path of > 1 implies a directory in between
            # Create TarInfo for the directory
            if len(path) > 1:
                if path[0] in ret_fs.keys():
                    LOGGER.debug(f"Skipping path {path} as added.")
                    continue

                LOGGER.debug(f"Adding directory for {path[0]} {path_prefix}")
                new_info = tarfile.TarInfo(
                    name=get_path_from_list([path[0] + "/"], path_prefix)
                )

                # Set default directory rights (755)
                new_info.mode = 493  # default to d u+wrx g+rx a+rx
                # Set type to directory
                new_info.type = tarfile.DIRTYPE
                new_info.mtime = int(time.time())

                dir_contents = []
                for i in to_parse:
                    if ContainerArchiveDownloadProxy._filter_by_root(path[0], i):
                        dir_contents.append(i)

                LOGGER.debug(f"Dir {path[0]} contents: {dir_contents}")

                ret_fs[path[0]] = {
                    "name": get_path_from_list([path[0]], path_prefix),
                    "type": "folder",
                    "tar_info": new_info,
                    "contents": ContainerArchiveDownloadProxy._parse_archive_fs(
                        [i[1:] for i in dir_contents],
                        get_path_from_list([path[0]], path_prefix),
                    ),
                }
            # Path of == 1 implies a file
            else:
                # Create file TarInfo class
                LOGGER.debug(f"Adding file {path} to {path_prefix}")
                new_info = tarfile.TarInfo(name=get_path_from_list(path, path_prefix))

                # Set rights as the info is not given by openstack
                new_info.mode = 420  # default to u+wr g+r a+r

                # Add to fs representation
                ret_fs[path[0]] = {
                    "name": get_path_from_list(path, path_prefix),
                    "type": "file",
                    "tar_info": new_info,
                }

        return ret_fs

    def get_object_listing(
        self,
    ) -> None:
        """Synchronize the list of objects to download."""
        with requests.get(
            generate_download_url(
                get_download_host(self.auth, self.project), container=self.container
            ),
            headers={"X-Auth-Token": self.auth.get_token()},
            verify=True,
        ) as req:
            self.fs = self._parse_archive_fs(
                [i.split("/") for i in req.text.lstrip().rstrip().split("\n")]
            )

    def sync_folders(self, fs: dict) -> None:
        """Sycnhronize the folders into the tar archive."""
        if self.archive:
            for i in fs:
                if fs[i]["type"] == "folder":
                    self.archive.addfile(fs[i]["tar_info"])
                    self.sync_folders(fs[i]["contents"])

    def download_init(
        self,
    ) -> None:
        """Create download init."""
        self.download_init_loop(self.fs)
        self.download_queue.put(None)

    def download_init_loop(self, fs: dict) -> None:
        """Loop to run for initializing downloads."""
        if self.archive:
            for i in fs:
                if fs[i]["type"] == "folder":
                    self.download_init_loop(fs[i]["contents"])
                else:
                    tar_info = fs[i]["tar_info"]
                    fileobj = TarInputWrapper(
                        self.auth, self.project, self.container, tar_info.name
                    )

                    self.download_queue.put({"fileobj": fileobj, "tar_info": tar_info})

    def tar_archiving_loop(
        self,
    ) -> None:
        """Loop to run for initializing tarballing."""
        while True:
            next_file = self.download_queue.get()

            if next_file is None:
                self.archive.close()
                self.output_queue.get_q().put(None)
                break

            next_file["fileobj"].begin_download()

            LOGGER.info(
                f"""
            Writing file {next_file["tar_info"].name} into the archive.
            """
            )

            tar_info = next_file["tar_info"]
            tar_info.size = next_file["fileobj"].get_dload().get_size()
            if next_file["fileobj"].get_dload().get_chksum():
                tar_info.chksum = next_file["fileobj"].get_dload().get_chksum()
            tar_info.mtime = next_file["fileobj"].get_dload().get_mtime()

            self.archive.addfile(tar_info, next_file["fileobj"])

    async def a_begin_container_download(
        self,
    ) -> None:
        """Begin the operation for downloading a whole container."""
        self.begin_container_download()

    def begin_container_download(
        self,
    ) -> None:
        """Begin the operation for downloading a whole container."""
        self.get_object_listing()

        self.archive = tarfile.open(
            name=self.container + ".tar",
            mode="w|",
            fileobj=self.output_queue,  # type:ignore
        )

        self.sync_folders(self.fs)

        self.downloader_thread = threading.Thread(target=self.download_init, daemon=True)
        self.downloader_thread.start()

        self.archiving_thread = threading.Thread(
            target=self.tar_archiving_loop, daemon=True
        )
        self.archiving_thread.start()

    async def a_write_to_response(self, response: aiohttp.web.StreamResponse) -> None:
        """Write the tarball into the response."""
        while True:
            chunk = await self.output_queue.a_read()
            if chunk is None:
                await response.write_eof()
                return
            await response.write(chunk)
