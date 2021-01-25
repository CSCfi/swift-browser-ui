"""Async Python bindings for the swift-x-account-sharing backend."""


import os
import json
import typing
import logging
import aiohttp

from .signature import sign_api_request

import ssl
import certifi


ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())


class SwiftSharingRequest:
    """Swift Sharing Request backend client."""

    def __init__(
            self,
            url: str
    ) -> None:
        """."""
        self.url = url
        self.session = aiohttp.ClientSession()

    async def __aenter__(self) -> 'SwiftSharingRequest':
        """."""
        return self

    async def __aexit__(self, *excinfo: BaseException) -> None:
        """."""
        await self.session.close()

    async def add_access_request(
            self,
            user: str,
            container: str,
            owner: str
    ) -> dict:
        """Add a request for container access."""
        path = f"/request/user/{user}/{container}"
        url = self.url + path

        signature = sign_api_request(path)

        params = {
            "owner": owner,
            "valid": signature["valid"],
            "signature": signature["signature"],
        }

        async with self.session.post(url,
                                     params=params,
                                     ssl=ssl_context) as resp:
            if resp.status == 200:
                try:
                    return json.loads(await resp.text())
                except json.decoder.JSONDecodeError:
                    logging.error("Decoding JSON error \
                        response was not possible.")
                    raise
                except Exception as e:
                    logging.error(f"Unknown exception \
                        occured with content: {e}.")
                    raise
            else:
                logging.error(f"response status: {resp.status}.")
                raise Exception(f"response status: {resp.status}.")

    async def list_made_requests(
            self,
            user: str
    ) -> typing.List[dict]:
        """List requests made by user."""
        path = f"/request/user/{user}"
        url = self.url + path

        signature = sign_api_request(path)

        params = {
            "valid": signature["valid"],
            "signature": signature["signature"],
        }

        async with self.session.get(url,
                                    params=params,
                                    ssl=ssl_context) as resp:
            if resp.status == 200:
                try:
                    return json.loads(await resp.text())
                except json.decoder.JSONDecodeError:
                    logging.error("Decoding JSON error \
                        response was not possible.")
                    raise
                except Exception as e:
                    logging.error(f"Unknown exception \
                        occured with content: {e}.")
                    raise
            else:
                logging.error(f"response status: {resp.status}.")
                raise Exception(f"response status: {resp.status}.")

    async def list_owned_requests(
            self,
            user: str
    ) -> typing.List[dict]:
        """List requests owned by the user."""
        path = f"/request/owner/{user}"
        url = self.url + path

        signature = sign_api_request(path)

        params = {
            "valid": signature["valid"],
            "signature": signature["signature"],
        }

        async with self.session.get(url,
                                    params=params,
                                    ssl=ssl_context) as resp:
            if resp.status == 200:
                try:
                    return json.loads(await resp.text())
                except json.decoder.JSONDecodeError:
                    logging.error("Decoding JSON error \
                        response was not possible.")
                    raise
                except Exception as e:
                    logging.error(f"Unknown exception \
                        occured with content: {e}.")
                    raise
            else:
                logging.error(f"response status: {resp.status}.")
                raise Exception(f"response status: {resp.status}.")

    async def list_container_requests(
            self,
            container: str
    ) -> typing.List[dict]:
        """List requests made for a container."""
        path = f"/request/container/{container}"
        url = self.url + path

        project = os.environ.get("OS_PROJECT_ID", None)

        signature = sign_api_request(path)

        params = {
            "valid": signature["valid"],
            "signature": signature["signature"],
        }

        if project:
            params["project"] = project

        async with self.session.get(url,
                                    params=params,
                                    ssl=ssl_context) as resp:
            return json.loads(await resp.text())

    async def share_delete_access(
            self,
            username: str,
            container: str,
            owner: str
    ) -> bool:
        """Delete the details of an existing access request."""
        path = "/request/user/{username}/{container}"
        url = self.url + path

        signature = sign_api_request(path)

        params = {
            "owner": owner,
            "valid": signature["valid"],
            "signature": signature["signature"],
        }

        async with self.session.delete(url,
                                       params=params,
                                       ssl=ssl_context) as resp:
            return bool(resp.status == 200)
