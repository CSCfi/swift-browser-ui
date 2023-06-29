"""Vault c4ghtransit client."""
import asyncio
import logging
import os
import time
from base64 import standard_b64encode
from dataclasses import dataclass
from typing import Any, Dict, List

from aiohttp import ClientSession, ClientTimeout
from aiohttp.web import HTTPError, HTTPGatewayTimeout, HTTPInternalServerError
from yarl import URL

LOGGER = logging.getLogger("swift_browser_ui.common.vault_client")
LOGGER.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


class VaultServerError(HTTPError):
    """Service server errors should produce a 502 Bad Gateway response."""

    status_code = 502


class VaultClientError(HTTPError):
    """Service client errors should be raised unmodified."""

    def __init__(
        self,
        status_code: int,
        **kwargs: Any,
    ) -> None:
        """Class to raise for http client errors.

        HTTPError doesn't have a setter for status_code, so this allows setting it.

        :param status_code: Set the status code here
        """
        self.status_code = status_code
        HTTPError.__init__(self, **kwargs)


@dataclass
class VaultError:
    """Unpack a vault error into an object."""

    errors: List[str]


def _make_exception(reason: str, status: int) -> HTTPError:
    """Create a Client or Server exception, according to status code.

    https://developer.hashicorp.com/vault/api-docs#http-status-codes

    :param reason: Error message
    :param status: HTTP status code
    :returns VaultServerError or VaultClientError.
    """
    if status < 400:
        LOGGER.error("HTTP status code must be an error code, >400 received %s.", status)
        return HTTPInternalServerError(
            reason="Server encountered an unexpected situation."
        )
    reason = f"Vault error: {reason}"
    if status >= 500:
        return VaultServerError(text=reason, reason=reason)
    return VaultClientError(text=reason, reason=reason, status_code=status)


def _process_error(vault_error: VaultError) -> str:
    """Return formatted error message.

    https://developer.hashicorp.com/vault/api-docs#error-response

    :param vault_error: Vault error dictionary object
    :returns: formatted error message as a string.
    """
    return vault_error.errors[0]


