"""Common resources for swift-upload-runner."""


import logging
import os
import typing

import aiohttp.web

import swift_browser_ui.upload.cryptupload as cryptupload
from swift_browser_ui.upload import upload

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
    """Get the actual download host with shared container support."""
    ret = endpoint
    if project not in ret:
        ret = ret.replace(ret.split("/")[-1], f"AUTH_{project}")
    return str(ret)


def get_session_id(request: aiohttp.web.Request) -> str:
    """Return the session id from request."""
    try:
        return request.cookies["RUNNER_SESSION_ID"]
    except KeyError:
        try:
            return request.query["session"]
        except KeyError:
            raise aiohttp.web.HTTPUnauthorized(reason="Missing runner session ID")


async def parse_multipart_in(
    request: aiohttp.web.Request,
) -> typing.Tuple[typing.Dict[str, typing.Any], aiohttp.MultipartReader]:
    """Parse the form headers into a dictionary and chunk data as reader."""
    reader = await request.multipart()

    ret_d = {}

    while True:
        field = await reader.next()
        if field.name == "file":  # type: ignore
            ret_d["filename"] = field.filename  # type: ignore
            return ret_d, field  # type: ignore
        if field.name == "resumableChunkNumber":  # type: ignore
            ret_d["resumableChunkNumber"] = int(await field.text())  # type: ignore
        else:
            ret_d[
                str(field.name)  # type: ignore
            ] = await field.text()  # type: ignore


async def get_upload_instance(
    request: aiohttp.web.Request,
    pro: str,
    cont: str,
    p_query: typing.Dict[str, typing.Any] | None = None,
) -> upload.ResumableFileUploadProxy:
    """Return the specific upload proxy for the resumable upload."""
    session = get_session_id(request)

    if p_query:
        query: typing.Dict[str, typing.Any] = p_query
    else:
        query = request.query  # type: ignore

    # Check the existence of the dictionary structure
    try:
        request.app[session]["uploads"][pro]
    except KeyError:
        request.app[session]["uploads"][pro] = {}

    try:
        request.app[session]["uploads"][pro][cont]
    except KeyError:
        request.app[session]["uploads"][pro][cont] = {}

    try:
        ident = query["resumableIdentifier"]
    except KeyError:
        raise aiohttp.web.HTTPBadRequest(reason="Malformed query string")
    try:
        upload_session = request.app[session]["uploads"][pro][cont][ident]
    except KeyError:
        upload_session = upload.ResumableFileUploadProxy(
            request.app[session], query, request.match_info, request.app["client"]
        )
        await upload_session.a_check_container()
        request.app[session]["uploads"][pro][cont][ident] = upload_session

    return upload_session


def get_encrypted_upload_session(
    request: aiohttp.web.Request,
) -> cryptupload.UploadSession:
    """Return the specific encrypted upload session for the project."""
    session = get_session_id(request)
    project = request.match_info["project"]

    if project in request.app[session]["enuploads"]:
        LOGGER.debug(f"Returning an existing upload session for id {session}.")
        return request.app[session]["enuploads"][project]
    else:
        LOGGER.debug(f"Opening a new upload session for id {session}.")
        upload_session = cryptupload.UploadSession(request, request.app[session])
        request.app[session]["enuploads"][project] = upload_session
        return upload_session


def get_path_from_list(to_parse: typing.List[str], path_prefix: str) -> str:
    """Parse a path from a list of path parts."""
    ret = path_prefix

    for i in to_parse:
        ret += f"/{i}"

    return ret.lstrip("/").rstrip("/")
