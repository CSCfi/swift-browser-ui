"""Test sharing backend API functions."""


import asynctest


from swift_x_account_sharing.api import (
    has_access_handler,
    access_details_handler,
    gave_access_handler,
    shared_details_handler,
    share_container_handler,
    unshare_container_handler
)


class APITestClass(asynctest.TestCase):
    """Test the sharing backend public API."""

    async def test_endpoint_has_access_correct(self):
        """Test the has-access endpoint for conformity."""
        resp = await has_access_handler(None)
        self.assertEqual(resp.status, 200)

    async def test_endpoint_access_details_correct(self):
        """Test the access-details endpoint for conformity."""
        resp = await access_details_handler(None)
        self.assertEqual(resp.status, 200)

    async def test_endpoint_gave_access_correct(self):
        """Test the gave-access endpoint for conformity."""
        resp = await gave_access_handler(None)
        self.assertEqual(resp.status, 200)

    async def test_endpoint_shared_details_correct(self):
        """Test the shared_details endpoint for conformity."""
        resp = await shared_details_handler(None)
        self.assertEqual(resp.status, 200)

    async def test_endpoint_share_container_correct(self):
        """Test the share_container endpoint for conformity."""
        resp = await share_container_handler(None)
        self.assertEqual(resp.status, 200)

    async def test_endpoint_unshare_container_correct(self):
        """Test the unshare_container endpoint for conformmity."""
        resp = await unshare_container_handler(None)
        self.assertEqual(resp.status, 200)

    async def test_endpoint_has_access_noauth(self):
        """Test the has-access endpoint without authorization."""

    async def test_endpoint_access_details_noauth(self):
        """Test the access-details endpoint without authorization."""

    async def test_endpoint_gave_access_noauth(self):
        """Test the gave-access endpoint without authorization."""

    async def test_endpoint_shared_details_noauth(self):
        """Test the shared_details endpoint without authorization."""

    async def test_endpoint_share_container_noauth(self):
        """Test the share_container endpoint without authorization."""

    async def test_endpoint_unshare_container_noauth(self):
        """Test the unshare_container endpoint without authorization."""

    async def test_endpoint_has_access_missing(self):
        """Test the has-access endpoint with missing information."""

    async def test_endpoint_access_details_missing(self):
        """Test the access-details endpoint with missing information."""

    async def test_endpoint_gave_access_missing(self):
        """Test the gave-access endpoint with missing information."""

    async def test_endpoint_shared_details_missing(self):
        """Test the shared_details endpoint with missing information."""

    async def test_endpoint_share_container_missing(self):
        """Test the share_container endpoint with missing information."""

    async def test_endpoint_unshare_container_missing(self):
        """Test the unshare_container endpoint with missing information."""
