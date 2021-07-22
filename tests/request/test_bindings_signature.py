"""Module for testing singatures in bindings module."""


import unittest.mock


import asynctest


from swift_browser_ui.request.bindings.signature import sign_api_request


class SignatureModuleTestCase(asynctest.TestCase):
    """Test case for signature related methods."""

    async def test_sign_api_request(self):
        """Test sign_api_request function."""
        os_environ_mock = unittest.mock.Mock(return_value="testkey")
        os_environ_patch = unittest.mock.patch(
            "swift_browser_ui.request.bindings.signature.os.environ.get",
            new=os_environ_mock,
        )

        with os_environ_patch:
            ret = sign_api_request("testpath")
            self.assertEqual(type(ret), dict)
            os_environ_mock.assert_called_once()
