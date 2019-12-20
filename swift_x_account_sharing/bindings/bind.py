"""Async Python bindings for the swift-x-account-sharing backend."""


import json
import typing

import aiohttp

from .signature import sign_api_request


class SwiftXAccountSharing:
    """Swift X Account Sharing backend client."""

    def __init__(
            self,
            url: str
    ):
        """."""
        self.url = url
        self.session = aiohttp.ClientSession()

    async def __aenter__(self):
        """."""
        return self

    async def __aexit__(self, *excinfo):
        """."""
        await self.session.close()

    @staticmethod
    def parse_list_to_string(
            to_parse: typing.List[str]
    ) -> str:
        """Parse the list of users into a comma separated list."""
        ret = ""
        for item in to_parse:
            ret = ret + item + ","
        return ret.rstrip(",")

    async def get_access(
            self,
            username: str
    ) -> typing.List[dict]:
        """List the containers the user has been given access to."""
        path = "/access/{0}".format(username)
        url = self.url + path

        params = sign_api_request(path)

        async with self.session.get(url, params=params) as resp:
            return json.loads(await resp.text())

    async def get_access_details(
            self,
            username: str,
            container: str,
            owner: str
    ) -> dict:
        """Get details from a container the user has been given access to."""
        path = "/access/{0}/{1}".format(
            username,
            container
        )
        url = self.url + path

        params = sign_api_request(path)
        params.update({"owner": owner})

        async with self.session.get(url, params=params) as resp:
            return json.loads(await resp.text())

    async def get_share(
            self,
            username: str
    ) -> typing.List[dict]:
        """List the containers the user has shared to another user / users."""
        path = "/share/{0}".format(username)
        url = self.url + path

        params = sign_api_request(path)

        async with self.session.get(url, params=params) as resp:
            return json.loads(await resp.text())

    async def get_share_details(
            self,
            username: str,
            container: str
    ) -> dict:
        """Get details from a container the user has given access to."""
        path = "/share/{0}/{1}".format(
            username,
            container
        )
        url = self.url + path

        params = sign_api_request(path)

        async with self.session.get(url, params=params) as resp:
            return json.loads(await resp.text())

    async def share_new_access(
            self,
            username: str,
            container: str,
            userlist: typing.List[str],
            accesslist: typing.List[str],
            address: str
    ) -> dict:
        """Upload details about a new share action."""
        path = "/share/{0}/{1}".format(
            username,
            container
        )
        url = self.url + path

        params = sign_api_request(path)

        params.update({
            "user": self.parse_list_to_string(userlist),
            "access": self.parse_list_to_string(accesslist),
            "address": address
        })

        async with self.session.post(url, params=params) as resp:
            return json.loads(await resp.text())

    async def share_edit_access(
            self,
            username: str,
            container: str,
            userlist: typing.List[str],
            accesslist: typing.List[str]
    ) -> dict:
        """Edit the details of an existing share action."""
        path = "/share/{0}/{1}".format(
            username,
            container
        )
        url = self.url + path

        params = sign_api_request(path)
        params.update({
            "user": self.parse_list_to_string(userlist),
            "access": self.parse_list_to_string(accesslist),
        })

        async with self.session.patch(url, params=params) as resp:
            return json.loads(await resp.text())

    async def share_delete_access(
            self,
            username: str,
            container: str,
            userlist: typing.List[str]
    ) -> bool:
        """Delete the details of an existing share action."""
        path = "/share/{0}/{1}".format(
            username,
            container
        )
        url = self.url + path

        params = sign_api_request(path)
        params.update({
            "user": self.parse_list_to_string(userlist),
        })

        async with self.session.delete(url, params=params) as resp:
            return bool(resp.status == 204)
