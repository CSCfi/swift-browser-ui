"""Module for testing ``swift_browser_ui.discover``."""

import json
import unittest.mock

import asynctest

from swift_browser_ui.discover import handle_discover


class DiscoverTestClass(asynctest.TestCase):
    """Testing the endpoint discovery handler."""

    async def test_valid_json_reply(self):
        """Test if the handler returns a valid JSON reply with information."""
        patch_setd = unittest.mock.patch(
            "swift_browser_ui.discover.setd",
            new={
                "sharing_endpoint": "http://example",
                "request_endpoint": "http://example",
            }
        )
        with patch_setd:
            resp = await handle_discover(None)
            resp = json.loads(resp.text)
            self.assertEqual("http://example", resp["sharing_endpoint"])
