"""Module for testing ``swift_browser_ui.ui.health``."""


import unittest

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
        self.assertIn("time", self.mock_performance["swiftui-upload-runner"])
        first_time = self.mock_performance["swiftui-upload-runner"]["time"]

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
        self.assertNotEqual(
            first_time, self.mock_performance["swiftui-upload-runner"]["time"]
        )

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
        with self.setd, self.p_json_resp:
            await swift_browser_ui.ui.health.handle_health_check(self.mock_request)
        self.aiohttp_json_response_mock.assert_called()
        status = self.aiohttp_json_response_mock.call_args_list[0][0][0]["status"]
        self.assertEqual(status, "Ok")

        self.mock_client_response.status = 503
        with self.setd, self.p_json_resp:
            await swift_browser_ui.ui.health.handle_health_check(self.mock_request)
        status = self.aiohttp_json_response_mock.call_args_list[1][0][0]["status"]
        self.assertEqual(status, "Partially down")