class VaultClient:
    """AioHttp client that interacts with a Vault server."""

    _vault_token = str()
    service = "SD-Connect"

    def __init__(self, http_client: ClientSession):
        """Reuse an existing http client, and load environment variables.

        :param http_client: aiohttp.ClientSession instance
        """
        self._client = http_client
        self._base_url = URL(os.environ.get("VAULT_URL", "http://localhost:8200/v1"))
        self._role = os.environ.get("VAULT_ROLE", "")
        self._secret = os.environ.get("VAULT_SECRET", "")

        # TODO: The key name should be set by the `swift-browser-ui` client
        self._key_name = os.environ.get("VAULT_KEY_NAME", "")
        self._token_expires = 0

    async def _token(self) -> str:
        """Vault authentication token.

        When a token is not set, or seems to be expiring soon, it creates a new token.
        This requires the environment variables to be set.
        Token expiration logic uses the lease duration information from Vault.

        :returns: Vault token as str
        """
        if not self._vault_token or (self._token_expires - time.monotonic()) < 10:
            auth = {
                "role_id": self._role,
                "secret_id": self._secret,
            }
            LOGGER.debug("Attempting to create a new token")
            async with self._client.post(
                self._base_url / "auth/approle/login", json=auth
            ) as auth_response:
                response = await auth_response.json()
                if auth_response.ok:
                    self._token_expires = (
                        time.monotonic() + response["auth"]["lease_duration"]
                    )
                    self._vault_token = response["auth"]["client_token"]
                    LOGGER.debug("New token generated")

                else:
                    message = _process_error(VaultError(**response))
                    reason = f"Vault client was unable to authenticate: {message}"
                    LOGGER.error(reason)
                    raise VaultServerError(reason=reason)

        return self._vault_token

    async def _request(
        self,
        method: str = "GET",
        path: str = "",
        params: None | Dict[str, Any] = None,
        json_data: None | Dict[str, Any] | List[Dict[str, Any]] = None,
        timeout: int = 10,
    ) -> None | str | Dict[Any, Any]:
        """Request to Vault API with error handling logic, and retries in case of token expiry.

        :param method: HTTP method
        :param path: When requesting to self.base_url, provide only the path (shortcut).
        :param params: URL parameters, must be url encoded
        :param json_data: Dict with request data
        :param timeout: Request timeout in seconds
        :returns: Response body parsed as JSON, when present, or None
        """
        url = self._base_url / path

        LOGGER.debug(
            "%s request to: %r, params %r, request payload: %r",
            method,
            url,
            params,
            json_data,
        )

        try:
            n_retries = 0
            max_retries = 3
            # Retry in case Vault authentication failed
            while True:
                async with self._client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    timeout=ClientTimeout(total=timeout),
                    headers={
                        "X-Vault-Token": await self._token(),
                        "X-Vault-Request": "true",
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                    },
                ) as response:
                    LOGGER.debug(
                        "%s request to: %r, returned: %r",
                        method,
                        url,
                        response.status,
                    )
                    if response.status == 204 or response.status == 404:
                        return None

                    content: Dict[str, Any] = await response.json()
                    if response.status == 200:
                        LOGGER.debug("Content: %r", content)
                        return content

                    LOGGER.exception(response)

                    if response.status == 403:
                        LOGGER.debug("Authentication error, will retry.")
                        print(n_retries, max_retries)
                        n_retries += 1
                        self._vault_token = str()
                        if n_retries >= max_retries:
                            LOGGER.debug(
                                "Authentication error, retried too many times, raising."
                            )
                            response.raise_for_status()
                        await asyncio.sleep(0.2)
                        continue

                    if response.status >= 400:
                        message = _process_error(VaultError(**content))
                        raise VaultServerError(text=message, reason=message)

                    break
            return None

        except HTTPError as error:
            LOGGER.exception(error)
            raise
        except TimeoutError as exc:
            LOGGER.exception("%s request to %r timed out.", method, url)
            raise HTTPGatewayTimeout(
                reason="Vault error: Timeout trying to reach service provider."
            ) from exc
        except Exception as exc:
            LOGGER.exception(
                "%s request to %r raised an unexpected exception.", method, url
            )
            message = "Unexpected issue when connecting to service provider."
            raise VaultServerError(text=message, reason=message) from exc

    async def get_public_key(self, project: str) -> str:
        """Get a project specific public key.

        If a key is not found for a project, creates a new one and fetches it.

        :param project: Project ID
        :returns: Public key as a base64 encoded string
        """

        async def get_key() -> str:
            """Reusable function to get the public key."""
            key_json = await self._request("GET", f"c4ghtransit/keys/{project}")
            if isinstance(key_json, dict) and "data" in key_json:
                latest_version = str(key_json["data"]["latest_version"])
                return str(key_json["data"]["keys"][latest_version]["public_key_c4gh_64"])
            return ""

        LOGGER.debug("Getting public key for project %r", project)
        key = await get_key()
        if not key:
            LOGGER.debug(
                "No key: %s found for project %r, creating a new one.", key, project
            )
            await self._request(
                "POST", f"c4ghtransit/keys/{project}", json_data={"flavor": "crypt4gh"}
            )
            return await get_key()

        LOGGER.debug("Got key %r for project %r", key, project)
        return key

    async def put_whitelist_key(
        self, project: str, flavor: str, public_key: bytes
    ) -> None:
        """Update the project's whitelisted key.

        :param project: Project ID
        :param flavor: Public key flavor: one of crypt4gh or ed25519
        :param public_key: Public key bytes
        """
        await self._request(
            "POST",
            f"c4ghtransit/whitelist/{project}/{self.service}/{self._key_name}",
            json_data={
                "flavor": flavor,
                "pubkey": standard_b64encode(public_key).decode("ascii"),
            },
        )

    async def remove_whitelist_key(self, project: str) -> None:
        """Delete the project's whitelisted key.

        :param project: Project ID
        """
        await self._request(
            "DELETE", f"c4ghtransit/whitelist/{project}/{self.service}/{self._key_name}"
        )

    async def get_header(self, project: str, container: str, path: str) -> str:
        """Retrieve header.

        :param project: Project ID
        :param container: container name
        :param path: object path
        """
        header_response = await self._request(
            "GET",
            f"c4ghtransit/files/{project}/{container}/{path}",
            params={"service": self.service, "key": self._key_name},
        )
        if isinstance(header_response, dict) and "data" in header_response:
            return str(header_response["data"]["headers"]["1"]["header"])
        return ""

    async def put_header(
        self, project: str, container: str, path: str, header: str
    ) -> None:
        """Update header.

        :param project: Project ID
        :param container: container name
        :param path: object path
        :param header: header as b64 encoded string
        """
        await self._request(
            "POST",
            f"c4ghtransit/files/{project}/{container}/{path}",
            json_data={"header": header},
        )
