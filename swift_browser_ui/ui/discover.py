"""Endpoints for different server information discovery."""

from typing import Union

import aiohttp.web

from swift_browser_ui.ui.settings import setd


async def handle_discover(_: Union[aiohttp.web.Request, None]) -> aiohttp.web.Response:
    """Reply with sharing information if sharing API is available."""
    return aiohttp.web.json_response(
        {
            "sharing_endpoint": setd["sharing_endpoint"],
            "request_endpoint": setd["request_endpoint"],
            "upload_endpoint": setd["upload_external_endpoint"],
        }
    )


async def handle_s3_discover(_: Union[aiohttp.web.Request, None]) -> aiohttp.web.Response:
    """Handle requests for S3 API configuration."""
    # For now not returning region, as it shouldn't be a requirement for our needs
    return aiohttp.web.json_response(
        {
            "s3api_endpoint": setd["s3api_endpoint"],
        }
    )


async def handle_submit_discover(
    _: Union[aiohttp.web.Request, None]
) -> aiohttp.web.Response:
    """Reply with the information required for SD Submit integration."""
    if not setd["sd_submit_user"] or not setd["sd_submit_id"]:
        raise aiohttp.web.HTTPNotFound(
            reason="SD Submit integration has not been configured in the backend."
        )

    return aiohttp.web.json_response(
        {
            "sd_submit_user": setd["sd_submit_user"],
            "sd_submit_id": setd["sd_submit_id"],
        }
    )
