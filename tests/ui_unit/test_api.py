"""Module for testing ``swift_browser_ui.ui.api``."""


import json
import unittest
import types

import aiohttp.web

import tests.common.mockups
import swift_browser_ui.ui.api


class APITestClass(tests.common.mockups.APITestBase):
    """Test the Object Browser API."""

    def setUp(self):
        """Set up mocks."""
        super().setUp()

    async def test_get_os_user(self):
        """Test session Openstack username fetch."""
        with self.p_get_sess, self.p_json_resp:
            await swift_browser_ui.ui.api.get_os_user(self.mock_request)
        self.aiohttp_json_response_mock.assert_called_once_with("testuser")

    async def test_os_list_projects(self):
        """Test Openstack available project scope fetch."""
        with self.p_get_sess, self.p_json_resp:
            await swift_browser_ui.ui.api.os_list_projects(
                self.mock_request,
            )
        self.aiohttp_json_response_mock.assert_called_once_with(
            [
                {
                    "id": "test-id-0",
                    "name": "test-name-0",
                    "tainted": False,
                },
                {
                    "id": "test-id-1",
                    "name": "test-name-1",
                    "tainted": False,
                },
            ]
        )

    async def test_swift_list_containers(self):
        """Test container listing fetch from Openstack."""
        with self.p_get_sess, self.p_sresp:
            await swift_browser_ui.ui.api.swift_list_containers(
                self.mock_request,
            )
            self.mock_response_prepare.assert_awaited_once()
            self.mock_iter.assert_called()
            self.mock_response_write.assert_awaited()
            self.mock_response_write_eof.assert_awaited_once()

    async def test_swift_list_containers_fail_ostack(self):
        """Test failed container listing fetch from Openstack."""
        # Set client response to incorrect
        self.mock_client_response.status = 401
        with self.p_get_sess, self.p_sresp:
            await swift_browser_ui.ui.api.swift_list_containers(
                self.mock_request,
            )
            self.aiohttp_construct_response_mock.assert_called_once_with(status=401)
            self.mock_response_write.assert_not_called()
            self.mock_response_prepare.assert_awaited_once()
            self.mock_response_write_eof.assert_awaited_once()

    async def test_swift_list_containers_no_access(self):
        """Test failed container listing access rights."""
        # Set request project to incorrect
        self.mock_request.match_info["project"] = "test-id-not-available"
        with self.p_get_sess, self.assertRaises(aiohttp.web.HTTPForbidden):
            await swift_browser_ui.ui.api.swift_list_containers(
                self.mock_request,
            )

    async def test_swift_list_objects(self):
        """Test object listing fetch from Openstack."""
        with self.p_get_sess, self.p_sresp:
            await swift_browser_ui.ui.api.swift_list_objects(
                self.mock_request,
            )
            self.aiohttp_construct_response_mock.assert_called_once_with(status=200)
            self.mock_response_prepare.assert_awaited_once()
            self.mock_iter.assert_called()
            self.mock_response_write.assert_awaited()
            self.mock_response_write_eof.assert_awaited_once()

    async def test_swift_create_container(self):
        """Test container creation with Openstack."""
        # Set json for tags
        self.mock_request.json = unittest.mock.AsyncMock(
            return_value={
                "tags": "a,b,c,d,e",
            }
        )
        with self.p_get_sess, self.p_resp:
            await swift_browser_ui.ui.api.swift_create_container(
                self.mock_request,
            )
        self.aiohttp_construct_response_mock.assert_called_once_with(
            status=200,
        )
        self.mock_client.put.assert_called_once()
        self.mock_request.json.assert_awaited_once()

    async def test_swift_delete_container(self):
        """Test container deletion with Openstack."""
        with self.p_get_sess:
            resp = await swift_browser_ui.ui.api.swift_delete_container(
                self.mock_request,
            )
            self.assertEqual(resp.status, 200)

    async def test_swift_delete_containers_to_objects(self):
        """Test container deletion with objects in query."""
        self.mock_request.query["objects"] = "placeholder"
        mock_obj_delete = unittest.mock.AsyncMock()
        patch_obj_delete = unittest.mock.patch(
            "swift_browser_ui.ui.api.swift_delete_objects",
            mock_obj_delete,
        )
        with patch_obj_delete:
            await swift_browser_ui.ui.api.swift_delete_container(
                self.mock_request,
            )
        mock_obj_delete.assert_called_once()
        mock_obj_delete.assert_awaited_once()

    async def test_swift_delete_objects(self):
        """Test object batch deletion."""
        # set json for objects
        self.mock_request.json = unittest.mock.AsyncMock(
            return_value=[
                "test-object-0",
                "test-object-1",
                "test-object-2",
            ],
        )
        with self.p_get_sess:
            resp = await swift_browser_ui.ui.api.swift_delete_objects(
                self.mock_request,
            )
            self.mock_client.post.assert_called_once()
            self.mock_response_read.assert_awaited_once()
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.body, b"exampleread")

    async def test_swift_delete_objects_toomany(self):
        """Test object batch deletion with too many objects."""
        self.mock_request.json = unittest.mock.AsyncMock(
            return_value=[f"test-object-{i}" for i in range(0, 10001)]
        )
        with self.p_get_sess, self.assertRaises(aiohttp.web.HTTPBadRequest):
            await swift_browser_ui.ui.api.swift_delete_objects(
                self.mock_request,
            )

    async def test_swift_download_object(self):
        """Test object download with Openstack TempUrl engine."""
        get_tempurl_key_mock = unittest.mock.AsyncMock(return_value="test-key")
        patch_tempkey = unittest.mock.patch(
            "swift_browser_ui.ui.api.get_tempurl_key",
            get_tempurl_key_mock,
        )
        generate_tempurl_mock = unittest.mock.Mock(return_value="?tempurl=true")
        patch_tempurl = unittest.mock.patch(
            "swift_browser_ui.ui.api.generate_temp_url",
            generate_tempurl_mock,
        )

        self.mock_client_response.headers["Content-Type"] = "test-content"

        with self.p_get_sess, patch_tempkey, patch_tempurl:
            resp = await swift_browser_ui.ui.api.swift_download_object(
                self.mock_request,
            )
        self.assertEqual(resp.status, 302)
        self.assertEqual(resp.headers["Location"], "https://test-endpoint-0?tempurl=true")
        self.assertEqual(resp.headers["Content-Type"], "test-content")
        self.mock_client.head.assert_called_once()
        get_tempurl_key_mock.assert_awaited_once()
        generate_tempurl_mock.assert_called_once()

    async def test_swift_get_met_wrapper(self):
        """Test single object metadata fetch with Openstack."""
        self.mock_client_response.headers = {
            "X-Object-Meta-One": "examplemeta",
            "X-Object-Meta-Two": "examplemeta",
            "X-Object-Meta-Three": "examplemeta",
            "X-Object-Meta-Four": "examplemeta",
            "X-Object-Meta-s3cmd-attrs": "first:1/second:2/third:3",
        }
        with self.p_get_sess:
            ret = await swift_browser_ui.ui.api._swift_get_object_metadata_wrapper(
                self.mock_request,
                "test-object",
            )
        self.assertIn("Three", ret[1])
        self.mock_client.head.assert_called_once()
        self.assertIn("s3cmd-attrs", ret[1])
        self.assertIn("second", ret[1]["s3cmd-attrs"])

    async def test_swift_get_meta_fail(self):
        """Test single object metadata fetch failure with Openstack."""
        self.mock_client_response.status = 404
        with self.p_get_sess, self.assertRaises(aiohttp.web.HTTPInternalServerError):
            await swift_browser_ui.ui.api._swift_get_object_metadata_wrapper(
                self.mock_request,
                "test-object",
            )

    async def test_swift_batch_get_object_meta(self):
        """Test batch object metadata fetch with Openstack."""
        mock_get_meta = unittest.mock.AsyncMock(return_value=("object", "meta"))
        patch_get_meta = unittest.mock.patch(
            "swift_browser_ui.ui.api._swift_get_object_metadata_wrapper",
            mock_get_meta,
        )
        self.mock_request.query = {"objects": "obja,objb,objc,objd,obje,objf"}
        with self.p_get_sess, patch_get_meta:
            await swift_browser_ui.ui.api.swift_get_batch_object_metadata(
                self.mock_request,
            )
        mock_get_meta.assert_called()
        mock_get_meta.assert_awaited()

    async def test_swift_get_container_meta(self):
        """Test container metadata fetch with Openstack."""
        self.mock_client_response.headers = {
            "X-Container-Meta-One": "examplemeta",
            "X-Container-Meta-Two": "examplemeta",
            "X-Container-Meta-Three": "examplemeta",
            "X-Container-Meta-Four": "examplemeta",
            "X-Container-Meta-Five": "examplemeta",
        }
        with self.p_get_sess:
            await swift_browser_ui.ui.api.swift_get_metadata_container(
                self.mock_request,
            )
            self.mock_client.head.assert_called_once()

    async def test_swift_batch_get_object_meta_through_container(self):
        """Test object batch meta fetch via container meta handler."""
        mock_object_meta_batch = unittest.mock.AsyncMock()
        patch_object_meta = unittest.mock.patch(
            "swift_browser_ui.ui.api.swift_get_batch_object_metadata",
            mock_object_meta_batch,
        )
        self.mock_request.query["objects"] = "true"
        with patch_object_meta:
            await swift_browser_ui.ui.api.swift_get_metadata_container(
                self.mock_request,
            )
        mock_object_meta_batch.assert_awaited_once()

    async def test_swift_update_object_meta_wrapper(self):
        """Test single object metadata update with Openstack."""
        with self.p_get_sess:
            ret = await swift_browser_ui.ui.api._swift_update_object_meta_wrapper(
                self.mock_request,
                "test-object",
                [("a", 1), ("b", 2), ("c", 3)],
            )
        self.mock_client.post.assert_called_once()
        self.assertEqual(ret, 200)

    async def test_batch_swift_update_object_metadata(self):
        """Test object metadata batch update with Openstack."""
        mock_object_meta_update = unittest.mock.AsyncMock(
            return_value=204,
        )
        patch_meta_update = unittest.mock.patch(
            "swift_browser_ui.ui.api._swift_update_object_meta_wrapper",
            mock_object_meta_update,
        )

        self.mock_request.json = unittest.mock.AsyncMock(
            return_value=[
                (
                    "test-object-0",
                    {
                        "test-meta-0": "test",
                        "test-meta-1": "another_test",
                    },
                ),
                (
                    "test-object-1",
                    {
                        "test-meta-0": "test",
                        "test-meta-1": "another_test",
                    },
                ),
                (
                    "test-object-2",
                    {
                        "test-meta-0": "test",
                        "test-meta-1": "another_test",
                    },
                ),
                (
                    "test-object-3",
                    {
                        "test-meta-0": "test",
                        "test-meta-1": "another_test",
                    },
                ),
                (
                    "test-object-4",
                    {
                        "test-meta-0": "test",
                        "test-meta-1": "another_test",
                    },
                ),
            ]
        )

        with self.p_get_sess, patch_meta_update:
            resp = await swift_browser_ui.ui.api.swift_batch_update_object_metadata(
                self.mock_request,
            )
        self.assertEqual(resp.status, 204)
        mock_object_meta_update.assert_awaited()

        # Cover failure
        mock_object_meta_update.return_value = 404
        with self.p_get_sess, patch_meta_update, self.assertRaises(
            aiohttp.web.HTTPNotFound
        ):
            await swift_browser_ui.ui.api.swift_batch_update_object_metadata(
                self.mock_request,
            )

    async def test_batch_swift_update_object_metadata_no_objects(self):
        """Test object metadata batch update with missing body."""
        self.mock_request.json = unittest.mock.AsyncMock(return_value=[])
        with self.p_get_sess, self.assertRaises(aiohttp.web.HTTPBadRequest):
            await swift_browser_ui.ui.api.swift_batch_update_object_metadata(
                self.mock_request,
            )

    async def test_swift_update_container_metadata(self):
        """Test container metadata update with Openstack."""
        self.mock_request.json = unittest.mock.AsyncMock(
            return_value=[
                ("meta0", "test-data"),
                ("meta1", "more-test-data"),
            ],
        )
        with self.p_get_sess:
            resp = await swift_browser_ui.ui.api.swift_update_container_metadata(
                self.mock_request,
            )
        self.assertEqual(resp.status, 200)
        self.mock_request.json.assert_awaited_once()
        self.mock_client.post.assert_called_once()

    async def test_swift_update_object_metadata_via_container(self):
        """Test object batch meta update via container meta update."""
        mock_object_batch_meta_update = unittest.mock.AsyncMock()
        p_obj_update = unittest.mock.patch(
            "swift_browser_ui.ui.api.swift_batch_update_object_metadata",
            mock_object_batch_meta_update,
        )
        self.mock_request.query["objects"] = "true"
        with p_obj_update:
            await swift_browser_ui.ui.api.swift_update_container_metadata(
                self.mock_request,
            )
        mock_object_batch_meta_update.assert_awaited_once()

    async def test_swift_get_project_metadata(self):
        """Test project metadata fetch with Openstack."""
        self.mock_client_response.status = 204
        self.mock_client_response.headers = {
            "X-Account-Container-Count": 100,
            "X-Account-Object-Count": 10000,
            "X-Account-Bytes-Used": 65535,
        }
        with self.p_get_sess:
            await swift_browser_ui.ui.api.swift_get_project_metadata(
                self.mock_request,
            )
        self.mock_client.head.assert_called_once()

    async def test_swift_get_project_metadata_fail(self):
        """Test project metadata fetch with failed request."""
        self.mock_client_response.status = 403
        with self.p_get_sess, self.assertRaises(aiohttp.web.HTTPUnauthorized):
            await swift_browser_ui.ui.api.swift_get_project_metadata(
                self.mock_request,
            )

    async def test_swift_get_shared_container_address(self):
        """Test shared container address fetch."""
        with self.p_get_sess:
            resp = await swift_browser_ui.ui.api.get_shared_container_address(
                self.mock_request,
            )
        self.assertEqual(resp.body, b'"https://test-endpoint-0/v1/AUTH_test-id-0"')

    async def test_swift_get_container_acl_wrapper(self):
        """Test single container ACL fetch with Openstack."""
        self.mock_client_response.headers = {
            "X-Container-Read": "test-project-0:*,.r:*,.rlistings,test-project-1:*",
            "X-Container-Write": "test-project-0:*,test-project-1:*",
        }
        with self.p_get_sess:
            ret = await swift_browser_ui.ui.api._swift_get_container_acl_wrapper(
                self.mock_request,
                "test-container",
            )
        self.assertEqual(
            {
                "test-project-0": {
                    "write": "*",
                    "read": "*",
                },
                "test-project-1": {
                    "write": "*",
                    "read": "*",
                },
            },
            ret[1],
        )
        self.mock_client.head.assert_called_once()

        # Cover edge case with headers containing only .rlistings/.r:*
        self.mock_client_response.headers = {
            "X-Container-Read": ".r:*,.rlistings",
            "X-Container-Write": "test-project-0:*,test-project-1:*",
        }
        with self.p_get_sess:
            ret = await swift_browser_ui.ui.api._swift_get_container_acl_wrapper(
                self.mock_request,
                "test-container",
            )
        self.assertEqual(
            {
                "test-project-0": {"write": "*"},
                "test-project-1": {"write": "*"},
            },
            ret[1],
        )

    async def test_get_access_control_metadata(self):
        """Test get ACL metadata with Openstack."""
        acl_wrapper_mock = unittest.mock.AsyncMock(
            return_value=(
                "test-container",
                {
                    "test-project-0": {
                        "write": "*",
                    },
                    "test-project-1": {
                        "write": "*",
                        "read": "*",
                    },
                },
            ),
        )
        p_acl_wrapper = unittest.mock.patch(
            "swift_browser_ui.ui.api._swift_get_container_acl_wrapper",
            acl_wrapper_mock,
        )
        # (ab)use side effects to mimic openstacks "null" terminated container paging
        self.mock_client_response.json = unittest.mock.AsyncMock(
            side_effect=[
                [{"name": "test-container"}],
                [],
            ]
        )
        with self.p_get_sess, p_acl_wrapper:
            resp = await swift_browser_ui.ui.api.get_access_control_metadata(
                self.mock_request,
            )
        acl_wrapper_mock.assert_awaited()
        ret = json.loads(resp.body)
        self.assertEqual("https://test-endpoint-0/v1/AUTH_test-id-0", ret["address"])
        self.assertEqual(
            ret["access"],
            {
                "test-container": {
                    "test-project-0": {
                        "write": "*",
                    },
                    "test-project-1": {
                        "write": "*",
                        "read": "*",
                    },
                }
            },
        )
        # Cover edge case when ending in a 204
        self.mock_client_response.json = unittest.mock.AsyncMock(
            return_value=[{"name": "test-container"}]
        )
        self.mock_client.get = unittest.mock.Mock(
            side_effect=[
                self.MockHandler(self.mock_client_response),
                self.MockHandler(
                    types.SimpleNamespace(
                        **{
                            "status": 204,
                        }
                    )
                ),
            ]
        )
        with self.p_get_sess, p_acl_wrapper:
            resp = await swift_browser_ui.ui.api.get_access_control_metadata(
                self.mock_request,
            )
        acl_wrapper_mock.assert_awaited()
        ret = json.loads(resp.body)
        self.assertEqual("https://test-endpoint-0/v1/AUTH_test-id-0", ret["address"])
        self.assertEqual(
            ret["access"],
            {
                "test-container": {
                    "test-project-0": {
                        "write": "*",
                    },
                    "test-project-1": {
                        "write": "*",
                        "read": "*",
                    },
                }
            },
        )

    async def test_remove_project_container_acl(self):
        """Test project removal from container acl with Openstack."""
        self.mock_client_response.headers = {
            "X-Container-Read": "test-project-0:*,.r:*,.rlistings,test-project-1:*",
            "X-Container-Write": "test-project-0:*,test-project-1:*",
        }
        with self.p_get_sess, self.assertRaises(aiohttp.web.HTTPNotFound):
            await swift_browser_ui.ui.api.remove_project_container_acl(
                self.mock_request,
            )
        self.mock_client_response.status = 204
        with self.p_get_sess:
            await swift_browser_ui.ui.api.remove_project_container_acl(
                self.mock_request,
            )
        self.mock_client.post.assert_called_with(
            "https://test-endpoint-0/v1/AUTH_test-id-0/test-container",
            headers={
                "X-Auth-Token": "test-token-0",
                "X-Container-Read": "test-project-0:*,.r:*,.rlistings",
                "X-Container-Write": "test-project-0:*",
            },
        )

    async def test_remove_container_acl(self):
        """Test container acl removal with Openstack."""
        with self.p_get_sess, self.assertRaises(aiohttp.web.HTTPNotFound):
            await swift_browser_ui.ui.api.remove_container_acl(
                self.mock_request,
            )
        self.mock_client_response.status = 204
        with self.p_get_sess:
            await swift_browser_ui.ui.api.remove_container_acl(
                self.mock_request,
            )
        self.mock_client.post.assert_called_with(
            "https://test-endpoint-0/v1/AUTH_test-id-0/test-container",
            headers={
                "X-Auth-Token": "test-token-0",
                "X-Container-Read": "",
                "X-Container-Write": "",
            },
        )

    async def test_add_project_container_acl(self):
        """Test project addition to container acl with Openstack."""
        self.mock_client_response.headers = {
            "X-Container-Read": "test-project-0:*,.r:*,.rlistings",
            "X-Container-Write": "test-project-0:*",
        }
        self.mock_request.query["projects"] = "test-project-1"
        self.mock_request.query["rights"] = "rw"
        with self.p_get_sess, self.assertRaises(aiohttp.web.HTTPNotFound):
            await swift_browser_ui.ui.api.add_project_container_acl(
                self.mock_request,
            )
        self.mock_client_response.status = 204
        with self.p_get_sess:
            await swift_browser_ui.ui.api.add_project_container_acl(
                self.mock_request,
            )
        self.mock_client.post.assert_called_with(
            "https://test-endpoint-0/v1/AUTH_test-id-0/test-container",
            headers={
                "X-Auth-Token": "test-token-0",
                "X-Container-Read": "test-project-0:*,.r:*,.rlistings,test-project-1:*",
                "X-Container-Write": "test-project-0:*,test-project-1:*",
            },
        )


