"""Test ``swift_browser_ui.login`` module."""

import hashlib
import os
import unittest
import json
import types

import asynctest
import aiohttp

import swift_browser_ui.login
import swift_browser_ui.settings

from .creation import get_request_with_fernet, get_request_with_mock_openstack
from .mockups import return_project_avail, return_test_swift_endpoint
from .mockups import return_invalid
from .mockups import mock_token_project_avail

_path = "/auth/OS-FEDERATION/identity_providers/haka/protocols/saml2/websso"


class LoginTestClass(asynctest.TestCase):
    """Testing the Object Browser API."""

    async def test_handle_login(self):
        """Test initial login handler."""
        mock_req = types.SimpleNamespace(**{
            "query": {"navto": "http://example"}
        })
        resp = await swift_browser_ui.login.handle_login(mock_req)

        self.assertEqual(resp.headers['Location'], "/login/front")
        self.assertEqual(resp.status, 302)

    async def test_sso_query_begin_with_trust(self):
        """Test sso query begin function."""
        with unittest.mock.patch("swift_browser_ui.login.setd", new={
                "auth_endpoint_url": "https://example.os.com:5001/v3",
                "set_origin_address": "https://localhost/login/websso",
                "has_trust": True,
        }):
            resp = await swift_browser_ui.login.sso_query_begin(None)
            self.assertEqual(resp.status, 302)
            self.assertEqual(resp.headers['Location'], (
                "https://example.os.com:5001/v3" +
                _path +
                "?origin={origin}".format(
                    origin="https://localhost/login/websso"
                )
            ))

    async def test_sso_query_begin_without_trust(self):
        """Test sso query begin without trust."""
        with unittest.mock.patch("swift_browser_ui.login.setd", new={
                "auth_endpoint_url": "https://example.os.com:5001/v3",
                "origin_address": "https://localhost/login/websso",
                "has_trust": False,
                "static_directory": (__file__.replace("/settings.py", "") +
                                     "/static"),
        }):
            resp = await swift_browser_ui.login.sso_query_begin(None)
            self.assertEqual(resp.status, 200)

    async def test_sso_query_end_successful_http_form(self):
        """
        Test sso query end function with correct execution parameters.

        This version tests the token delivery in a http encoded form.
        """
        patch1 = unittest.mock.patch("swift_browser_ui.login.setd", new={
            "auth_endpoint_url": "http://example-auth.exampleosep.com:5001/v3",
            "swift_endpoint_url": "http://obj.exampleosep.com:443/v1",
        })

        # Patch away the convenience function for checking project availability
        patch2 = unittest.mock.patch(
            "swift_browser_ui.login.get_availability_from_token",
            new=return_project_avail
        )

        patch3 = unittest.mock.patch(
            "keystoneauth1.identity.v3.Token"
        )
        patch4 = unittest.mock.patch(
            "keystoneauth1.session.Session"
        )
        patch5 = unittest.mock.patch(
            "swiftclient.service.SwiftService"
        )

        patch6 = unittest.mock.patch(
            "swift_browser_ui.login.test_swift_endpoint",
            new=return_test_swift_endpoint
        )

        with patch1, patch2, patch3, patch4, patch5, patch6:
            req = get_request_with_fernet()
            token = hashlib.md5(os.urandom(64)).hexdigest()  # nosec
            req.set_post({
                "token": token
            })

            resp = await swift_browser_ui.login.sso_query_end(req)

            # Test for the correct values
            assert req.app['Sessions']  # nosec
            session = list(req.app['Sessions'])[0]
            self.assertTrue(req.app['Sessions'][session]['Token'] is not None)
            self.assertNotEqual(req.app['Sessions'][session]['Avail'], "INVALID")
            self.assertEqual(req.app['Sessions'][session]['active_project'], {
                "name": "placeholder",
                "id": "placeholder",
            })
            self.assertEqual(resp.status, 303)
            self.assertEqual(resp.headers['Location'], "/browse")
            self.assertIn("S3BROW_SESSION", resp.cookies)

    async def test_sso_query_end_successful_url_form(self):
        """
        Test sso query end function with correct execution parameters.

        This version tests the token delivery in a urlencoded form instead of a
        http encoded one.
        """
        patch1 = unittest.mock.patch("swift_browser_ui.login.setd", new={
            "auth_endpoint_url": "http://example-auth.exampleosep.com:5001/v3",
            "swift_endpoint_url": "http://obj.exampleosep.com:443/v1",
        })

        patch2 = unittest.mock.patch(
            "swift_browser_ui.login.get_availability_from_token",
            new=return_project_avail
        )

        patch3 = unittest.mock.patch(
            "keystoneauth1.identity.v3.Token"
        )
        patch4 = unittest.mock.patch(
            "keystoneauth1.session.Session"
        )
        patch5 = unittest.mock.patch(
            "swiftclient.service.SwiftService"
        )

        patch6 = unittest.mock.patch(
            "swift_browser_ui.login.test_swift_endpoint",
            new=return_test_swift_endpoint
        )

        with patch1, patch2, patch3, patch4, patch5, patch6:
            req = get_request_with_fernet()
            token = hashlib.md5(os.urandom(64)).hexdigest()  # nosec

            req.query['token'] = token

            resp = await swift_browser_ui.login.sso_query_end(req)

            # Test for the correct values
            assert req.app['Sessions']  # nosec
            session = list(req.app['Sessions'].keys())[0]
            self.assertTrue(req.app['Sessions'][session]['Token'] is not None)
            self.assertNotEqual(req.app['Sessions'][session]['Avail'], "INVALID")
            self.assertEqual(req.app['Sessions'][session]['active_project'], {
                "name": "placeholder",
                "id": "placeholder",
            })
            self.assertEqual(resp.status, 303)
            self.assertEqual(resp.headers['Location'], "/browse")
            self.assertIn("S3BROW_SESSION", resp.cookies)

    async def test_sso_query_end_successful_header(self):
        """
        Test sso query end function with correct execution parameters.

        This version tests the token delivery in a HTTP header.
        """
        patch1 = unittest.mock.patch("swift_browser_ui.login.setd", new={
            "auth_endpoint_url": "http://example-auth.exampleosep.com:5001/v3",
            "swift_endpoint_url": "http://obj.exampleosep.com:443/v1",
        })

        # Patch away the convenience function for checking project availability
        patch2 = unittest.mock.patch(
            "swift_browser_ui.login.get_availability_from_token",
            new=return_project_avail
        )

        patch3 = unittest.mock.patch(
            "keystoneauth1.identity.v3.Token"
        )

        patch4 = unittest.mock.patch(
            "keystoneauth1.session.Session"
        )

        patch5 = unittest.mock.patch(
            "swiftclient.service.SwiftService"
        )

        patch6 = unittest.mock.patch(
            "swift_browser_ui.login.test_swift_endpoint",
            new=return_test_swift_endpoint
        )

        with patch1, patch2, patch3, patch4, patch5, patch6:
            req = get_request_with_fernet()
            token = hashlib.md5(os.urandom(64)).hexdigest()  # nosec

            req.headers['X-Auth-Token'] = token

            resp = await swift_browser_ui.login.sso_query_end(req)

            # Test for the correct values
            assert req.app['Sessions']  # nosec
            session = list(req.app['Sessions'].keys())[0]
            self.assertTrue(req.app['Sessions'][session]['Token'] is not None)
            self.assertNotEqual(req.app['Sessions'][session]['Avail'], "INVALID")
            self.assertEqual(req.app['Sessions'][session]['active_project'], {
                "name": "placeholder",
                "id": "placeholder",
            })
            self.assertEqual(resp.status, 303)
            self.assertEqual(resp.headers['Location'], "/browse")
            self.assertIn("S3BROW_SESSION", resp.cookies)

    async def test_sso_query_end_unsuccessful_missing_token(self):
        """Test unsuccessful token delivery with token missing."""
        patch1 = unittest.mock.patch("swift_browser_ui.login.setd", new={
            "auth_endpoint_url": "http://example-auth.exampleosep.com:5001/v3",
            "swift_endpoint_url": "http://obj.exampleosep.com:443/v1",
        })

        patch2 = unittest.mock.patch(
            "keystoneauth1.identity.v3.Token"
        )
        patch3 = unittest.mock.patch(
            "keystoneauth1.session.Session"
        )
        patch4 = unittest.mock.patch(
            "swiftclient.service.SwiftService"
        )

        with patch1, patch2, patch3, patch4:
            req = get_request_with_fernet()

            with self.assertRaises(aiohttp.web.HTTPClientError):
                _ = await swift_browser_ui.login.sso_query_end(req)

    async def test_sso_query_end_unsuccessful_invalid_token(self):
        """Test unsuccessful token delivery with an invalid."""
        patch1 = unittest.mock.patch("swift_browser_ui.login.setd", new={
            "auth_endpoint_url": "http://example-auth.exampleosep.com:5001/v3",
            "swift_endpoint_url": "http://obj.exampleosep.com:443/v1",
            "has_trust": False,
        })

        # Patch away the convenience function for checking project availability
        patch2 = unittest.mock.patch(
            "swift_browser_ui.login.get_availability_from_token",
            new=return_invalid
        )

        patch3 = unittest.mock.patch(
            "keystoneauth1.identity.v3.Token"
        )
        patch4 = unittest.mock.patch(
            "keystoneauth1.session.Session"
        )
        patch5 = unittest.mock.patch(
            "swiftclient.service.SwiftService"
        )

        with patch1, patch2, patch3, patch4, patch5:
            req = get_request_with_fernet()
            # token = hashlib.md5(os.urandom(64)).hexdigest()  # nosec
            token = "incorrect_token"  # nosec

            req.headers['X-Auth-Token'] = token

            with self.assertRaises(aiohttp.web.HTTPClientError):
                await swift_browser_ui.login.sso_query_end(req)

    async def test_handle_logout(self):
        """Test the logout function."""
        cookie, req = get_request_with_mock_openstack()

        sess_mock = unittest.mock.MagicMock("keystoneauth.session.Session")
        req.app['Sessions'][cookie]['OS_sess'] = sess_mock()

        sess = req.app['Sessions'][cookie]['OS_sess']

        resp = await swift_browser_ui.login.handle_logout(req)

        self.assertEqual(resp.status, 303)
        self.assertEqual(resp.headers['Location'], "/")
        sess.invalidate.assert_called_once()
        self.assertNotIn(cookie, req.app['Sessions'])

    async def test_token_rescope_not_available(self):
        """Test the token rescope function."""
        session, req = get_request_with_mock_openstack()
        req.app["Sessions"][session]["Avail"] = \
            json.loads(mock_token_project_avail)
        req.query["project"] = "non-existent-project"
        with self.assertRaises(aiohttp.web.HTTPForbidden):
            await swift_browser_ui.login.token_rescope(req)

    async def test_token_rescope_correct(self):
        """Test the token rescope function with correct request."""
        session, req = get_request_with_mock_openstack()
        req.app["Sessions"][session]["Avail"] = \
            json.loads(mock_token_project_avail)
        req.query["project"] = "wol"
        req.app["Sessions"][session]["Token"] = "not_actually_a_token"  # nosec

        # Set up mockups
        sess_mock = unittest.mock.MagicMock("keystoneauth.session.Session")
        req.app["Sessions"][session]["OS_sess"] = sess_mock()
        patch_os_auth = unittest.mock.patch(
            "swift_browser_ui.login.initiate_os_service",
            new=unittest.mock.MagicMock(
                swift_browser_ui._convenience.initiate_os_service
            )
        )
        patch_os_sess = unittest.mock.patch(
            "swift_browser_ui.login.initiate_os_session",
            new=unittest.mock.MagicMock(
                swift_browser_ui._convenience.initiate_os_session
            )
        )
        with patch_os_auth, patch_os_sess:
            resp = await swift_browser_ui.login.token_rescope(req)
            self.assertEqual(resp.status, 303)
            self.assertEqual(resp.headers["Location"], "/browse")
