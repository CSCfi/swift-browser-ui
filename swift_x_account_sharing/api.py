"""Sharing backend API specification and implementation."""


import aiohttp.web


async def has_access_handler(request):
    """Handle has-access endpoint query."""
    # Future authorization check here

    # Check for incorrect client query here

    access_list = request.app["db_conn"].get_access_list(request.query["user"])
    if not access_list:
        raise aiohttp.web.HTTPNotFound()
    return aiohttp.web.json_response(access_list)


async def access_details_handler(request):
    """Handle access-details endpoint query."""
    # Future authorization check here

    # Check for incorrect client query here

    access_details = request.app["db_conn"].get_access_container_details(
        request.query["user"],
        request.query["owner"],
        request.query["container"]
    )
    if not access_details:
        raise aiohttp.web.HTTPNotFound()
    return aiohttp.web.json_response(access_details)


async def gave_access_handler(request):
    """Handle gave-access endpoint query."""
    # Future authorization check here

    # Check for incorrect client query here

    shared_list = request.app["db_conn"].get_shared_list(
        request.query["user"]
    )
    if not shared_list:
        raise aiohttp.web.HTTPNotFound()
    return aiohttp.web.json_response(shared_list)


async def shared_details_handler(request):
    """Handle shared-details endpoint query."""
    # Future authorization check here

    # Check for incorrect client query here

    shared_details = request.app["db_conn"].get_shared_container_details(
        request.query["user"],
        request.query["container"]
    )
    if not shared_details:
        raise aiohttp.web.HTTPNotFound()
    return aiohttp.web.json_response(shared_details)


async def share_container_handler(request):
    """Handle share-container endpoint query."""
    # Future authorization check here

    # Check for incorrect client query here

    request.app["db_conn"].add_share(
        request.query["owner"],
        request.query["container"],
        request.query["user"].split(","),
        request.query["access"].split(","),
        request.query["address"]
    )

    return aiohttp.web.Response(
        status=204,
        body="OK"
    )


async def unshare_container_handler(request):
    """Handle unshare-container endpoint query."""
    # Future authorization check here

    # Check for incorrect client query here

    request.app["db_conn"].remove_share(
        request.query["owner"],
        request.query["container"],
        request.query["user"].split(","),
        request.query["access"].split(",")
    )

    return aiohttp.web.Response(
        status=204,
        body="OK"
    )
