"""Module for testing swift_browser_ui common utility functions."""


import unittest

import asynctest


import swift_browser_ui.common.common_util


class CommonUtilTestCase(asynctest.TestCase):
    """Clkass for testing common utility functions."""

    def setUp(self):
        self.app_mock = {}
        super().setUp()

    async def test_read_in_keys(self):
        """Test read_in_keys function."""
        os_environ_mock = unittest.mock.Mock(return_value="a,b,c,d,e,f")
        os_environ_patch = unittest.mock.patch(
            "swift_browser_ui.common.common_util.os.environ.get", new=os_environ_mock
        )
        with os_environ_patch:
            await swift_browser_ui.common.common_util.read_in_keys(self.app_mock)
            os_environ_mock.assert_called_once()
            self.assertIsNotNone(self.app_mock["tokens"])
