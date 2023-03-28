"""Mock-up classes and functions for testing swift_browser_ui."""

import json
import yarl
import unittest
import unittest.mock
import time
import types
import logging

import aiohttp_session


class APITestBase(unittest.IsolatedAsyncioTestCase):
    """Base class for API tests using aiohttp client and server."""

    def setUp(self):
        """Set up mocks."""
        self.session_return = aiohttp_session.Session(
            "test-identity",
            new=True,
            data={},
        )
        self.session_return["token"] = "not-really-a-token"  # nosec
        self.session_return["at"] = time.time()
        self.session_return["referer"] = "http://localhost:8080"
        self.session_return["uname"] = "testuser"
        self.session_return["projects"] = {
            "test-id-0": {
                "id": "test-id-0",
                "name": "test-name-0",
                "token": "test-token-0",
                "endpoint": "https://test-endpoint-0/v1/AUTH_test-id-0",
                "tainted": False,
            },
            "test-id-1": {
                "id": "test-id-1",
                "name": "test-name-1",
                "token": "test-token-1",
                "endpoint": "https://test-endpoint-1/v1/AUTH_test-id-1",
                "tainted": False,
                "runner": "test-runner"
            },
        }
        self.aiohttp_session_get_session_mock = unittest.mock.AsyncMock()
        self.aiohttp_session_get_session_mock.return_value = self.session_return
        self.p_get_sess = unittest.mock.patch(
            "swift_browser_ui.ui.api.aiohttp_session.get_session",
            self.aiohttp_session_get_session_mock,
        )
        self.aiohttp_session_new_session_mock = unittest.mock.AsyncMock()
        self.p_new_sess = unittest.mock.patch(
            "swift_browser_ui.ui.login.aiohttp_session.new_session",
            self.aiohttp_session_new_session_mock,
        )
        self.aiohttp_session_get_session_oidc_mock = unittest.mock.AsyncMock()
        self.aiohttp_session_get_session_oidc_mock.return_value = {
            **self.session_return,
            "oidc": {
                "userinfo": {},
                "state": "",
                "access_token": "",
            },
        }
        self.p_get_sess_oidc = unittest.mock.patch(
            "swift_browser_ui.ui.api.aiohttp_session.get_session",
            self.aiohttp_session_get_session_oidc_mock,
        )

        self.setd_mock = {
            "auth_endpoint_url": "https://example.os.com:5001/v3",
            "set_origin_address": "https://localhost/login/websso",
            "has_trust": True,
            "upload_external_endpoint": "http://test-endpoint:9092/",
            "oidc_enabled": False,
            "upload_internal_endpoint": "http://test-endpoint",
        }
        self.patch_setd = unittest.mock.patch(
            "swift_browser_ui.ui.api.setd", self.setd_mock
        )

        self.aiohttp_json_response_mock = unittest.mock.Mock()
        self.p_json_resp = unittest.mock.patch(
            "swift_browser_ui.ui.api.aiohttp.web.json_response",
            self.aiohttp_json_response_mock,
        )

        self.mock_response_write = unittest.mock.AsyncMock()
        self.mock_response_prepare = unittest.mock.AsyncMock()
        self.mock_response_write_eof = unittest.mock.AsyncMock()
        self.aiohttp_construct_response_mock = unittest.mock.Mock()
        self.aiohttp_construct_response_mock.return_value = types.SimpleNamespace(
            **{
                "status": 200,
                "headers": {},
                "cookie": {},
                "write": self.mock_response_write,
                "prepare": self.mock_response_prepare,
                "write_eof": self.mock_response_write_eof,
            }
        )
        self.p_resp = unittest.mock.patch(
            "swift_browser_ui.ui.api.aiohttp.web.Response",
            self.aiohttp_construct_response_mock,
        )
        self.p_sresp = unittest.mock.patch(
            "swift_browser_ui.ui.api.aiohttp.web.StreamResponse",
            self.aiohttp_construct_response_mock,
        )

        self.mock_response_read = unittest.mock.AsyncMock(return_value=b"exampleread")
        self.mock_iter = unittest.mock.Mock(return_value=b"test-chunk")

        async def citer(_):
            yield self.mock_iter()

        self.mock_client_json = {"status": "Ok"}
        self.mock_client_text = ""
        self.mock_client_response = types.SimpleNamespace(
            **{
                "status": 200,
                "headers": {},
                "cookie": {},
                "json": unittest.mock.AsyncMock(return_value=self.mock_client_json),
                "content": types.SimpleNamespace(
                    **{
                        "iter_chunked": citer,
                    }
                ),
                "read": self.mock_response_read,
                "text": unittest.mock.AsyncMock(return_value=self.mock_client_text),
                "url": "https://localhost:8080",
            }
        )

        class MockHandler(APITestBase):
            def __init__(self, mockresp):
                """."""
                self.mock_client_response = mockresp

            async def __aenter__(self):
                return self.mock_client_response

            async def __aexit__(self, *_):
                return

        self.MockHandler = MockHandler
        self.mock_client = types.SimpleNamespace(
            **{
                "get": unittest.mock.Mock(
                    return_value=self.MockHandler(
                        self.mock_client_response,
                    )
                ),
                "post": unittest.mock.Mock(
                    return_value=self.MockHandler(
                        self.mock_client_response,
                    )
                ),
                "put": unittest.mock.Mock(
                    return_value=self.MockHandler(
                        self.mock_client_response,
                    )
                ),
                "delete": unittest.mock.Mock(
                    return_value=self.MockHandler(
                        self.mock_client_response,
                    )
                ),
                "head": unittest.mock.Mock(
                    return_value=self.MockHandler(
                        self.mock_client_response,
                    )
                ),
            }
        )
        self.mock_oidc_userinfo = types.SimpleNamespace(
            **{
                "to_dict": unittest.mock.Mock(return_value={}),
            }
        )
        self.mock_oidc_client = types.SimpleNamespace(
            **{
                "begin": unittest.mock.Mock(
                    return_value={
                        "url": "/should_be_oidc_provider",
                    }
                ),
                "get_session_information": unittest.mock.Mock(
                    return_value={
                        "auth_request": {},
                        "iss": "",
                    }
                ),
                "finalize": unittest.mock.Mock(
                    return_value={
                        "userinfo": self.mock_oidc_userinfo,
                        "state": "",
                        "token": "",
                    }
                ),
            }
        )

        self.mock_request = types.SimpleNamespace(
            **{
                "match_info": {
                    "project": "test-id-0",
                    "container": "test-container",
                    "object": "test-object",
                    "receiver": "test-project-1",
                },
                "cookies": {},
                "query": {},
                "headers": {},
                "query_string": "",
                "remote": "test-remote",
                "json": None,
                "post": unittest.mock.AsyncMock(),
                "app": {
                    "api_client": self.mock_client,
                    "client": self.mock_client,
                    "Log": unittest.mock.MagicMock(logging.Logger),
                    "test-id": "placeholder",
                    "oidc_client": self.mock_oidc_client,
                },
                "url": types.SimpleNamespace(
                    **{
                        "host": "https://localhost",
                    }
                ),
                "path": "/",
            }
        )
        super().setUp()