class ProxyFunctionsTestClass(tests.common.mockups.APITestBase):
    """Test the handlers proxying information to the upload runner."""

    def setUp(self):
        """."""
        super().setUp()
        self.mock_request.match_info = {
            "project": "test-project",
            "container": "test-container",
            "object": "test-object",
        }
        self.mock_request.query = {
            "from_container": "test-container-2",
            "from_project": "test-project-2",
        }
        self.mock_request.query_string = ("&test-query=test-value§",)
        self.mock_request.remote = ("remote",)

        self.session_open_mock = unittest.mock.AsyncMock(return_value="test_runner_id")
        self.patch_runner_session = unittest.mock.patch(
            "swift_browser_ui.ui.api.open_upload_runner_session", self.session_open_mock
        )

        self.sign_mock = unittest.mock.AsyncMock(
            return_value={
                "signature": "test-signature",
                "valid": "test-valid",
            }
        )
        self.patch_sign = unittest.mock.patch(
            "swift_browser_ui.ui.api.sign", self.sign_mock
        )

    async def test_swift_download_share_object(self):
        """Test share object download handler."""
        with self.p_get_sess, self.patch_runner_session, self.patch_setd, self.patch_sign:
            resp = await swift_browser_ui.ui.api.swift_download_shared_object(
                self.mock_request,
            )
        self.assertIn("test-signature", resp.headers["Location"])
        self.assertIn("test-valid", resp.headers["Location"])
        self.assertIn("test-endpoint", resp.headers["Location"])
        self.assertEqual(303, resp.status)

    async def test_swift_download_container(self):
        """Test container download handler."""
        with self.p_get_sess, self.patch_runner_session, self.patch_setd, self.patch_sign:
            resp = await swift_browser_ui.ui.api.swift_download_container(
                self.mock_request,
            )
        self.assertIn("test-signature", resp.headers["Location"])
        self.assertIn("test-valid", resp.headers["Location"])
        self.assertIn("test-endpoint", resp.headers["Location"])
        self.assertEqual(303, resp.status)

    async def test_swift_replicate_container(self):
        """Test replicate container handler."""
        with self.p_get_sess, self.patch_runner_session, self.patch_setd, self.patch_sign:
            resp = await swift_browser_ui.ui.api.swift_replicate_container(
                self.mock_request,
            )
        self.assertIn("test-signature", resp.headers["Location"])
        self.assertIn("test-valid", resp.headers["Location"])
        self.assertIn("test-endpoint", resp.headers["Location"])
        self.assertEqual(307, resp.status)
        self.assertIn("from_container", resp.headers["Location"])
        self.assertIn("test-container-2", resp.headers["Location"])
        self.assertIn("from_project", resp.headers["Location"])
        self.assertIn("test-project-2", resp.headers["Location"])

    async def test_get_upload_session(self):
        """Test get active upload session."""
        with self.p_get_sess, self.patch_runner_session, self.patch_setd, self.patch_sign:
            await swift_browser_ui.ui.api.get_upload_session(
                self.mock_request,
            )
        self.session_open_mock.assert_awaited_once()
        self.sign_mock.assert_awaited_once()
