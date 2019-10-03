"""Async Python bindings for the swift-x-account-sharing backend."""


import json


import aiohttp


class SwiftXAccountSharing:
    """Swift X Account Sharing backend client."""

    def __init__(self, url):
        """."""
        self.url = url
        self.session = aiohttp.ClientSession()

    def __del__(self):
        """."""
        self.session.close()

    @staticmethod
    def parse_list_to_string(to_parse):
        """Parse the list of users into a comma separated list."""
        ret = ""
        for item in to_parse:
            ret = ret + item + ","
        return ret.rstrip(",")

    async def get_access(
            self,
            username
    ):
        """List the containers the user has been given access to."""
        url = "{0}/access/{1}".format(self.url, username)

        async with self.session.get(url) as resp:
            return json.loads(await resp.text())

    async def get_access_details(
            self,
            username,
            container,
            owner
    ):
        """Get details from a container the user has been given access to."""
        url = "{0}/access/{1}/{2}".format(self.url, username, container)
        params = {"owner": owner}

        async with self.session.get(url, params=params) as resp:
            return json.loads(await resp.text())

    async def get_share(
            self,
            username
    ):
        """List the containers the user has shared to another user / users."""
        url = "{0}/share/{1}".format(self.url, username)

        async with self.session.get(url) as resp:
            return json.loads(await resp.text())

    async def get_share_details(
            self,
            username,
            container
    ):
        """Get details from a container the user has given access to."""
        url = "{0}/share/{1}/{2}".format(self.url, username, container)

        async with self.session.get(url) as resp:
            return json.loads(await resp.text())

    async def share_new_access(
            self,
            username,
            container,
            userlist,
            accesslist,
            address
    ):
        """Upload details about a new share action."""
        url = "{0}/share/{1}/{2}".format(self.url, username, container)
        params = {
            "user": self.parse_list_to_string(userlist),
            "access": self.parse_list_to_string(accesslist),
            "address": address
        }

        async with self.session.post(url, params=params) as resp:
            return json.loads(await resp.text())

    async def share_edit_access(
            self,
            username,
            container,
            userlist,
            accesslist
    ):
        """Edit the details of an existing share action."""
        url = "{0}/share/{1}/{2}".format(self.url, username, container)
        params = {
            "user": self.parse_list_to_string(userlist),
            "access": self.parse_list_to_string(accesslist),
        }

        async with self.session.patch(url, params=params) as resp:
            return json.loads(await resp.text())

    async def share_delete_access(
            self,
            username,
            container,
            userlist
    ):
        """Delete the details of an existing share action."""
        url = "{0}/share/{1}/{2}".format(self.url, username, container)
        params = {
            "user": self.parse_list_to_string(userlist),
        }

        async with self.session.delete(url, params=params) as resp:
            return bool(resp.status == 204)