mock_token_project_avail: dict = {
    "projects": [
        # there is a special use case when this is first
        # as the list of projects might give 401
        {
            "is_domain": False,
            "description": "Not enabled project",
            "links": {"self": "https://place-holder-url:5001/v3/projects/no"},
            "enabled": False,
            "id": "no",
            "parent_id": "default",
            "domain_id": "default",
            "name": "no",
        },
        {
            "is_domain": False,
            "description": "",
            "links": {"self": "https://place-holder-url:5001/v3/projects/placeholder"},
            "enabled": True,
            "id": "placeholder",
            "parent_id": "default",
            "domain_id": "default",
            "name": "placeholder",
        },
        {
            "is_domain": False,
            "description": "Wololo yol aweii",
            "links": {"self": "https://place-holder-url:5001/v3/projects/wol"},
            "enabled": True,
            "id": "wol",
            "parent_id": "default",
            "domain_id": "default",
            "name": "wol",
        },
        {
            "is_domain": False,
            "description": "Hmmph, what is",
            "links": {"self": "https://place-holder-url:5001/v3/projects/what"},
            "enabled": True,
            "id": "what",
            "parent_id": "default",
            "domain_id": "default",
            "name": "what",
        },
    ],
}

mock_token_domain_avail: dict = {"domains": []}

mock_token_output = {
    "projects": [
        {
            "is_domain": False,
            "description": "",
            "links": {"self": "https://place-holder-url:5001/v3/projects/placeholder"},
            "enabled": True,
            "id": "placeholder",
            "parent_id": "default",
            "domain_id": "default",
            "name": "placeholder",
        },
        {
            "is_domain": False,
            "description": "Wololo yol aweii",
            "links": {"self": "https://place-holder-url:5001/v3/projects/wol"},
            "enabled": True,
            "id": "wol",
            "parent_id": "default",
            "domain_id": "default",
            "name": "wol",
        },
        {
            "is_domain": False,
            "description": "Hmmph, what is",
            "links": {"self": "https://place-holder-url:5001/v3/projects/what"},
            "enabled": True,
            "id": "what",
            "parent_id": "default",
            "domain_id": "default",
            "name": "what",
        },
    ],
    "domains": [],
}


class Mock_Request:
    """
    Mock-up class for the aiohttp.web.Request.

    It contains the dictionary
    representation of the requests that will be passed to the functions.
    (the actual request being a MutableMapping instance)
    """

    def __init__(self):
        """Initialize Mock request."""
        # Application mutable mapping represented by a dictionary
        self.app = {}
        self.headers = {}
        self.cookies = {}
        self.query = {}
        self.match_info = {}
        self.remote = "127.0.0.1"
        self.url = yarl.URL("http://localhost:8080")
        self.path = "/"
        self.post_data = {}

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

    def set_query(self, query):
        """Set mock request query."""
        for i in query.keys():
            self.query[i] = query[i]

    def set_match(self, match):
        """Set mock request match_info."""
        for i in match.keys():
            self.match_info[i] = match[i]

    def set_post(self, data):
        """Set post data."""
        self.post_data = data

    def set_path(self, path):
        self.path = path

    async def post(self):
        """Return post data."""
        return self.post_data

    async def json(self):
        if isinstance(self.post_data, str):
            return json.loads(self.post_data)
        return self.post_data
