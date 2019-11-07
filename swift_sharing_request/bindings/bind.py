"""Async Python bindings for the swift-x-account-sharing backend."""


import json


import aiohttp


class SwiftSharingRequest:
    """Swift X Account Sharing backend client."""

    def __init__(self, url):
        """."""
        self.url = url
        self.session = aiohttp.ClientSession()

    async def __aenter__(self):
        """."""
        return self

    async def __aexit__(self, *excinfo):
        """."""
        await self.session.close()

    async def add_access_request(self, user, container, owner):
        """Add a request for container access."""
        url = "{0}/request/user/{user}/{container}".format(
            self.url,
            user,
            container
        )
        params = {
            "owner": owner,
        }

        async with self.session.post(url, params=params) as resp:
            return json.loads(await resp.text())

    async def list_made_requests(self, user):
        """List requests made by user."""
        url = "{0}/request/user/{1}".format(
            self.url,
            user
        )

        async with self.session.get(url) as resp:
            return json.loads(await resp.text())

    async def list_owned_requests(self, user):
        """List requests owned by the user."""
        url = "{0}/request/owner/{1}".format(
            self.url,
            user
        )

        async with self.session.get(url) as resp:
            return json.loads(await resp.text())

    async def list_container_requests(self, container):
        """List requests made for a container."""
        url = "{0}/request/container/{1}".format(
            self.url,
            container
        )

        async with self.session.get(url) as resp:
            return json.loads(await resp.text())

    async def share_delete_access(
            self,
            username,
            container,
            owner
    ):
        """Delete the details of an existing access request."""
        url = "{0}/request/user/{1}/{2}".format(self.url, username, container)
        params = {
            "owner": owner,
        }

        async with self.session.delete(url, params=params) as resp:
            return bool(resp.status == 200)
