"""Async Python bindings for the swift-x-account-sharing backend."""


import json
import typing
import logging
import aiohttp

from .signature import sign_api_request

import ssl
import certifi


ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())


class SwiftXAccountSharing:
    """Swift X Account Sharing backend client."""

    def __init__(
            self,
            url: str
    ) -> None:
        """."""
        self.url = url
        self.session = aiohttp.ClientSession()

    async def __aenter__(self) -> 'SwiftXAccountSharing':
        """."""
        return self

    async def __aexit__(self, *excinfo: BaseException) -> None:
        """."""
        await self.session.close()

    async def _handler_response(
            self,
            resp: aiohttp.ClientResponse
    ) -> typing.Any:
        """Handle API response."""
        if resp.status == 200:
            try:
                return json.loads(await resp.text())
            except json.decoder.JSONDecodeError:
                logging.error("Decoding JSON error, "
                              "response was not possible.")
                raise
            except Exception as e:
                logging.error("Unknown exception "
                              f"occured with content: {e}.")
                raise
        else:
            logging.error(f"API call {resp.url} responded with "
                          f"status {resp.status} and reason {resp.reason}.")
            raise Exception

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
        path = f"/access/{username}"
        url = self.url + path

        params = sign_api_request(path)

        async with self.session.get(url,
                                    params=params,
                                    ssl=ssl_context) as resp:

            return await self._handler_response(resp)

    async def get_access_details(
            self,
            username: str,
            container: str,
            owner: str
    ) -> dict:
        """Get details from a container the user has been given access to."""
        path = f"/access/{username}/{container}"
        url = self.url + path

        params = sign_api_request(path)
        params.update({"owner": owner})

        async with self.session.get(url,
                                    params=params,
                                    ssl=ssl_context) as resp:
            return await self._handler_response(resp)

    async def get_share(
            self,
            username: str
    ) -> typing.List[dict]:
        """List the containers the user has shared to another user / users."""
        path = f"/share/{username}"
        url = self.url + path

        params = sign_api_request(path)

        async with self.session.get(url,
                                    params=params,
                                    ssl=ssl_context) as resp:
            return await self._handler_response(resp)

    async def get_share_details(
            self,
            username: str,
            container: str
    ) -> dict:
        """Get details from a container the user has given access to."""
        path = f"/share/{username}/{container}"
        url = self.url + path

        params = sign_api_request(path)

        async with self.session.get(url,
                                    params=params,
                                    ssl=ssl_context) as resp:
            return await self._handler_response(resp)

    async def share_new_access(
            self,
            username: str,
            container: str,
            userlist: typing.List[str],
            accesslist: typing.List[str],
            address: str
    ) -> dict:
        """Upload details about a new share action."""
        path = f"/share/{username}/{container}"
        url = self.url + path

        params = sign_api_request(path)

        params.update({
            "user": self.parse_list_to_string(userlist),
            "access": self.parse_list_to_string(accesslist),
            "address": address
        })

        async with self.session.post(url,
                                     params=params,
                                     ssl=ssl_context) as resp:
            return await self._handler_response(resp)

    async def share_edit_access(
            self,
            username: str,
            container: str,
            userlist: typing.List[str],
            accesslist: typing.List[str]
    ) -> dict:
        """Edit the details of an existing share action."""
        path = f"/share/{username}/{container}"
        url = self.url + path

        params = sign_api_request(path)
        params.update({
            "user": self.parse_list_to_string(userlist),
            "access": self.parse_list_to_string(accesslist),
        })

        async with self.session.patch(url,
                                      params=params,
                                      ssl=ssl_context) as resp:
            return await self._handler_response(resp)

    async def share_delete_access(
            self,
            username: str,
            container: str,
            userlist: typing.List[str]
    ) -> bool:
        """Delete the details of an existing share action."""
        path = f"/share/{username}/{container}"
        url = self.url + path

        params = sign_api_request(path)
        params.update({
            "user": self.parse_list_to_string(userlist),
        })

        async with self.session.delete(url,
                                       params=params,
                                       ssl=ssl_context) as resp:
            if resp.status == 204:
                return True
            else:
                logging.error(f"API call {resp.url} responded with status "
                              f"{resp.status} and reason {resp.reason}.")
                raise Exception
