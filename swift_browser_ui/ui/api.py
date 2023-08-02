"""Project functions for handling API requests from front-end."""

import asyncio
import json
import re
import ssl
import time
import typing
import urllib.parse
from datetime import datetime

import aiohttp.web
import aiohttp_session
import certifi
from swiftclient.utils import generate_temp_url

from swift_browser_ui.ui._convenience import (
    get_tempurl_key,
    open_upload_runner_session,
    sign,
)
from swift_browser_ui.ui.settings import setd

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())


async def get_os_user(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Fetch the session owning OS user."""
    session = await aiohttp_session.get_session(request)
    request.app["Log"].info(
        f"API call for username from {request.remote}, sess: {session} :: {time.ctime()}"
    )
    return aiohttp.web.json_response(session["uname"])


async def os_list_projects(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Fetch the projects available for the open session."""
    session = await aiohttp_session.get_session(request)
    request.app["Log"].info(
        "API call for project listing from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )
    # Filter out the tokens contained in session token
    return aiohttp.web.json_response(
        [
            {
                "name": v["name"],
                "id": v["id"],
                "tainted": v["tainted"],
            }
            for _, v in session["projects"].items()
        ]
    )


async def swift_list_containers(
    request: aiohttp.web.Request,
) -> aiohttp.web.StreamResponse:
    """Proxy Swift list buckets available to a project."""
    session = await aiohttp_session.get_session(request)
    client = request.app["api_client"]

    project = request.match_info["project"]
    request.app["Log"].info(
        "API call for list buckets from "
        f"{request.remote}, session: {session} :: {time.ctime()}"
    )

    query = request.query.copy()
    query["format"] = "json"
    try:
        async with client.get(
            session["projects"][project]["endpoint"],
            headers={"X-Auth-Token": session["projects"][project]["token"]},
            params=query,
        ) as ret:
            resp = aiohttp.web.StreamResponse(status=ret.status)
            await resp.prepare(request)
            if ret.status == 200:
                async for chunk in ret.content.iter_chunked(65535):
                    tasks = [
                        _check_last_modified(request, container)
                        for container in json.loads(chunk)
                    ]
                    ret = await asyncio.gather(*tasks)
                    chunk = json.dumps(ret).encode()
                    await resp.write(chunk)
            await resp.write_eof()
        return resp
    except KeyError:
        raise aiohttp.web.HTTPForbidden(
            reason="Account does not have access to the project."
        )


async def _check_last_modified(
    request: aiohttp.web.Request, container: typing.Dict[str, typing.Any]
) -> typing.Dict[str, typing.Any]:
    """Ensure container data includes 'last_modified' key and value.

    :param request: A request instance
    :param data: Containers basic info
    """
    session = await aiohttp_session.get_session(request)
    client = request.app["api_client"]
    request.app["Log"].info(
        "API call for project listing from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )
    project = request.match_info["project"]
    endpoint = session["projects"][project]["endpoint"]
    if "owner" in request.query:
        endpoint = endpoint.replace(project, request.query["owner"])

    # If last_modified is not part of container basic info,
    # head request is made to check container metadata
    # and add last modified data from there.
    if "last_modified" not in container.keys():
        try:
            name = container["name"]
            async with client.head(
                f"{endpoint}/{name}",
                headers={
                    "X-Auth-Token": session["projects"][project]["token"],
                },
            ) as ret:
                date_str = ret.headers["Last-Modified"]
                # Convert the date string to the ISO 8601 format
                date_obj = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %Z")
                iso_8601_str = date_obj.strftime("%Y-%m-%dT%H:%M:%S.%f")
                container["last_modified"] = iso_8601_str
        # we expect either the header Last Modified to be missing or
        # the value is not what we expect for str to date conversion
        except (KeyError, ValueError):
            # If anything goes wrong, set last_modified key anyway with null value
            container["last_modified"] = None
    return container


async def swift_create_container(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Create a new container from name."""
    session = await aiohttp_session.get_session(request)
    client = request.app["api_client"]
    project = request.match_info["project"]
    container = request.match_info["container"]

    request.app["Log"].info(
        f"API call for container creation from {request.remote}, sess {session}"
    )

    req_json = await request.json()
    tags = req_json.get("tags", None)

    headers = {"X-Auth-Token": session["projects"][project]["token"]}
    if tags:
        headers["X-Container-Meta-UserTags"] = tags

    async with client.put(
        f"{session['projects'][project]['endpoint']}/{container}",
        headers=headers,
        params=request.query,
    ) as ret:
        resp = aiohttp.web.Response(
            status=ret.status,
        )
    return resp


async def swift_delete_container(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Delete an empty container or batch delete objects."""
    if "objects" in request.query:
        return await swift_delete_objects(request)
    session = await aiohttp_session.get_session(request)
    client = request.app["api_client"]

    project = request.match_info["project"]
    container = request.match_info["container"]
    request.app["Log"].info(
        f"API call for container deletion from {request.remote}, sess {session}"
    )
    async with client.delete(
        f"{session['projects'][project]['endpoint']}/{container}",
        headers={
            "X-Auth-Token": session["projects"][project]["token"],
        },
        params=request.query,
    ) as ret:
        resp = aiohttp.web.Response(
            status=ret.status,
        )
    return resp


async def swift_delete_objects(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Delete objects."""
    session = await aiohttp_session.get_session(request)
    client = request.app["api_client"]
    project = request.match_info["project"]
    container = request.match_info["container"]

    # Bulk deletion middleware wants a list of URL-safe object names separated
    # with newlines
    objects = (
        "".join(
            [urllib.parse.quote(f"/{container}/{i}") + "\n" for i in await request.json()]
        )
    ).encode("utf-8")
    if len(objects) > 10000:
        raise aiohttp.web.HTTPBadRequest(reason="Too many objects (>10000)")

    async with client.post(
        f"{session['projects'][project]['endpoint']}",
        headers={
            "X-Auth-Token": session["projects"][project]["token"],
            "Accept": "application/json",
            "Content-Type": "text/plain",
        },
        params={
            "bulk-delete": "true",
        },
        data=objects,
    ) as ret:
        resp = aiohttp.web.Response(status=ret.status, body=(await ret.read()))
    return resp


async def swift_list_objects(request: aiohttp.web.Request) -> aiohttp.web.StreamResponse:
    """List objects in a given bucket or container."""
    session = await aiohttp_session.get_session(request)
    client = request.app["api_client"]
    project = request.match_info["project"]
    container = request.match_info["container"]

    request.app["Log"].info(
        "API call for list objects from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )

    query = request.query.copy()
    query["format"] = "json"

    endpoint = session["projects"][project]["endpoint"]
    if "owner" in request.query:
        endpoint = endpoint.replace(project, request.query["owner"])

    # TODO: MOVE UNICODE NULL HANDLING TO FRONTEND
    async with client.get(
        f"{endpoint}/{container}",
        headers={
            "X-Auth-Token": session["projects"][project]["token"],
        },
        params=query,
    ) as ret:
        resp = aiohttp.web.StreamResponse(
            status=ret.status,
        )
        await resp.prepare(request)
        async for chunk in ret.content.iter_chunked(65535):
            await resp.write(chunk)
        await resp.write_eof()

    return resp


async def swift_download_object(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Point a user to a temporary pre-signed download URL."""
    session = await aiohttp_session.get_session(request)
    client = request.app["api_client"]
    project = request.match_info["project"]
    object_name = request.match_info["object"]
    container = request.match_info["container"]
    request.app["Log"].info(
        "API call for download {object_name} from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )

    temp_url_key = await get_tempurl_key(request)
    request.app["Log"].debug(f"Using {temp_url_key} as temporary URL key")

    # Generate temporary URL with the key
    endpoint = session["projects"][project]["endpoint"]
    host = endpoint.split("/v1")[0]
    path_start = endpoint.replace(host, "")
    url = host + generate_temp_url(
        f"{path_start}/{container}/{object_name}",
        600,  # Use 10 minute lifetime
        temp_url_key,
        "GET",
    )

    async with client.head(
        f"{endpoint}/{container}/{object_name}",
        headers={
            "X-Auth-Token": session["projects"][project]["token"],
        },
    ) as ret:
        ctype = ret.headers["Content-Type"]

    return aiohttp.web.Response(
        status=302,
        headers={
            "Location": url,
            "Content-Type": ctype,
        },
    )


async def _swift_get_object_metadata_wrapper(
    request: aiohttp.web.Request, obj: str
) -> typing.Tuple[str, typing.Dict[str, typing.Any]]:
    """Get metadata for a single object."""
    session = await aiohttp_session.get_session(request)
    client = request.app["api_client"]
    project = request.match_info["project"]
    container = request.match_info["container"]

    if "owner" in request.query:
        owner: str = request.query["owner"]
    else:
        owner = ""

    endpoint = session["projects"][project]["endpoint"]
    async with client.head(
        f"{endpoint.replace(project, owner) if owner else endpoint}/{container}/{obj}",
        headers={
            "X-Auth-Token": session["projects"][project]["token"],
        },
    ) as ret:
        if ret.status != 200:
            raise aiohttp.web.HTTPInternalServerError(reason="Failed to fetch metadata.")
        meta = dict(filter(lambda i: "X-Object-Meta" in i[0], ret.headers.items()))
        meta = {k.replace("X-Object-Meta-", ""): v for k, v in meta.items()}
        if "s3cmd-attrs" in meta.keys():
            meta["s3cmd-attrs"] = dict(
                [j.split(":") for j in meta["s3cmd-attrs"].split("/")]
            )
    return (obj, meta)


async def swift_get_batch_object_metadata(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Batch get metadata for objects."""
    session = await aiohttp_session.get_session(request)
    request.app["Log"].info(
        "API call for batch object metadata listing "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )
    batch = []
    for obj in request.query["objects"].split(","):
        batch.append(_swift_get_object_metadata_wrapper(request, obj))
    batch = await asyncio.gather(*batch, return_exceptions=False)
    return aiohttp.web.json_response(batch)


async def swift_get_metadata_container(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Get metadata for a container."""
    if "objects" in request.query:
        return await swift_get_batch_object_metadata(request)
    session = await aiohttp_session.get_session(request)
    client = request.app["api_client"]
    request.app["Log"].info(
        "API call for project listing from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )
    project = request.match_info["project"]
    container = request.match_info["container"]
    if "owner" in request.query:
        owner: str = request.query["owner"]
    else:
        owner = ""

    endpoint = session["projects"][project]["endpoint"]
    async with client.head(
        f"{endpoint.replace(project, owner) if owner else endpoint}/{container}",
        headers={
            "X-Auth-Token": session["projects"][project]["token"],
        },
    ) as ret:
        headers = ret.headers
    return aiohttp.web.json_response(
        [
            container,
            {k.replace("X-Container-Meta-", ""): v for k, v in headers.items()},
        ]
    )


async def _swift_update_object_meta_wrapper(
    request: aiohttp.web.Request,
    obj: str,
    meta: typing.List[typing.Tuple[typing.Any, typing.Any]],
) -> int:
    """Update metadata for a single object."""
    session = await aiohttp_session.get_session(request)
    client = request.app["api_client"]
    project = request.match_info["project"]
    container = request.match_info["container"]

    headers = {(f"X-Object-Meta-{k}"): v for k, v in meta}
    headers.update(
        {
            "X-Auth-Token": session["projects"][project]["token"],
        }
    )

    async with client.post(
        f"{session['projects'][project]['endpoint']}/{container}/{obj}",
        headers=headers,
    ) as ret:
        return int(ret.status)


async def swift_batch_update_object_metadata(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Update metadata for an object."""
    session = await aiohttp_session.get_session(request)
    request.app["Log"].info(
        "API call for updating container metadata from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )
    objects = await request.json()
    if not objects:
        raise aiohttp.web.HTTPBadRequest
    batch: typing.List[typing.Any] = [
        _swift_update_object_meta_wrapper(
            request,
            name,
            [(key, value) for key, value in meta.items() if value],
        )
        for name, meta in objects
    ]
    batch = await asyncio.gather(*batch, return_exceptions=False)
    for ret in batch:
        if ret not in {202, 204}:
            raise aiohttp.web.HTTPNotFound
    return aiohttp.web.HTTPNoContent()


async def swift_update_container_metadata(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Update metadata for a container."""
    if "objects" in request.query:
        return await swift_batch_update_object_metadata(request)
    session = await aiohttp_session.get_session(request)
    client = request.app["api_client"]
    request.app["Log"].info(
        "API call for updating container metadata from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )
    project = request.match_info["project"]
    container = request.match_info["container"]
    meta = await request.json()
    meta = {f"X-Container-Meta-{k}": v for k, v in meta.items()}
    headers = {
        "X-Auth-Token": session["projects"][project]["token"],
    }
    headers.update(meta)
    async with client.post(
        f"{session['projects'][project]['endpoint']}/{container}",
        headers=headers,
    ) as ret:
        return aiohttp.web.Response(status=ret.status)


async def swift_get_project_metadata(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Get the bare minimum required project metadata from Openstack."""
    session = await aiohttp_session.get_session(request)
    client = request.app["api_client"]
    project = request.match_info["project"]
    request.app["Log"].info(
        f"Api call for project metadata check from {request.remote}, sess: {session}"
    )

    async with client.head(
        session["projects"][project]["endpoint"],
        headers={
            "X-Auth-Token": session["projects"][project]["token"],
        },
    ) as ret:
        # Empty projects return 200, otherwise 204
        if ret.status not in {200, 204}:
            raise aiohttp.web.HTTPUnauthorized(
                reason="Project is not valid for Object Storage"
            )
        return aiohttp.web.json_response(
            {
                "Account": project,
                "Containers": ret.headers["X-Account-Container-Count"],
                "Objects": ret.headers["X-Account-Object-Count"],
                "Bytes": ret.headers["X-Account-Bytes-Used"],
            }
        )


async def get_shared_container_address(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Get the project specific object storage address."""
    session = await aiohttp_session.get_session(request)
    project = request.match_info["project"]
    request.app["Log"].info(
        "API call for project specific storage from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )
    return aiohttp.web.json_response(session["projects"][project]["endpoint"])


async def _swift_get_container_acl_wrapper(
    request: aiohttp.web.Request,
    container: str,
) -> typing.Tuple[str, typing.Dict[str, typing.Any]]:
    """Return container access control headers."""
    session = await aiohttp_session.get_session(request)
    client = request.app["api_client"]
    project = request.match_info["project"]

    async with client.head(
        f"{session['projects'][project]['endpoint']}/{container}",
        headers={
            "X-Auth-Token": session["projects"][project]["token"],
        },
    ) as ret:
        acl = {}
        if "X-Container-Read" in ret.headers:
            r_meta = ret.headers["X-Container-Read"]
            # Filter non-keystone ACL information out as unnecessary
            r_meta = r_meta.replace(".r:*", "").replace(".rlistings", "")
            r_meta = re.sub(
                ",,",
                "",
                r_meta,
            )
            r_meta = r_meta.lstrip(",").rstrip(",").split(",")
            try:
                acl = {k: {"read": v} for k, v in [i.split(":") for i in r_meta]}
            except ValueError:
                acl = {}
        if "X-Container-Write" in ret.headers:
            # No need for write ACL filtering as it's project scope only
            w_acl = {
                k: {"write": v}
                for k, v in [
                    i.split(":") for i in ret.headers["X-Container-Write"].split(",")
                ]
            }
            for k, v in w_acl.items():
                try:
                    acl[k].update(v)
                except KeyError:
                    acl[k] = v
    return (container, acl)


async def get_access_control_metadata(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Fetch a compilation of ACL information for sharing discovery."""
    session = await aiohttp_session.get_session(request)
    request.app["Log"].info(
        "API call for project ACL info from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )
    client = request.app["api_client"]
    project = request.match_info["project"]

    containers: typing.List[typing.Dict[str, typing.Any]] = []
    while True:
        params = {
            "limit": 10000,
            "format": "json",
        }
        if len(containers) > 0:
            params["marker"] = containers[-1]["name"]
        async with client.get(
            f"{session['projects'][project]['endpoint']}",
            params=params,
            headers={
                "X-Auth-Token": session["projects"][project]["token"],
            },
        ) as ret:
            if ret.status == 204:
                break
            page = await ret.json()
            containers = containers + page
            # If no items are returned, we've reached the end
            if not len(page) > 0:
                break
    tasks = [
        _swift_get_container_acl_wrapper(request, container["name"])
        for container in containers
    ]
    ret = await asyncio.gather(*tasks)
    return aiohttp.web.json_response(
        {
            "address": session["projects"][project]["endpoint"],
            "access": dict(
                filter(
                    lambda i: len(i[1]) > 0,
                    ret,
                )
            ),
        }
    )


async def remove_project_container_acl(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Remove access from a project in container acl."""
    session = await aiohttp_session.get_session(request)
    request.app["Log"].info(
        "API call to remove container ACL from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )
    client = request.app["api_client"]

    project = request.match_info["project"]
    container = request.match_info["container"]
    receiver = request.match_info["receiver"]
    headers: typing.Dict[str, typing.Any] = {
        "X-Auth-Token": session["projects"][project]["token"],
    }
    async with client.head(
        f"{session['projects'][project]['endpoint']}/{container}",
        headers=headers,
    ) as ret:
        if "X-Container-Read" in ret.headers:
            headers["X-Container-Read"] = (
                ret.headers["X-Container-Read"]
                .replace(f"{receiver}:*", "")
                .replace(",,", ",")
                .rstrip(",")
            )
        if "X-Container-Write" in ret.headers:
            headers["X-Container-Write"] = (
                ret.headers["X-Container-Write"]
                .replace(f"{receiver}:*", "")
                .replace(",,", ",")
                .rstrip(",")
            )
    async with client.post(
        f"{session['projects'][project]['endpoint']}/{container}",
        headers=headers,
    ) as ret:
        if ret.status == 204:
            return aiohttp.web.Response(status=200)
        else:
            raise aiohttp.web.HTTPNotFound()


async def remove_container_acl(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Remove all allowed projects from container acl."""
    session = await aiohttp_session.get_session(request)
    request.app["Log"].info(
        "API call to remove projects fom container ACL from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )
    client = request.app["api_client"]
    project = request.match_info["project"]
    container = request.match_info["container"]

    async with client.post(
        f"{session['projects'][project]['endpoint']}/{container}",
        headers={
            "X-Auth-Token": session["projects"][project]["token"],
            "X-Container-Read": "",
            "X-Container-Write": "",
        },
    ) as ret:
        if ret.status == 204:
            return aiohttp.web.Response(status=200)
        else:
            raise aiohttp.web.HTTPNotFound()


async def add_project_container_acl(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Add access for a project in container acl."""
    session = await aiohttp_session.get_session(request)
    request.app["Log"].info(
        "API call to add access for project in container from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )
    client = request.app["api_client"]
    project = request.match_info["project"]
    container = request.match_info["container"]
    receivers = request.query["projects"].split(",")

    headers = {
        "X-Auth-Token": session["projects"][project]["token"],
    }

    read_acl = ""
    write_acl = ""
    async with client.head(
        f"{session['projects'][project]['endpoint']}/{container}",
        headers=headers,
    ) as ret:
        if "X-Container-Read" in ret.headers:
            read_acl = ret.headers["X-Container-Read"]
        if "X-Container-Write" in ret.headers:
            write_acl = ret.headers["X-Container-Write"]
    if "r" in request.query["rights"]:
        for receiver in receivers:
            read_acl += f",{receiver}:*"
        read_acl = read_acl.replace(",,", ",").lstrip(",")
    if "w" in request.query["rights"]:
        for receiver in receivers:
            write_acl += f",{receiver}:*"
        write_acl = write_acl.replace(",,", ",").lstrip(",")

    headers["X-Container-Read"] = read_acl
    headers["X-Container-Write"] = write_acl
    async with client.post(
        f"{session['projects'][project]['endpoint']}/{container}",
        headers=headers,
    ) as ret:
        if ret.status == 204:
            return aiohttp.web.Response(status=201)
        else:
            raise aiohttp.web.HTTPNotFound


async def swift_download_shared_object(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Point a user to the shared download runner."""
    session = await aiohttp_session.get_session(request)
    request.app["Log"].info(
        "API call for shared download runner "
        f"from {request.remote}, sess: {session} :: {time.ctime()}"
    )

    project = ""
    if "project" in request.query:
        project = request.query["project"]

    path = (
        f"/{request.match_info['project']}/"
        + f"{request.match_info['container']}/"
        + request.match_info["object"]
    )
    runner_id = await open_upload_runner_session(request, project=project)
    signature = await sign(3600, path)
    path += (
        f"?session={runner_id}"
        + f"&signature={signature['signature']}"
        + f"&valid={signature['valid']}"
    )
    return aiohttp.web.Response(
        status=303,
        headers={
            "Location": f"{setd['upload_external_endpoint']}{path}",
        },
    )


async def swift_download_container(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Point a user to the container download runner."""
    session = await aiohttp_session.get_session(request)
    request.app["Log"].info(
        "API call for container download runner from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )

    project = ""
    if "project" in request.query:
        project = request.query["project"]

    path = f"/{request.match_info['project']}/" + f"{request.match_info['container']}"
    runner_id = await open_upload_runner_session(request, project=project)
    signature = await sign(3600, path)
    path += (
        f"?session={runner_id}"
        + f"&signature={signature['signature']}"
        + f"&valid={signature['valid']}"
    )
    return aiohttp.web.Response(
        status=303,
        headers={
            "Location": f"{setd['upload_external_endpoint']}{path}",
        },
    )


async def swift_replicate_container(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Point the user to container replication endpoint."""
    session = await aiohttp_session.get_session(request)
    request.app["Log"].info(
        "API call for replication endpoint from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )
    runner_id = await open_upload_runner_session(request)
    path = f"/{request.match_info['project']}/{request.match_info['container']}"
    signature = await sign(3600, path)
    path += (
        f"?session={runner_id}"
        + f"&signature={signature['signature']}"
        + f"&valid={signature['valid']}"
    )
    for i in request.query.keys():
        path += f"&{i}={request.query[i]}"
    return aiohttp.web.Response(
        status=307,
        headers={
            "Location": f"{setd['upload_external_endpoint']}{path}",
        },
    )


async def get_upload_session(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Return a pre-signed upload runner session for upload target."""
    session = await aiohttp_session.get_session(request)
    request.app["Log"].info(
        "API call for object upload runner info request from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )
    project = ""
    if "project" in request.query:
        project = request.query["project"]
    runner_id = await open_upload_runner_session(request, project=project)
    path = f"/{request.match_info['project']}/{request.match_info['container']}"
    signature = await sign(3600, path)
    return aiohttp.web.json_response(
        {
            "id": runner_id,
            "url": f"{setd['upload_external_endpoint']}{path}",
            "host": setd["upload_external_endpoint"],
            "signature": signature,
        }
    )


async def get_crypted_upload_session(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Return a pre-signed upload runner session for upload target."""
    session = await aiohttp_session.get_session(request)
    request.app["Log"].info(
        "API call for object upload runner info request from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )
    project = ""
    if "project" in request.query:
        project = request.query["project"]
    runner_id = await open_upload_runner_session(request, project=project)
    path = (
        f"/cryptic/{request.match_info['project']}/{request.match_info['container']}"
        + f"/{request.match_info['object_name']}"
    )
    signature = await sign(3600, path)
    ws_path = (
        f"/cryptic/{request.match_info['project']}/{request.match_info['container']}"
        + f"/{request.match_info['object_name']}"
    )
    ws_sign_path = (
        f"/cryptic/{request.match_info['project']}/{request.match_info['container']}"
        + f"/{request.match_info['object_name']}"
    )
    ws_signature = await sign(3600, ws_sign_path)
    return aiohttp.web.json_response(
        {
            "id": runner_id,
            "url": f"{setd['upload_external_endpoint']}{path}",
            "wsurl": f"{setd['upload_external_endpoint']}{ws_path}".replace(
                "https", "wss"
            ),
            "host": setd["upload_external_endpoint"],
            "signature": signature,
            "wssignature": ws_signature,
        }
    )


async def close_upload_session(
    request: aiohttp.web.Request,
    project: str = "",
) -> aiohttp.web.Response:
    """Close the upload session opened for the token."""
    session = await aiohttp_session.get_session(request)
    status = 204
    if not project:
        project = request.match_info["project"]
    if "runner" in session["projects"][project]:
        runner = session["projects"][project]["runner"]
        client = request.app["api_client"]
        path = f"{setd['upload_internal_endpoint']}/{project}"
        signature = await sign(3600, f"/{project}")
        async with client.delete(
            path,
            cookies={"RUNNER_SESSION_ID": runner},
            params=signature,
            ssl=ssl_context,
        ) as resp:
            status = resp.status
        session["projects"][project].pop("runner")
        session.changed()
    return aiohttp.web.Response(status=status)
