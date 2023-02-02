"""Module for testing ``swift_browser_ui.discover``."""

import json
import unittest

from swift_browser_ui.ui.discover import handle_discover


class DiscoverTestClass(unittest.IsolatedAsyncioTestCase):
    """Testing the endpoint discovery handler."""

    async def test_valid_json_reply(self):
        """Test if the handler returns a valid JSON reply with information."""
        patch_setd = unittest.mock.patch(
            "swift_browser_ui.ui.discover.setd",
            new={
                "sharing_endpoint": "http://example",
                "request_endpoint": "http://example",
                "upload_external_endpoint": "http://example",
            },
        )
        with patch_setd:
            resp = await handle_discover(None)
            resp = json.loads(resp.text)
            self.assertEqual("http://example", resp["sharing_endpoint"])
