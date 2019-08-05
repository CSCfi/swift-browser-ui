"""
Module that contains some frequently used constructors.

The purpose is to ease in the building of the test environment.
"""


import logging
import hashlib
import os
import json

import cryptography.fernet
from swift_browser_ui._convenience import generate_cookie

from .mockups import Mock_Request, Mock_Service, Mock_Session


def get_request_with_fernet():
    """Create a request with a working fernet object."""
    ret = Mock_Request()
    ret.app['Sessions'] = []
    ret.app['Creds'] = {}
    ret.app['Log'] = logging.getLogger(name="test_logger")
    ret.app['Crypt'] = cryptography.fernet.Fernet(
        cryptography.fernet.Fernet.generate_key()
    )
    ret.app['Salt'] = hashlib.sha256(os.urandom(512)).hexdigest()
    return ret


def get_request_with_mock_openstack():
    """Create a request with a openstack mock-up service & session."""
    ret = get_request_with_fernet()
    cookie, _ = generate_cookie(ret)
    cookie["referer"] = "http://localhost:8080"
    cookie["signature"] = (hashlib.sha256((cookie["id"] +
                                           cookie["referer"] +
                                           ret.app["Salt"])
                                          .encode('utf-8'))).hexdigest()
    session = cookie["id"]
    ret.cookies["S3BROW_SESSION"] = ret.app["Crypt"].encrypt(
        json.dumps(cookie).encode('utf-8')
    ).decode('utf-8')
    ret.app['Sessions'].append(session)
    ret.app['Creds'][session] = {}
    ret.app['Creds'][session]['OS_sess'] = Mock_Session()
    ret.app['Creds'][session]['ST_conn'] = Mock_Service()
    ret.app['Creds'][session]['Avail'] = {
        "projects": ['test-project-1', 'test-project-2'],
        "domains": ['default']
    }
    return session, ret


def get_full_crypted_session_cookie(cookie, app):
    """."""
    cookie["referer"] = "http://localhost:8080"
    cookie["signature"] = (hashlib.sha256((cookie["id"] +
                                           cookie["referer"] +
                                           app["Salt"])
                                          .encode('utf-8'))).hexdigest()
    return app["Crypt"].encrypt(
        json.dumps(cookie).encode('utf-8')
    ).decode('utf-8')
