"""
This module contains the mock-up classes and functions, used for testing the
s3browser package.
"""


class Mock_Request:
    """
    Mock-up class for the aiohttp.web.Request, which contains the dictionary
    representation of the requests that will be passed to the functions. (the
    actual request eing a MutableMapping instance)
    """
    app = None
    headers = {}
    cookies = {}

    def set_headers(self, headers):
        """
        Set mock request headers.
        Params:
            headers: dict
        """
        for i in headers.keys():
            self.headers[i] = headers[i]

    def set_cookies(self, cookies):
        """
        Set mock request cookies.
        Params:
            cookies: dict
        """
        for i in cookies.keys():
            self.cookies[i] = cookies[i]

    def set_app(self, app):
        """
        Set mock request application.
        Params:
            app: object(Mock_App)
        """
        self.app = app


class Mock_App:
    """
    Mock-up class for the aiohttp.web.Application, which contains the
    dictionary representation of the Application. (the actual application
    being a MutableMapping instance)
    """
    def __init__(self):
        pass


class Mock_Service:
    """
    Mock-up class for the Openstack service, in this case a swiftclient.Service
    instance. Contains the mock-ups for the relevant methods used in this
    project. Also contains functions for generating test data, in case it is
    necessary.
    """
    def __init__(self):
        pass


class Mock_Session:
    """
    Mock--up class for the Openstack keystoneauth1 session instance, which
    contains the relevant methods for querying the OS identity API (aka.
    keystone)
    """
    def __init__(self):
        pass
