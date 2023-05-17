"""Unit tests for swift_browser_ui.upload.download module."""

import tarfile

import aiohttp.web
from unittest import mock

from swift_browser_ui.upload.download import (
    FileDownloadProxy,
    TarInputWrapper,
    ContainerArchiveDownloadProxy,
)
import tests.common.mockups


class DownloadTestClass(tests.common.mockups.APITestBase):
    """Test class for swift_browser_ui.upload.download functions."""

    def setUp(self):
        """Set up mocks."""
        super().setUp()
        self.mock_session = {
            "endpoint": "https://test-endpoint-0/v1/AUTH_test-id",
            "token": "test-token1",
        }

    def mocked_requests_get(self, *args, **kwargs):
        class MockResponse:
            def __init__(self, headers, status_code):
                self.status_code = status_code
                self.headers = headers

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                pass

            def iter_content(self, chunk_size):
                cont = []
                for i in range(chunk_size):
                    cont.append(1)
                return cont

        if kwargs["headers"]["X-Auth-Token"] == "test-token1":
            return MockResponse({}, 200)
        elif kwargs["headers"]["X-Auth-Token"] == "test-token2":
            headers = {
                "Content_Type": "type",
                "ETag": "something",
                "X-Timestamp": 10,
                "Content-Length": 10,
            }
            return MockResponse(headers, 200)

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_download_into_queue(self, mock_get):
        """Test downloading object chunk into the queue."""
        proxy = FileDownloadProxy(self.mock_session)
        with self.assertRaises(aiohttp.web.HTTPUnprocessableEntity):
            proxy.download_into_queue("project", "container", "object")

        self.mock_session["token"] = "test-token2"
        another_proxy = FileDownloadProxy(self.mock_session, 10)
        another_proxy.download_into_queue("project", "container", "object")
        self.assertEqual(another_proxy.q.qsize(), 11)

    def test_file_wrapper(self):
        """Test TarInputWrapper methods."""
        wrapper = TarInputWrapper(self.mock_session, "project", "container", "object")
        self.assertEqual(type(wrapper.get_dload()), FileDownloadProxy)
        wrapper.dload.q.put(b"asdfg")
        wrapper.begin_download()
        wrapper.dload.q.put(b"asdfg")
        wrapper.last_chunk = b"12345"
        ret = wrapper.read(10)
        self.assertEqual(ret, b"12345asdfg")

    def test_parse_archive(self):
        """Test parsing a list of paths."""
        cont_proxy = ContainerArchiveDownloadProxy(
            self.mock_session, "project", "container", "object"
        )
        with self.assertRaises(ValueError):
            cont_proxy._parse_archive_fs([""])

        ret = cont_proxy._parse_archive_fs([["path"]], "-")
        self.assertEqual(len(ret["path"].keys()), 3)
        self.assertEqual(ret["path"]["name"], "-/path")
        self.assertEqual(type(ret["path"]["tar_info"]), tarfile.TarInfo)

        ret = cont_proxy._parse_archive_fs([["path", "file"], ["path", "file"]], "-")
        self.assertEqual(len(ret["path"].keys()), 4)
        self.assertEqual(ret["path"]["name"], "-/path")
        self.assertEqual(ret["path"]["type"], "folder")
        self.assertEqual(ret["path"]["contents"]["file"]["type"], "file")

    def test_download_loop(self):
        """Test loop to initialize downloads."""
        cont_proxy = ContainerArchiveDownloadProxy(
            self.mock_session, "project", "container", "object"
        )
        cont_proxy.archive = tarfile.open(
            name=cont_proxy.container + ".tar",
            mode="w|",
            fileobj=cont_proxy.output_queue,
        )
        cont_proxy.fs = {
            "path": {
                "name": "/path",
                "type": "folder",
                "tar_info": tarfile.TarInfo(name="/path"),
                "contents": {
                    "file": {
                        "name": "/file",
                        "type": "file",
                        "tar_info": tarfile.TarInfo(name="/file"),
                    }
                },
            }
        }
        cont_proxy.download_init()
        q = cont_proxy.download_queue
        self.assertEqual(q.qsize(), 2)
        self.assertEqual(type(q.get()["fileobj"]), TarInputWrapper)

    def mocked_queue_get(*args, **kwargs):
        return None

    @mock.patch("queue.Queue.get", side_effect=mocked_queue_get)
    def test_tar_archiving_loop(self, mocked_queue):
        """Test end of loop to initialize tarballing."""
        cont_proxy = ContainerArchiveDownloadProxy(
            self.mock_session, "project", "container", "object"
        )
        cont_proxy.archive = tarfile.open(
            name=cont_proxy.container + ".tar",
            mode="w|",
            fileobj=cont_proxy.output_queue,
        )
        cont_proxy.tar_archiving_loop()
        with self.assertRaises(OSError):
            # Archive was closed
            cont_proxy.archive.getnames()
