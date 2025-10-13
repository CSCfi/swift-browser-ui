"""Common resources for swift-upload-runner."""

import logging
import os
import typing

import aiohttp.web

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


VAULT_CLIENT = "vault_client"
SEGMENTS_CONTAINER = "_segments"


def generate_download_url(
    host: str,
    container: typing.Union[str, None] = None,
    object_name: typing.Union[str, None] = None,
) -> str:
    """Generate the download URL to use."""
    if not container and not object_name:
        return host
    elif not object_name:
        return f"{host}/{container}"
    # The object_name based URL works fine with prefixes as well
    return f"{host}/{container}/{object_name}"


def get_download_host(endpoint: str, project: str) -> str:
    """Return the catalog endpoint as-is."""
    return str(endpoint)


def get_session_id(request: aiohttp.web.Request) -> str:
    """Return the session id from request."""
    try:
        return request.cookies["RUNNER_SESSION_ID"]
    except KeyError:
        try:
            return request.query["session"]
        except KeyError:
            raise aiohttp.web.HTTPUnauthorized(reason="Missing runner session ID")


def get_path_from_list(to_parse: typing.List[str], path_prefix: str) -> str:
    """Parse a path from a list of path parts."""
    ret = path_prefix

    for i in to_parse:
        ret += f"/{i}"

    return ret.lstrip("/").rstrip("/")
