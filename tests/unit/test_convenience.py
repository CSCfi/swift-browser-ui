"""Module for testing ``swift_browser_ui._convenience``."""


import hashlib
import os
import unittest
import time

from aiohttp.web import HTTPUnauthorized, Response
from aiohttp.web import HTTPForbidden

import cryptography.fernet
from swiftclient.service import SwiftService
from keystoneauth1.session import Session
from swift_browser_ui._convenience import api_check, generate_cookie
from swift_browser_ui._convenience import disable_cache, decrypt_cookie
from swift_browser_ui._convenience import session_check, setup_logging
from swift_browser_ui._convenience import get_availability_from_token
from swift_browser_ui._convenience import initiate_os_service
from swift_browser_ui._convenience import initiate_os_session
from swift_browser_ui._convenience import check_csrf, clear_session_info
from swift_browser_ui.settings import setd

from .creation import get_request_with_fernet, get_request_with_mock_openstack
from .creation import get_full_crypted_session_cookie
from .creation import add_csrf_to_cookie, encrypt_cookie
from .mockups import mock_token_output, urlopen


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions."""

    def setUp(self):
        """Test that the logging setup function works."""
        setup_logging()
        setd['verbose'] = True
        setup_logging()
        setd['debug'] = True
        setup_logging()

    def test_disable_cache(self):
        """Test that the disable_cache function correctly disables cache."""
        response = Response(
            status=200,
            body=b'OK'
        )
        response = disable_cache(response)
        self.assertEqual(response.headers['Cache-Control'], (
            "no-cache, no-store, must-revalidate"
        ))
        self.assertEqual(response.headers['Pragma'], 'no-Cache')
        self.assertEqual(response.headers['Expires'], '0')

    def test_generate_cookie(self):
        """Test that the cookie generation works."""
        testreq = get_request_with_fernet()
        self.assertTrue(generate_cookie(testreq) is not None)

    def test_decrypt_cookie(self):
        """Test that the cookie decrypt function works."""
        testreq = get_request_with_fernet()
        # Generate cookie is tested separately, it can be used for testing the
        # rest of the functions without mockups
        cookie, testreq.cookies['S3BROW_SESSION'] = generate_cookie(testreq)
        self.assertEqual(cookie, decrypt_cookie(testreq))

    def test_session_check_nocookie(self):
        """Test session check raise 401 on non-existing cookie."""
        req = get_request_with_fernet()
        with self.assertRaises(HTTPUnauthorized):
            session_check(req)

    def test_session_check_invtoken(self):
        """Test session check raise 401 on a stale cookie."""
        req = get_request_with_fernet()
        _, req.cookies['S3BROW_SESSION'] = generate_cookie(req)
        req.app['Crypt'] = cryptography.fernet.Fernet(
            cryptography.fernet.Fernet.generate_key()
        )
        with self.assertRaises(HTTPUnauthorized):
            session_check(req)

    def test_session_check_nosession(self):
        """
        Test session check function raise 401 on invalid session cookie.

        (i.e. it cannot be found in the open session list)
        """
        req = get_request_with_fernet()
        _, req.cookies['S3BROW_SESSION'] = generate_cookie(req)
        req.app['Sessions'] = {}
        with self.assertRaises(HTTPUnauthorized):
            session_check(req)

    def test_session_check_expired_last_used(self):
        """Test session check function raise on expired last use."""
        session, req = get_request_with_mock_openstack()
        req.app["Sessions"][session]["last_used"] = time.time() - 7200
        with self.assertRaises(HTTPUnauthorized):
            session_check(req)

    def test_session_check_expired_max_lifetime(self):
        """Test session check function raise on expired lifetime."""
        session, req = get_request_with_mock_openstack()
        req.app["Sessions"][session]["max_lifetime"] = time.time() - 86400
        with self.assertRaises(HTTPUnauthorized):
            session_check(req)

    def test_session_check_correct(self):
        """
        Test that the ordinary session check function result is True.

        Test condition when the request is formed correctly.
        """
        req = get_request_with_fernet()
        cookie, _ = generate_cookie(req)

        req.cookies['S3BROW_SESSION'] = \
            get_full_crypted_session_cookie(cookie, req.app)

        session = cookie["id"]

        req.app['Sessions'][session] = {}
        req.app['Sessions'][session]['last_used'] = time.time() - 360
        req.app['Sessions'][session]['max_lifetime'] = time.time() + 86400
        self.assertIsNone(session_check(req))

    # The api_check session check function testing – Might seem unnecessary,
    # but are required since e.g. token rescoping can fail the sessions
    # before the next API call, also might try to use the API
    # while rescoping -> 401
    def test_api_check_raise_on_no_cookie(self):
        """Test raise if there's no session cookie."""
        testreq = get_request_with_fernet()
        _, testreq.cookies['S3BROW_SESSION'] = generate_cookie(testreq)
        testreq.app['Sessions'] = {}
        with self.assertRaises(HTTPUnauthorized):
            api_check(testreq)

    def test_api_check_raise_on_invalid_cookie(self):
        """Test raise if there's an invalid session cookie."""
        testreq = get_request_with_fernet()
        _, testreq.cookies['S3BROW_SESSION'] = generate_cookie(testreq)
        testreq.app['Sessions'] = {}
        with self.assertRaises(HTTPUnauthorized):
            api_check(testreq)

    def test_api_check_raise_on_invalid_fernet(self):
        """Test raise if the cryptographic key has changed."""
        testreq = get_request_with_fernet()
        _, testreq.cookies['S3BROW_SESSION'] = generate_cookie(testreq)
        testreq.app['Crypt'] = cryptography.fernet.Fernet(
            cryptography.fernet.Fernet.generate_key()
        )
        with self.assertRaises(HTTPUnauthorized):
            api_check(testreq)

    def test_api_check_raise_on_no_connection(self):
        """Test raise if there's no existing OS connection on an API call."""
        testreq = get_request_with_fernet()
        cookie, _ = generate_cookie(testreq)
        testreq.cookies['S3BROW_SESSION'] = \
            get_full_crypted_session_cookie(cookie, testreq.app)
        session = cookie["id"]
        testreq.app['Sessions'][session] = {}
        testreq.app['Sessions'][session]['Avail'] = "placeholder"
        testreq.app['Sessions'][session]['OS_sess'] = "placeholder"
        testreq.app['Sessions'][session]['last_used'] = time.time() - 360
        testreq.app['Sessions'][session]['max_lifetime'] = time.time() + 86400
        with self.assertRaises(HTTPUnauthorized):
            api_check(testreq)

    def test_api_check_raise_on_no_session(self):
        """Test raise if there's no established OS session on an API call."""
        testreq = get_request_with_fernet()
        cookie, _ = generate_cookie(testreq)
        testreq.cookies['S3BROW_SESSION'] = \
            get_full_crypted_session_cookie(cookie, testreq.app)
        session = cookie["id"]
        testreq.app['Sessions'][session] = {}
        testreq.app['Sessions'][session]['ST_conn'] = "placeholder"
        testreq.app['Sessions'][session]['Avail'] = "placeholder"
        testreq.app['Sessions'][session]['last_used'] = time.time() - 360
        testreq.app['Sessions'][session]['max_lifetime'] = time.time() + 86400
        with self.assertRaises(HTTPUnauthorized):
            api_check(testreq)

    def test_api_check_raise_on_no_avail(self):
        """Test raise if the availability wasn't checked before an API call."""
        testreq = get_request_with_fernet()
        cookie, _ = generate_cookie(testreq)
        testreq.cookies['S3BROW_SESSION'] = \
            get_full_crypted_session_cookie(cookie, testreq.app)
        session = cookie["id"]
        testreq.app['Sessions'][session] = {}
        testreq.app['Sessions'][session]['ST_conn'] = "placeholder"
        testreq.app['Sessions'][session]['OS_sess'] = "placeholder"
        testreq.app['Sessions'][session]['last_used'] = time.time() - 360
        testreq.app['Sessions'][session]['max_lifetime'] = time.time() + 86400
        with self.assertRaises(HTTPUnauthorized):
            api_check(testreq)

    def test_api_check_success(self):
        """Test that the api_check function runs with correct input."""
        testreq = get_request_with_fernet()
        cookie, _ = generate_cookie(testreq)
        testreq.cookies['S3BROW_SESSION'] = \
            get_full_crypted_session_cookie(cookie, testreq.app)
        session = cookie["id"]
        testreq.app['Sessions'][session] = {}
        testreq.app['Sessions'][session]['Avail'] = "placeholder"
        testreq.app['Sessions'][session]['OS_sess'] = "placeholder"
        testreq.app['Sessions'][session]['ST_conn'] = "placeholder"
        testreq.app['Sessions'][session]['last_used'] = time.time() - 360
        testreq.app['Sessions'][session]['max_lifetime'] = time.time() + 86400
        ret = api_check(testreq)
        self.assertEqual(ret, cookie["id"])

    def test_get_availability_from_token(self):
        """Test the get_availability_from_token function."""
        with unittest.mock.patch("swift_browser_ui._convenience.setd", new={
            "auth_endpoint_url": "http://example.osexampleserver.com:5001/v3"
        }):

            # Make the required patches to urllib.request to test the function
            with unittest.mock.patch("urllib.request.urlopen", new=urlopen):

                # Test with a valid token
                token = hashlib.md5(os.urandom(64)).hexdigest()  # nosec
                avail = get_availability_from_token(token)

                self.assertEqual(
                    avail['projects'], mock_token_output['projects']
                )
                self.assertEqual(
                    avail['domains'], mock_token_output['domains']
                )

    def test_initiate_os_session(self):
        """Test initiate_os_session function."""
        with unittest.mock.patch("swift_browser_ui.settings.setd", new={
            "auth_endpoint_url": "http://example-auth.exampleosep.com:5001/v3"
        }):
            ret = initiate_os_session(
                hashlib.md5(os.urandom(64)).hexdigest(),  # nosec
                "testproject"
            )
            self.assertIsInstance(ret, Session)  # nosec

    def test_initiate_os_service(self):
        """Test initiate_os_servce function."""
        with unittest.mock.patch("swift_browser_ui.settings.setd", new={
            "auth_endpoint_url": "http://example-auth.exampleosep.com:5001/v3",
            "swift_endpoint_url": "http://obj.exampleosep.com:443/v1",
        }):
            sess_mock = unittest.mock.MagicMock(Session)
            ret = initiate_os_service(sess_mock())
            self.assertIsInstance(ret, SwiftService)  # nosec

    def test_check_csrf_os_skip(self):
        """Test check_csrf when skipping referer from OS."""
        with unittest.mock.patch("swift_browser_ui._convenience.setd", new={
            "auth_endpoint_url": "http://example-auth.exampleosep.com:5001/v3"
        }):
            testreq = get_request_with_fernet()
            cookie, _ = generate_cookie(testreq)
            cookie = add_csrf_to_cookie(cookie, testreq)
            encrypt_cookie(cookie, testreq)
            testreq.headers["Referer"] = "http://example-auth.exampleosep.com"
            self.assertTrue(check_csrf(testreq))

    def test_check_csrf_incorrect_referer(self):
        """Test check_csrf when Referer header is incorrect."""
        with unittest.mock.patch("swift_browser_ui._convenience.setd", new={
            "auth_endpoint_url": "http://example-auth.exampleosep.com:5001/v3"
        }):
            testreq = get_request_with_fernet()
            cookie, _ = generate_cookie(testreq)
            cookie = add_csrf_to_cookie(cookie, testreq)
            encrypt_cookie(cookie, testreq)
            testreq.headers["Referer"] = "http://notlocaclhost:8080"
            with self.assertRaises(HTTPForbidden):
                check_csrf(testreq)

    def test_check_csrf_incorrect_signature(self):
        """Test check_csrf when signature doesn't match."""
        with unittest.mock.patch("swift_browser_ui._convenience.setd", new={
            "auth_endpoint_url": "http://example-auth.exampleosep.com:5001/v3"
        }):
            testreq = get_request_with_fernet()
            cookie, _ = generate_cookie(testreq)
            cookie = add_csrf_to_cookie(cookie, testreq, bad_sign=True)
            encrypt_cookie(cookie, testreq)
            testreq.headers["Referer"] = "http://localhost:8080"
            with self.assertRaises(HTTPForbidden):
                check_csrf(testreq)

    def test_check_csrf_no_referer(self):
        """Test check_csrf when no Referer header is present."""
        with unittest.mock.patch("swift_browser_ui._convenience.setd", new={
            "auth_endpoint_url": "http://example-auth.exampleosep.com:5001/v3"
        }):
            testreq = get_request_with_fernet()
            cookie, _ = generate_cookie(testreq)
            cookie = add_csrf_to_cookie(cookie, testreq)
            encrypt_cookie(cookie, testreq)
            self.assertTrue(check_csrf(testreq))

    def test_check_csrf_correct_referer(self):
        """Test check_csrf when the session is valid."""
        with unittest.mock.patch("swift_browser_ui._convenience.setd", new={
            "auth_endpoint_url": "http://example-auth.exampleosep.com:5001/v3"
        }):
            testreq = get_request_with_fernet()
            cookie, _ = generate_cookie(testreq)
            cookie = add_csrf_to_cookie(cookie, testreq)
            encrypt_cookie(cookie, testreq)
            testreq.headers["Referer"] = "http://localhost:8080"
            self.assertTrue(check_csrf(testreq))

    def test_clear_session_info(self):
        """Test if session information clear works."""
        session, req = get_request_with_mock_openstack()
        sess_mock = unittest.mock.MagicMock("keystoneauth.session.Session")
        sess = sess_mock()
        req.app["Sessions"][session]["OS_sess"] = sess
        req.app["Sessions"][session]["Token"] = "not_real_token"

        clear_session_info(req.app["Sessions"][session])

        sess.invalidate.assert_called_once()
        self.assertIsNone(req.app["Sessions"][session]["ST_conn"])
        self.assertIsNone(req.app["Sessions"][session]["OS_sess"])
        self.assertIsNone(req.app["Sessions"][session]["Avail"])
        self.assertIsNone(req.app["Sessions"][session]["Token"])
