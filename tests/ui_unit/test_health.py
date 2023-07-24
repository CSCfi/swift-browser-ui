"""Module for testing ``swift_browser_ui.ui.health``."""

import redis
import unittest
import unittest.mock

import tests.common.mockups
import swift_browser_ui.ui.health


class HealthTestClass(tests.common.mockups.APITestBase):
    """Test the Object Browser API."""

    def setUp(self):
        """Set up mocks."""
        super().setUp()
        self.mock_services = {}
        self.mock_api_params = {}
        self.mock_performance = {}

        self.mock_setd = {
            "upload_internal_endpoint": "http://test-endpoint",
            "sharing_internal_endpoint": "http://test-endpoint",
            "request_internal_endpoint": "http://test-endpoint",
        }
        self.setd = unittest.mock.patch("swift_browser_ui.ui.health.setd", self.mock_setd)

        self.mock_redis = unittest.mock.AsyncMock()
        self.mock_redis.ping.return_value = True
        self.mock_redis_client = unittest.mock.AsyncMock(return_value=self.mock_redis)

    async def test_get_x_account_sharing(self):
        """Test getting x account sharing."""
        with self.setd:
            await swift_browser_ui.ui.health.get_x_account_sharing(
                self.mock_services,
                self.mock_request,
                self.mock_client,
                self.mock_api_params,
                self.mock_performance,
            )
        self.mock_client.get.assert_called_once()
        self.assertEqual(self.mock_services["swift-x-account-sharing"], {"status": "Ok"})
        self.assertIn("time", self.mock_performance["swift-x-account-sharing"])
        first_time = self.mock_performance["swift-x-account-sharing"]["time"]

        self.mock_client_response.status = 503
        with self.setd:
            await swift_browser_ui.ui.health.get_x_account_sharing(
                self.mock_services,
                self.mock_request,
                self.mock_client,
                self.mock_api_params,
                self.mock_performance,
            )
        self.assertEqual(
            self.mock_services["swift-x-account-sharing"], {"status": "Down"}
        )
        self.assertNotEqual(
            first_time, self.mock_performance["swift-x-account-sharing"]["time"]
        )

    async def test_get_swift_sharing(self):
        """Test getting swift sharing."""
        with self.setd:
            await swift_browser_ui.ui.health.get_swift_sharing(
                self.mock_services,
                self.mock_request,
                self.mock_client,
                self.mock_api_params,
                self.mock_performance,
            )
        self.mock_client.get.assert_called_once()
        self.assertEqual(self.mock_services["swift-sharing-request"], {"status": "Ok"})
        self.assertIn("time", self.mock_performance["swift-sharing-request"])
        first_time = self.mock_performance["swift-sharing-request"]["time"]

        self.mock_client_response.status = 503
        with self.setd:
            await swift_browser_ui.ui.health.get_swift_sharing(
                self.mock_services,
                self.mock_request,
                self.mock_client,
                self.mock_api_params,
                self.mock_performance,
            )
        self.assertEqual(self.mock_services["swift-sharing-request"], {"status": "Down"})
        self.assertNotEqual(
            first_time, self.mock_performance["swift-sharing-request"]["time"]
        )

    async def test_get_upload_runner(self):
        """Test getting upload runner."""
        self.mock_client_json["upload-runner"] = {"status": "Ok"}
        self.mock_client_json["vault-instance"] = {"status": "Ok"}
        self.mock_client_json["start-time"] = 0.1
        self.mock_client_json["end-time"] = 0.2
        with self.setd:
            await swift_browser_ui.ui.health.get_upload_runner(
                self.mock_services,
                self.mock_request,
                self.mock_client,
                self.mock_api_params,
                self.mock_performance,
            )

        self.mock_client.get.assert_called_once()
        self.assertEqual(self.mock_services["swiftui-upload-runner"], {"status": "Ok"})
        self.assertEqual(self.mock_services["vault"], {"status": "Ok"})
        self.assertIn("time", self.mock_performance["swiftui-upload-runner"])
        first_time_upload = self.mock_performance["swiftui-upload-runner"]["time"]
        first_time_vault = self.mock_performance["vault"]["time"]

        self.mock_client_response.status = 503
        with self.setd:
            await swift_browser_ui.ui.health.get_upload_runner(
                self.mock_services,
                self.mock_request,
                self.mock_client,
                self.mock_api_params,
                self.mock_performance,
            )
        self.assertEqual(self.mock_services["swiftui-upload-runner"], {"status": "Down"})
        self.assertEqual(self.mock_services["vault"], {"status": "Down"})
        self.assertNotEqual(
            first_time_upload, self.mock_performance["swiftui-upload-runner"]["time"]
        )
        self.assertNotEqual(first_time_vault, self.mock_performance["vault"]["time"])

    async def test_get_redis(self):
        """Test getting redis service."""
        with self.setd:
            with unittest.mock.patch(
                "swift_browser_ui.ui.health.get_redis_client", self.mock_redis_client
            ):
                await swift_browser_ui.ui.health.get_redis(
                    self.mock_services,
                    self.mock_request,
                    self.mock_performance,
                )
        self.assertEqual(self.mock_services["redis"], {"status": "Ok"})
        self.assertIn("time", self.mock_performance["redis"])
        first_time = self.mock_performance["redis"]["time"]

        self.mock_redis.ping.side_effect = redis.ConnectionError
        self.mock_redis_client = unittest.mock.AsyncMock(return_value=self.mock_redis)
        with self.setd:
            with unittest.mock.patch(
                "swift_browser_ui.ui.health.get_redis_client", self.mock_redis_client
            ):
                await swift_browser_ui.ui.health.get_redis(
                    self.mock_services,
                    self.mock_request,
                    self.mock_performance,
                )
        self.assertEqual(self.mock_services["redis"], {"status": "Down"})
        self.assertNotEqual(first_time, self.mock_performance["redis"]["time"])

    async def test_some_exception(self):
        """Test that an exception happens when getting one of the service statuses."""
        self.mock_client_response.json = None
        with self.setd:
            await swift_browser_ui.ui.health.get_upload_runner(
                self.mock_services,
                self.mock_request,
                self.mock_client,
                self.mock_api_params,
                self.mock_performance,
            )
        self.assertEqual(self.mock_services["swiftui-upload-runner"], {"status": "Error"})

    async def test_nonexistant_service(self):
        """Test get_upload_runner when upload_internal_endpoint is not assigned."""
        self.mock_setd["upload_internal_endpoint"] = None
        with self.setd:
            await swift_browser_ui.ui.health.get_upload_runner(
                self.mock_services,
                self.mock_request,
                self.mock_client,
                self.mock_api_params,
                self.mock_performance,
            )
        self.assertEqual(
            self.mock_services["swiftui-upload-runner"], {"status": "Nonexistent"}
        )

    async def test_handle_health_check(self):
        """Test handling health check."""
        self.mock_client_response.json.return_value = {
            "status": "Ok",
            "upload-runner": {"status": "Ok"},
            "vault-instance": {"status": "Ok"},
            "start-time": 0.1,
            "end-time": 0.2,
        }
        redis_mock = unittest.mock.patch(
            "swift_browser_ui.ui.health.get_redis_client", new=self.mock_redis_client
        )
        with self.setd, self.p_json_resp, redis_mock:
            await swift_browser_ui.ui.health.handle_health_check(self.mock_request)
        self.aiohttp_json_response_mock.assert_called()
        status = self.aiohttp_json_response_mock.call_args_list[0][0][0]["status"]
        self.assertEqual(status, "Ok")

        self.mock_client_response.status = 503
        with self.setd, self.p_json_resp:
            await swift_browser_ui.ui.health.handle_health_check(self.mock_request)
        status = self.aiohttp_json_response_mock.call_args_list[1][0][0]["status"]
        self.assertEqual(status, "Partially down")
