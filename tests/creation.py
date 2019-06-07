"""
This module contains some frequently used constructors to ease in the building
of the test environment.
"""


import cryptography.fernet
from mockups import Mock_Request


def get_request_with_fernet():
    """
    Create a request with a working fernet object
    """
    ret = Mock_Request()
    ret.app['Sessions'] = []
    ret.app['Creds'] = []
    ret.app['Crypt'] = cryptography.fernet.Fernet(
        cryptography.fernet.Fernet.generate_key()
    )
    return ret
