"""Common resources for swift-upload-runner."""


import typing


import aiohttp.web

import keystoneauth1.session


def generate_download_url(
        host,
        container=None,
        object_name=None,
) -> str:
    """Generate the download URL to use."""
    if not container and not object_name:
        return host
    elif not object_name:
        return f'{host}/{container}'
    # The object_name based URL works fine with prefixes as well
    return f'{host}/{container}/{object_name}'


def get_auth_instance(
        request: aiohttp.web.Request
) -> keystoneauth1.session.Session:
    """Return the session specific keystone auth instance"""
    try:
        return request.app[request.cookies["RUNNER_SESSION_ID"]]
    except KeyError:
        try:
            return request.app[request.query["session"]]
        except KeyError:
            raise aiohttp.web.HTTPUnauthorized(
                reason="Runner session ID missing"
            )


def get_path_from_list(
        to_parse: typing.List[str],
        path_prefix: str
) -> str:
    """Parse a path from a list of path parts."""
    ret = path_prefix

    for i in to_parse:
        ret += f"/{i}"

    return ret.lstrip("/").rstrip("/")


async def handle_delete_preflight(_) -> aiohttp.web.Response:
    """Serve correct response headers to allowed DELETE preflight query."""
    resp = aiohttp.web.Response(
        headers={
            "Access-Control-Allow-Methods": "POST, OPTIONS, DELETE",
            "Access-Control-Max-Age": "84600",
        }
    )
    return resp
