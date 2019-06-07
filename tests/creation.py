"""
This module contains some frequently used constructors to ease in the building
of the test environment.
"""


import cryptography.fernet
from mockups import Mock_Request, Mock_Service, Mock_Session
from s3browser._convenience import generate_cookie
import logging


def get_request_with_fernet():
    """
    Create a request with a working fernet object
    """
    ret = Mock_Request()
    ret.app['Sessions'] = []
    ret.app['Creds'] = {}
    ret.app['Log'] = logging.getLogger(name="test_logger")
    ret.app['Crypt'] = cryptography.fernet.Fernet(
        cryptography.fernet.Fernet.generate_key()
    )
    return ret


def get_request_with_mock_openstack():
    """
    Create a request with a "working" openstack mock-up service and session
    """
    ret = get_request_with_fernet()
    cookie, ret.cookies['S3BROW_SESSION'] = generate_cookie(ret)
    ret.app['Sessions'].append(cookie)
    ret.app['Creds'][cookie] = {}
    ret.app['Creds'][cookie]['OS_sess'] = Mock_Session()
    ret.app['Creds'][cookie]['ST_conn'] = Mock_Service()
    ret.app['Creds'][cookie]['Avail'] = "Placeholder"
    return cookie, ret
