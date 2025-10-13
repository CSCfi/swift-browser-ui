"""Module for testing ``swift_browser_ui.ui._convenience``."""

import os
import unittest

import aiohttp.web

import swift_browser_ui.ui._convenience

import tests.common.mockups
from tests.common.mockups import mock_token_output


class TestConvenienceFunctions(
    tests.common.mockups.APITestBase,
):
    """Test convenience functions."""

    def setUp(self):
        """Test that the logging setup function works."""
        super().setUp()

    async def test_sign(self):
        """Test the signature generation."""
        mock_setd = {}
        p_setd = unittest.mock.patch(
            "swift_browser_ui.ui._convenience.setd",
            mock_setd,
        )
        mock_sign_api = unittest.mock.Mock()
        p_sign = unittest.mock.patch(
            "swift_browser_ui.ui._convenience.swift_browser_ui.common.signature.sign_api_request",
            mock_sign_api,
        )
        with self.assertRaises(aiohttp.web.HTTPNotImplemented), p_setd:
            await swift_browser_ui.ui._convenience.sign(
                3600,
                "/testpath",
            )
        mock_setd["sharing_request_token"] = "test-token"
        with p_setd, p_sign:
            await swift_browser_ui.ui._convenience.sign(
                3600,
                "/testpath",
            )
        mock_sign_api.assert_called_with(
            "/testpath",
            valid_for=3600,
            key=b"test-token",
        )

    def test_disable_cache(self):
        """Test that the disable_cache function correctly disables cache."""
        response = aiohttp.web.Response(status=200, body=b"OK")
        response = swift_browser_ui.ui._convenience.disable_cache(response)
        self.assertEqual(
            response.headers["Cache-Control"], ("no-cache, no-store, must-revalidate")
        )
        self.assertEqual(response.headers["Pragma"], "no-Cache")
        self.assertEqual(response.headers["Expires"], "0")

    async def test_get_availability_from_token(self):
        """Test token availability fetch from Openstack."""
        p_setd = unittest.mock.patch(
            "swift_browser_ui.ui._convenience.setd",
            {"auth_endpoint_url": "http://example.osexampleserver.com:5001/v3"},
        )
        self.mock_client_response.json = unittest.mock.AsyncMock(
            side_effect=[
                tests.common.mockups.mock_token_project_avail,
                tests.common.mockups.mock_token_domain_avail,
            ],
        )
        with p_setd:
            ret = await swift_browser_ui.ui._convenience.get_availability_from_token(
                "test-token",
                self.mock_client,
            )
        self.assertEqual(ret["projects"], mock_token_output["projects"])
        self.assertEqual(ret["domains"], mock_token_output["domains"])

    async def test_get_tempurl_key(self):
        """Test tempurl key fetch from Openstack."""
        with self.p_get_sess, self.assertRaises(aiohttp.web.HTTPServerError):
            ret = await swift_browser_ui.ui._convenience.get_tempurl_key(
                self.mock_request,
            )
        self.mock_client_response.status = 204
        with self.p_get_sess:
            ret = await swift_browser_ui.ui._convenience.get_tempurl_key(
                self.mock_request,
            )
        self.assertIsNotNone(ret)

        self.mock_client_response.headers = {"X-Account-Meta-Temp-Url-Key": "test-key"}
        with self.p_get_sess:
            ret = await swift_browser_ui.ui._convenience.get_tempurl_key(
                self.mock_request,
            )
        self.assertEqual(ret, "test-key")

        self.mock_client_response.headers = {"X-Account-Meta-Temp-Url-Key-2": "test-key"}
        with self.p_get_sess:
            ret = await swift_browser_ui.ui._convenience.get_tempurl_key(
                self.mock_request,
            )
        self.assertEqual(ret, "test-key")

    async def test_ldap_get_project_titles(self):
        os.environ["LDAP_SERVER_HOST"] = "host"
        os.environ["LDAP_SERVER_PORT"] = "636"
        os.environ["LDAP_SERVER_BIND"] = "bind"
        os.environ["LDAP_SERVER_PASSWORD"] = "password"
        os.environ["LDAP_SERVER_DISTINGUISHED_NAME"] = "dn"

        p_server = unittest.mock.patch(
            "swift_browser_ui.ui._convenience.Server",
            return_value=self.mock_ldap_server,
        )
        p_connection = unittest.mock.patch(
            "swift_browser_ui.ui._convenience.Connection",
            return_value=self.mock_ldap_connection,
        )
        projects = {
            "123abc": {"name": "project_123"},
            "987zyx": {"name": "project_456"},
        }
        with p_server, p_connection:
            ret = await swift_browser_ui.ui._convenience.ldap_get_project_titles(
                projects,
            )

        self.assertEqual(
            ret,
            {
                "123": "First Project",
                "456": "Second Project",
            },
        )
