"""Health check endpoint."""


import typing
import time

import aiohttp.web
from aiohttp.client_exceptions import ServerDisconnectedError

from .settings import setd
from .signature import sign


async def get_x_account_sharing(
        services: typing.Dict[str, typing.Any],
        request: aiohttp.web.Request,
        web_client: aiohttp.ClientSession,
        api_params: dict,
        performance: typing.Dict[str, typing.Any]
) -> None:
    """Poll swift-x-account-sharing API."""
    try:
        if setd["sharing_internal_endpoint"]:
            start = time.time()
            async with web_client.get(
                    str(setd["sharing_internal_endpoint"]) + "/health",
                    params=api_params
            ) as resp:
                request.app["Log"].debug(resp)
                if resp.status != 200:
                    services["swift-x-account-sharing"] = {
                        "status": "Down",
                    }
                else:
                    sharing_status = await resp.json()
                    services["swift-x-account-sharing"] = sharing_status
            performance["swift-x-account-sharing"] = {
                "time": time.time() - start
            }
        else:
            services["swift-x-account-sharing"] = {
                "status": "Nonexistent"
            }
    except ServerDisconnectedError:
        request.app["Log"].debug("Poll swift-x-account-sharing failed")
        services["swift-x-account-sharing"] = {
            "status": "Error"
        }


async def get_swift_sharing(
        services: typing.Dict[str, typing.Any],
        request: aiohttp.web.Request,
        web_client: aiohttp.ClientSession,
        api_params: dict,
        performance: typing.Dict[str, typing.Any]
) -> None:
    """Poll swift-sharing-request API."""
    try:
        if setd["request_internal_endpoint"]:
            start = time.time()
            async with web_client.get(
                    str(setd["request_internal_endpoint"]) + "/health",
                    params=api_params
            ) as resp:
                request.app["Log"].debug(resp)
                if resp.status != 200:
                    services["swift-sharing-request"] = {
                        "status": "Down",
                    }
                else:
                    request_status = await resp.json()
                    services["swift-sharing-request"] = request_status
            performance["swift-sharing-request"] = {
                "time": time.time() - start
            }
        else:
            services["swift-sharing-request"] = {
                "status": "Nonexistent"
            }
    except ServerDisconnectedError:
        request.app["Log"].debug("Poll swift-x-account-sharing failed")
        services["swift-sharing-request"] = {
            "status": "Error"
        }


async def get_upload_runner(
        services: typing.Dict[str, typing.Any],
        request: aiohttp.web.Request,
        web_client: aiohttp.ClientSession,
        api_params: dict,
        performance: typing.Dict[str, typing.Any]
) -> None:
    """Poll swiftui-upload-runner API."""
    try:
        if setd["upload_internal_endpoint"]:
            start = time.time()
            async with web_client.get(
                    str(setd["upload_internal_endpoint"]) + "/health",
                    params=api_params
            ) as resp:
                request.app["Log"].debug(resp)
                if resp.status != 200:
                    services["swiftui-upload-runner"] = {
                        "status": "Down",
                    }
                else:
                    upload_status = await resp.json()
                    services["swiftui-upload-runner"] = upload_status
            performance["swiftui-upload-runner"] = {
                "time": time.time() - start
            }
        else:
            services["swiftui-upload-runner"] = {
                "status": "Nonexistent"
            }
    except ServerDisconnectedError:
        request.app["Log"].debug("Poll swift-x-account-sharing failed")
        services["swiftui-upload-runner"] = {
            "status": "Error"
        }


async def handle_health_check(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Handle a service health check."""
    # Pull all health endpoint information
    web_client = request.app["api_client"]

    status: typing.Dict[str, typing.Union[
        str, typing.Dict
    ]] = {
        "status": "Ok",
    }

    services: typing.Dict[str, typing.Any] = dict()
    performance: typing.Dict[str, typing.Any] = dict()

    signature = await sign(60, "/health")
    api_params = {
        "signature": signature["signature"],
        "valid": signature["valid_until"]
    }

    await get_x_account_sharing(services,
                                request,
                                web_client,
                                api_params,
                                performance)

    await get_swift_sharing(services,
                            request,
                            web_client,
                            api_params,
                            performance)

    await get_upload_runner(services,
                            request,
                            web_client,
                            api_params,
                            performance)

    status["services"] = services
    status["performance"] = performance

    for service in services.values():
        if service["status"] in ["Down", "Error"]:
            status["status"] = "Partially down"
            break
        if service["status"] == "Degraded":
            status["status"] = "Degraded"

    for perf in performance.values():
        if perf["time"] > 1000 and not status["status"] == "Down":
            status["status"] = "Degraded (high load)"

    return aiohttp.web.json_response(status)
