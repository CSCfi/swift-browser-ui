"""Async Python bindings for the swift-x-account-sharing backend."""


import json
import logging
import os
import ssl
import typing

import aiohttp
import certifi

import swift_browser_ui.common.signature

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())


class SwiftSharingRequest:
    """Swift Sharing Request backend client."""

    def __init__(self, url: str) -> None:
        """."""
        self.url = url
        self.session = aiohttp.ClientSession()

    async def __aenter__(self) -> "SwiftSharingRequest":
        """."""
        return self

    async def __aexit__(self, *excinfo: BaseException) -> None:
        """."""
        await self.session.close()

    async def _handler_response(self, resp: aiohttp.ClientResponse) -> typing.Any:
        """Handle API response."""
        if resp.status == 200:
            try:
                return json.loads(await resp.text())
            except json.decoder.JSONDecodeError:
                logging.error("Decoding JSON error, " "response was not possible.")
                raise
            except Exception as e:
                logging.error("Unknown exception " f"occured with content: {e}.")
                raise
        else:
            logging.error(
                f"API call {resp.url} responded with "
                f"status {resp.status} and reason {resp.reason}."
            )
            raise Exception

    async def add_access_request(self, user: str, container: str, owner: str) -> dict:
        """Add a request for container access."""
        path = f"/request/user/{user}/{container}"
        url = self.url + path

        signature = swift_browser_ui.common.signature.sign_api_request(path)

        params = {
            "owner": owner,
            "valid": signature["valid"],
            "signature": signature["signature"],
        }

        async with self.session.post(url, params=params, ssl=ssl_context) as resp:
            return await self._handler_response(resp)

    async def list_made_requests(self, user: str) -> typing.List[dict]:
        """List requests made by user."""
        path = f"/request/user/{user}"
        url = self.url + path

        signature = swift_browser_ui.common.signature.sign_api_request(path)

        params = {
            "valid": signature["valid"],
            "signature": signature["signature"],
        }

        async with self.session.get(url, params=params, ssl=ssl_context) as resp:
            return await self._handler_response(resp)

    async def list_owned_requests(self, user: str) -> typing.List[dict]:
        """List requests owned by the user."""
        path = f"/request/owner/{user}"
        url = self.url + path

        signature = swift_browser_ui.common.signature.sign_api_request(path)

        params = {
            "valid": signature["valid"],
            "signature": signature["signature"],
        }

        async with self.session.get(url, params=params, ssl=ssl_context) as resp:
            return await self._handler_response(resp)

    async def list_container_requests(self, container: str) -> typing.List[dict]:
        """List requests made for a container."""
        path = f"/request/container/{container}"
        url = self.url + path

        project = os.environ.get("OS_PROJECT_ID", None)

        signature = swift_browser_ui.common.signature.sign_api_request(path)

        params = {
            "valid": signature["valid"],
            "signature": signature["signature"],
        }

        if project:
            params["project"] = project

        async with self.session.get(url, params=params, ssl=ssl_context) as resp:
            return await self._handler_response(resp)

    async def share_delete_access(
        self, username: str, container: str, owner: str
    ) -> bool:
        """Delete the details of an existing access request."""
        path = "/request/user/{username}/{container}"
        url = self.url + path

        signature = swift_browser_ui.common.signature.sign_api_request(path)

        params = {
            "owner": owner,
            "valid": signature["valid"],
            "signature": signature["signature"],
        }

        async with self.session.delete(url, params=params, ssl=ssl_context) as resp:
            return bool(resp.status == 200)
