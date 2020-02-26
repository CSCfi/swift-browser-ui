"""Common resources for swift-upload-runner."""


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
