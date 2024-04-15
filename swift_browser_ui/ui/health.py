"""Health check endpoint."""

import time
import typing

import aiohttp.web
from aiohttp.client_exceptions import ServerDisconnectedError
from redis import ConnectionError

import swift_browser_ui.common.signature
from swift_browser_ui.ui._convenience import get_redis_client
from swift_browser_ui.ui.settings import setd


def _set_error_status(
    request: aiohttp.web.Request,
    services: typing.Dict[str, typing.Any],
    service: str,
) -> None:
    request.app["Log"].debug(f"Poll {service} failed")
    services[service] = {"status": "Error"}


async def get_x_account_sharing(
    services: typing.Dict[str, typing.Any],
    request: aiohttp.web.Request,
    web_client: aiohttp.ClientSession,
    api_params: dict,
    performance: typing.Dict[str, typing.Any],
) -> None:
    """Poll swift-x-account-sharing API."""
    try:
        if setd["sharing_internal_endpoint"]:
            start = time.time()
            async with web_client.get(
                str(setd["sharing_internal_endpoint"]) + "/health", params=api_params
            ) as resp:
                request.app["Log"].debug(resp)
                if resp.status != 200:
                    services["swift-x-account-sharing"] = {
                        "status": "Down",
                    }
                else:
                    sharing_status = await resp.json()
                    services["swift-x-account-sharing"] = sharing_status
            performance["swift-x-account-sharing"] = {"time": time.time() - start}
        else:
            services["swift-x-account-sharing"] = {"status": "Nonexistent"}
    except ServerDisconnectedError:
        _set_error_status(request, services, "swift-x-account-sharing")
    except Exception as e:
        request.app["Log"].info(f"Health failed for reason: {e}")
        _set_error_status(request, services, "swift-x-account-sharing")


async def get_swift_sharing(
    services: typing.Dict[str, typing.Any],
    request: aiohttp.web.Request,
    web_client: aiohttp.ClientSession,
    api_params: dict,
    performance: typing.Dict[str, typing.Any],
) -> None:
    """Poll swift-sharing-request API."""
    try:
        if setd["request_internal_endpoint"]:
            start = time.time()
            async with web_client.get(
                str(setd["request_internal_endpoint"]) + "/health", params=api_params
            ) as resp:
                request.app["Log"].debug(resp)
                if resp.status != 200:
                    services["swift-sharing-request"] = {
                        "status": "Down",
                    }
                else:
                    request_status = await resp.json()
                    services["swift-sharing-request"] = request_status
            performance["swift-sharing-request"] = {"time": time.time() - start}
        else:
            services["swift-sharing-request"] = {"status": "Nonexistent"}
    except ServerDisconnectedError:
        _set_error_status(request, services, "swift-sharing-request")
    except Exception as e:
        request.app["Log"].info(f"Health failed for reason: {e}")
        _set_error_status(request, services, "swift-sharing-request")


async def get_upload_runner(
    services: typing.Dict[str, typing.Any],
    request: aiohttp.web.Request,
    web_client: aiohttp.ClientSession,
    api_params: dict,
    performance: typing.Dict[str, typing.Any],
) -> None:
    """Poll swiftui-upload-runner API."""
    try:
        if setd["upload_internal_endpoint"]:
            start = time.time()
            async with web_client.get(
                str(setd["upload_internal_endpoint"]) + "/health", params=api_params
            ) as resp:
                request.app["Log"].debug(resp)
                if resp.status != 200:
                    services["swiftui-upload-runner"] = {"status": "Down"}
                    services["vault"] = {"status": "Down"}
                    end = time.time() - start
                    performance["swiftui-upload-runner"] = {"time": end}
                    performance["vault"] = {"time": end}
                else:
                    status = await resp.json()
                    services["swiftui-upload-runner"] = status["upload-runner"]
                    services["vault"] = status["vault-instance"]
                    performance["swiftui-upload-runner"] = {
                        "time": status["start-time"] - start
                    }
                    performance["vault"] = {
                        "time": status["end-time"] - status["start-time"]
                    }
        else:
            services["swiftui-upload-runner"] = {"status": "Nonexistent"}
    except ServerDisconnectedError:
        _set_error_status(request, services, "swiftui-upload-runner")
        _set_error_status(request, services, "vault")
    except Exception as e:
        request.app["Log"].info(f"Health failed for reason: {e}")
        _set_error_status(request, services, "swiftui-upload-runner")
        _set_error_status(request, services, "vault")


async def get_redis(
    services: typing.Dict[str, typing.Any],
    request: aiohttp.web.Request,
    performance: typing.Dict[str, typing.Any],
) -> None:
    """Poll Redis service."""
    try:
        start = time.time()
        redis_client = await get_redis_client()
        await redis_client.ping()
        services["redis"] = {"status": "Ok"}
        performance["redis"] = {"time": time.time() - start}
        await redis_client.close()
    except ConnectionError:
        services["redis"] = {"status": "Down"}
        performance["redis"] = {"time": time.time() - start}
    except Exception as e:
        request.app["Log"].info(f"Health failed for reason: {e}")
        _set_error_status(request, services, "redis")


async def handle_health_check(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Handle a service health check."""
    # Pull all health endpoint information
    web_client = request.app["api_client"]

    status: typing.Dict[str, typing.Union[str, typing.Dict]] = {
        "status": "Ok",
    }

    services: typing.Dict[str, typing.Any] = {}
    performance: typing.Dict[str, typing.Any] = {}

    signature = swift_browser_ui.common.signature.sign_api_request("/health")
    api_params = {
        "signature": signature["signature"],
        "valid": signature["valid"],
    }

    await get_x_account_sharing(services, request, web_client, api_params, performance)

    await get_swift_sharing(services, request, web_client, api_params, performance)

    await get_upload_runner(services, request, web_client, api_params, performance)

    await get_redis(services, request, performance)

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
