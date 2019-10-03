"""Sharing backend API specification and implementation."""


import aiohttp.web


async def has_access_handler(request):
    """Handle has-access endpoint query."""
    # Future authorization check here

    # Check for incorrect client query here

    access_list = request.app["db_conn"].get_access_list(
        request.match_info["user"]
    )
    return aiohttp.web.json_response(access_list)


async def access_details_handler(request):
    """Handle access-details endpoint query."""
    # Future authorization check here

    # Check for incorrect client query here

    access_details = request.app["db_conn"].get_access_container_details(
        request.match_info["user"],
        request.query["owner"],
        request.match_info["container"]
    )
    return aiohttp.web.json_response(access_details)


async def gave_access_handler(request):
    """Handle gave-access endpoint query."""
    # Future authorization check here

    # Check for incorrect client query here

    shared_list = request.app["db_conn"].get_shared_list(
        request.match_info["owner"]
    )
    return aiohttp.web.json_response(shared_list)


async def shared_details_handler(request):
    """Handle shared-details endpoint query."""
    # Future authorization check here

    # Check for incorrect client query here

    shared_details = request.app["db_conn"].get_shared_container_details(
        request.match_info["owner"],
        request.match_info["container"]
    )
    return aiohttp.web.json_response(shared_details)


async def share_container_handler(request):
    """Handle share-container endpoint query."""
    # Future authorization check here

    # Check for incorrect client query here

    request.app["db_conn"].add_share(
        request.match_info["owner"],
        request.match_info["container"],
        request.query["user"].split(","),
        request.query["access"].split(","),
        request.query["address"]
    )

    return aiohttp.web.Response(
        status=204,
        body="OK"
    )


async def edit_share_handler(request):
    """Handle container shared rights editions."""
    # Future authorization check here

    # Check for incorrect client query here

    edited = request.app["db_conn"].edit_share(
        request.match_info["owner"],
        request.match_info["container"],
        request.query["user"].split(","),
        request.query["access"].split(",")
    )

    return aiohttp.web.json_response(edited)


async def delete_share_handler(request):
    """Handle unshare-container endpoint query."""
    # Future authorization check here

    # Check for incorrect client query here

    deleted = request.app["db_conn"].delete_share(
        request.match_info["owner"],
        request.match_info["container"],
        request.query["user"].split(",")
    )

    if not deleted:
        raise aiohttp.web.HTTPNotFound()

    return aiohttp.web.Response(
        status=204,
        body="OK"
    )
