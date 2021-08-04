"""Project functions for handling API requests from front-end."""

import time
import typing

import aiohttp.web
from swiftclient.exceptions import ClientException
from swiftclient.service import SwiftError
from swiftclient.service import SwiftService, get_conn  # for type hints
from swiftclient.utils import generate_temp_url

from swift_browser_ui.ui._convenience import (
    api_check,
    initiate_os_service,
    get_tempurl_key,
    open_upload_runner_session,
    sign,
)
from swift_browser_ui.ui.settings import setd


async def get_os_user(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Fetch the session owning OS user."""
    session = api_check(request)
    request.app["Log"].info(
        f"API call for username from {request.remote}, sess: {session} :: {time.ctime()}"
    )

    userid = request.app["Sessions"][session]["OS_sess"].get_user_id()

    return aiohttp.web.json_response(userid)


def _unpack(
    item: dict, cont: typing.List[dict], request: aiohttp.web.Request
) -> typing.Any:
    """Unpack container list if the request was successful."""
    if item["success"]:
        tenant = (
            f"Container: {item['container']}"
            if item["container"]
            else "No tenant specified, working with container"
        )
        request.app["Log"].info(f"{tenant} list unpacked successfully.")
        return cont.extend(item["listing"])
    else:
        request.app["Log"].error(item["error"])


async def swift_list_buckets(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """
    Return necessary information listing swift buckets in a project.

    The function strips out e.g. the information on a success, since that's
    not necessary in this case and returns a JSON response containing all the
    necessary data.
    """
    cont: typing.List[dict] = []
    try:
        session = api_check(request)
        request.app["Log"].info(
            "API call for list buckets from "
            f"{request.remote}, sess: {session} :: {time.ctime()}"
        )
        # The maximum amount of buckets / containers is measured in thousands,
        # so it's not necessary to think twice about iterating over the whole
        # response at once
        serv = request.app["Sessions"][session]["ST_conn"].list()
        [_unpack(i, cont, request) for i in serv]
        # for a bucket with no objects
        if not cont:
            # return empty object
            request.app["Log"].debug("Empty container list.")
            raise aiohttp.web.HTTPNotFound()
        return aiohttp.web.json_response(cont)
    except SwiftError:
        request.app["Log"].error("SwiftError occured return empty container list.")
        raise aiohttp.web.HTTPNotFound()
    except KeyError:
        # listing is missing; possible broken swift auth
        request.app["Log"].error("listing is missing; possible broken swift auth.")
        return aiohttp.web.json_response(cont)


async def swift_create_container(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Create a new container according to the name specified."""
    try:
        session = api_check(request)
        request.app["Log"].info(
            f"API call for container creation from {request.remote}, sess {session}"
        )
        # Shamelessly use private methods from SwiftService to avoid writing
        # own implementation
        res = request.app["Sessions"][session]["ST_conn"]._create_container_job(
            get_conn(request.app["Sessions"][session]["ST_conn"]._options),
            request.match_info["container"],
        )
    except (SwiftError, ClientException):
        request.app["Log"].error("Container creation failed.")
        raise aiohttp.web.HTTPServerError(reason="Container creation failure")
    # Return HTTPCreated upon a successful creation
    if res["success"]:
        return aiohttp.web.Response(status=201)
    if res["error"].http_status == 409:
        request.app["Log"].info(res["error"].http_status)
        raise aiohttp.web.HTTPConflict(reason="Container name in use")
    raise aiohttp.web.HTTPServerError(reason=res["error"].msg)


async def swift_delete_container(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Delete an empty container."""
    if "objects" in request.query:
        return await swift_delete_objects(request)
    try:
        session = api_check(request)
        request.app["Log"].info(
            f"API call for container deletion from {request.remote}, sess {session}"
        )
        res = request.app["Sessions"][session]["ST_conn"].delete(
            container=request.match_info["container"]
        )
    except (SwiftError, ClientException):
        request.app["Log"].error("Container deletion failed.")
        raise aiohttp.web.HTTPServerError(reason="Container deletion failure")
    for item in res:
        if not item["success"]:
            raise aiohttp.web.HTTPServerError(reason=item["error"])
    return aiohttp.web.Response(status=204)


async def swift_delete_objects(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Delete an object."""
    try:
        session = api_check(request)
        request.app["Log"].info(
            f"API call for object deletion from {request.remote}, sess {session}"
        )
        options: typing.Dict[str, typing.Any] = {
            "yes_all": False,
            "leave_segments": False,
            "version_id": None,
            "prefix": request.query["prefix"] if "prefix" in request.query else None,
            "versions": False,
            "header": [],
        }
        res = request.app["Sessions"][session]["ST_conn"].delete(
            container=request.match_info["container"],
            objects=request.query["objects"].split(","),
            options=options,
        )
    except (SwiftError, ClientException):
        request.app["Log"].error("Object deletion failed.")
        raise aiohttp.web.HTTPServerError(reason="Object deletion failure")
    for item in res:
        if not item["success"]:
            raise aiohttp.web.HTTPServerError(reason=item["error"])
    return aiohttp.web.Response(status=204)


async def swift_list_objects(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """
    List objects in a given bucket or container.

    The function strips out e.g. the information on a success, since that's
    not necessary in this case and returns a JSON response containing all the
    necessasry data.
    """
    obj: typing.List[dict] = []
    try:
        session = api_check(request)
        request.app["Log"].info(
            "API call for list objects from "
            f"{request.remote}, sess: {session} :: {time.ctime()}"
        )

        serv = request.app["Sessions"][session]["ST_conn"].list(
            container=request.query["bucket"]
        )
        [_unpack(i, obj, request) for i in serv]
        if not obj:
            request.app["Log"].debug("Empty container object list.")
            raise aiohttp.web.HTTPNotFound()

        # Some tools leave unicode nulls to e.g. file hashes. These must be
        # replaced as they break the utf-8 text rendering in browsers for some
        # reason.
        for i in obj:
            i["hash"] = i["hash"].replace("\u0000", "")
            if "content_type" not in i.keys():
                i["content_type"] = "binary/octet-stream"
            else:
                i["content_type"] = i["content_type"].replace("\u0000", "")

        return aiohttp.web.json_response(obj)
    except SwiftError:
        request.app["Log"].error("SwiftError occured return empty container list.")
        return aiohttp.web.json_response(obj)
    except KeyError:
        # listing is missing; possible broken swift auth
        request.app["Log"].error("listing is missing; possible broken swift auth.")
        return aiohttp.web.json_response(obj)


async def swift_list_shared_objects(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """
    List objects in a shared container.

    The function strips out e.g. the information on a success, since that's
    not necessary in this case and returns a JSON response containing all the
    necessary data.
    """
    obj: typing.List[dict] = []
    try:
        session = api_check(request)
        request.app["Log"].info(
            "API call for list shared objects from "
            f"{request.remote}, sess: {session} :: {time.ctime()}"
        )

        # Establish a temporary Openstack SwiftService connection
        tmp_serv = initiate_os_service(
            request.app["Sessions"][session]["OS_sess"], url=request.query["storageurl"]
        )
        serv = tmp_serv.list(container=request.query["container"])
        [_unpack(i, obj, request) for i in serv]

        if not obj:
            request.app["Log"].debug("Empty list in shared container.")
            raise aiohttp.web.HTTPNotFound()

        # Some tools leave unicode nulls to e.g. file hashes. These must be
        # replaced as they break the utf-8 text rendering in browsers for some
        # reason.
        for i in obj:
            i["hash"] = i["hash"].replace("\u0000", "")
            if "content_type" not in i.keys():
                i["content_type"] = "binary/octet-stream"
            else:
                i["content_type"] = i["content_type"].replace("\u0000", "")

        return aiohttp.web.json_response(obj)

    except SwiftError:
        request.app["Log"].error("SwiftError occured return empty container list.")
        return aiohttp.web.json_response(obj)
    except ClientException as e:
        request.app["Log"].error(e.msg)
        return aiohttp.web.json_response(obj)
    except KeyError:
        # listing is missing; possible broken swift auth
        request.app["Log"].error("listing is missing; possible broken swift auth.")
        return aiohttp.web.json_response(obj)


async def swift_download_object(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Point a user to a temporary pre-signed download URL."""
    session = api_check(request)
    request.app["Log"].info(
        "API call for download object from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )

    serv = request.app["Sessions"][session]["ST_conn"]
    sess = request.app["Sessions"][session]["OS_sess"]

    temp_url_key = await get_tempurl_key(serv)
    request.app["Log"].debug(f"Using {temp_url_key} as temporary URL key")
    # Generate temporary URL
    host = sess.get_endpoint(service_type="object-store").split("/v1")[0]
    path_begin = sess.get_endpoint(service_type="object-store").replace(host, "")
    request.app["Log"].debug(f"Using {host} as host and {path_begin} as path start.")
    container = request.query["bucket"]
    object_key = request.query["objkey"]
    lifetime = 60 * 15
    # In the path creation, the stats['items'][0][1] is the tenant id from
    # server statistics, the order should be significant, so this shouldn't
    # be a problem
    path = f"{path_begin}/{container}/{object_key}"

    dloadurl = host + generate_temp_url(path, lifetime, temp_url_key, "GET")

    response = aiohttp.web.Response(
        status=302,
    )
    response.headers["Location"] = dloadurl
    return response


async def swift_download_shared_object(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Point a user to the shared download runner."""
    session = api_check(request)
    request.app["Log"].info(
        "API call for shared download runner "
        f"from {request.remote}, sess: {session} :: {time.ctime()}"
    )

    project: str = request.match_info["project"]
    container: str = request.match_info["container"]
    object_name: str = request.match_info["object"]

    runner_id = await open_upload_runner_session(
        session,
        request,
        request.app["Sessions"][session]["active_project"]["id"],
        request.app["Sessions"][session]["Token"],
    )
    request.app["Sessions"][session]["runner"] = runner_id

    path = f"/{project}/{container}/{object_name}"
    signature = await sign(3600, path)

    path += f"?session={runner_id}"
    path += f"&signature={signature['signature']}"
    path += f"&valid={signature['valid_until']}"

    resp = aiohttp.web.Response(status=303)
    resp.headers["Location"] = f"{setd['upload_external_endpoint']}{path}"

    return resp


async def swift_download_container(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Point a user to the container download runner."""
    session = api_check(request)
    request.app["Log"].info(
        "API call for container download runner from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )

    project: str = request.match_info["project"]
    container: str = request.match_info["container"]

    runner_id = await open_upload_runner_session(
        session,
        request,
        request.app["Sessions"][session]["active_project"]["id"],
        request.app["Sessions"][session]["Token"],
    )
    request.app["Sessions"][session]["runner"] = runner_id

    path = f"/{project}/{container}"
    signature = await sign(3600, path)

    path += f"?session={runner_id}"
    path += f"&signature={signature['signature']}"
    path += f"&valid={signature['valid_until']}"

    resp = aiohttp.web.Response(status=303)
    resp.headers["Location"] = f"{setd['upload_external_endpoint']}{path}"

    return resp


async def swift_upload_object_chunk(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Point a user to the object upload runner."""
    session = api_check(request)
    request.app["Log"].info(
        "API call for object upload runner from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )

    project: str = request.match_info["project"]
    container: str = request.match_info["container"]

    runner_id = await open_upload_runner_session(
        session,
        request,
        request.app["Sessions"][session]["active_project"]["id"],
        request.app["Sessions"][session]["Token"],
    )

    path = f"/{project}/{container}"
    signature = await sign(3600, path)

    path += f"?session={runner_id}"
    path += f"&signature={signature['signature']}"
    path += f"&valid={signature['valid_until']}"

    resp = aiohttp.web.Response(status=307)
    resp.headers["Location"] = f"{setd['upload_external_endpoint']}{path}"

    request.app["Log"].info(f"redirecting {session} to {resp.headers['Location']}")

    return resp


async def swift_replicate_container(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Point the user to container replication endpoint."""
    session = api_check(request)
    request.app["Log"].info(
        "API call for replication endpoint from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )

    project: str = request.match_info["project"]
    container: str = request.match_info["container"]

    runner_id = await open_upload_runner_session(
        session,
        request,
        request.app["Sessions"][session]["active_project"]["id"],
        request.app["Sessions"][session]["Token"],
    )

    path = f"/{project}/{container}"
    signature = await sign(3600, path)

    path += f"?session={runner_id}"
    path += f"&signature={signature['signature']}"
    path += f"&valid={signature['valid_until']}"

    for i in request.query.keys():
        path += f"&{i}={request.query[i]}"

    resp = aiohttp.web.Response(status=307)
    resp.headers["Location"] = f"{setd['upload_external_endpoint']}{path}"

    return resp


async def swift_check_object_chunk(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Point check for object existence to the upload runner."""
    session = api_check(request)
    request.app["Log"].info(
        "API call to check object existence in upload runner from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )

    project: str = request.match_info["project"]
    container: str = request.match_info["container"]

    runner_id = await open_upload_runner_session(
        session,
        request,
        request.app["Sessions"][session]["active_project"]["id"],
        request.app["Sessions"][session]["Token"],
    )

    path = f"/{project}/{container}"
    signature = await sign(3600, path)

    path += f"?{request.query_string}"
    path += f"&session={runner_id}"
    path += f"&signature={signature['signature']}"
    path += f"&valid={signature['valid_until']}"

    resp = aiohttp.web.Response(status=307)
    resp.headers["Location"] = f"{setd['upload_external_endpoint']}{path}"

    return resp


async def get_object_metadata(
    conn: SwiftService, meta_cont: str, meta_obj: typing.Union[typing.List[str], None]
) -> typing.List[dict]:
    """Get object metadata."""
    try:
        res = list(conn.stat(meta_cont, meta_obj))

        # Fail if an object wasn't usable
        if False in [i["success"] for i in res]:
            raise aiohttp.web.HTTPNotFound()

        # Filter for metadata not already served with the list request
        res = [
            [
                i["object"],
                dict(filter(lambda j: "x-object-meta" in j[0], i["headers"].items())),
            ]
            for i in res
        ]

        # Strip unnecessary specifcations from header names and split open s3
        # information so that it doesn't have to be done in the browser
        for i in res:
            i[1] = {k.replace("x-object-meta-", ""): v for k, v in i[1].items()}
            if "s3cmd-attrs" in i[1].keys():
                i[1]["s3cmd-attrs"] = {
                    k: v
                    for k, v in [j.split(":") for j in i[1]["s3cmd-attrs"].split("/")]
                }
        return res
    except SwiftError:
        # Fail if container wasn't found
        raise aiohttp.web.HTTPNotFound()


async def get_metadata_bucket(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Get metadata for a container."""
    session = api_check(request)
    request.app["Log"].info(
        "API cal for project listing from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )

    # Get required variables from query string
    meta_cont = (
        request.query["container"] if "container" in request.query.keys() else None
    )
    conn = request.app["Sessions"][session]["ST_conn"]
    # Get container listing if no object list was specified
    ret = conn.stat(meta_cont)

    if not ret["success"]:
        raise aiohttp.web.HTTPNotFound()

    # Strip any unnecessary information from the metadata headers
    ret["headers"] = dict(
        filter(lambda i: "x-container-meta" in i[0], ret["headers"].items())
    )
    ret["headers"] = {
        k.replace("x-container-meta-", ""): v for k, v in ret["headers"].items()
    }

    return aiohttp.web.json_response([ret["container"], ret["headers"]])


async def get_metadata_object(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Get metadata for a container or for an object."""
    session = api_check(request)
    request.app["Log"].info(
        "API cal for project listing from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )

    # Get required variables from query string
    meta_cont = (
        request.query["container"] if "container" in request.query.keys() else None
    )
    meta_obj = request.query["object"].split(",") if "object" in request.query else None

    # If no container was specified, raise an Unauthorized error – the user is
    # not meant to see the account metadata information directly since it may
    # contain sensitive data. This is not needed directly for the UI, but
    # the API is exposed for the user and thus can't expose any sensitive info
    if not meta_cont:
        request.app["Log"].error("Container not specified.")
        raise aiohttp.web.HTTPClientError()

    conn = request.app["Sessions"][session]["ST_conn"]

    # Otherwise get object listing (object listing won't need to throw an
    # exception here incase of a failure – the function handles that)
    return aiohttp.web.json_response(await get_object_metadata(conn, meta_cont, meta_obj))


async def get_project_metadata(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Get the bare minimum required project metadata from OS."""
    # The project metadata needs to be filtered for sensitive information, as
    # it contains e.g. temporary URL keys. These keys can be used to pull any
    # object from the object storage, and thus shouldn't be provided for the
    # user.
    ret = dict()
    try:
        session = api_check(request)
        request.app["Log"].info(
            f"Api call for project metadata check from {request.remote}, sess: {session}"
        )

        conn = request.app["Sessions"][session]["ST_conn"]

        # Get the account metadata listing
        stat = dict(conn.stat()["items"])
        ret = {
            "Account": stat["Account"],
            "Containers": stat["Containers"],
            "Objects": stat["Objects"],
            "Bytes": stat["Bytes"],
        }
        return aiohttp.web.json_response(ret)
    except SwiftError:
        request.app["Log"].error("SwiftError occured.")
        return aiohttp.web.json_response(ret)
    except ClientException as e:
        request.app["Log"].error(e.msg)
        return aiohttp.web.json_response(ret)
    except KeyError:
        request.app["Log"].error(
            "items is missing; possible swift storage is not authorised for project."
        )
        return aiohttp.web.json_response(ret)


async def os_list_projects(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Fetch the projects available for the open session."""
    session = api_check(request)
    request.app["Log"].info(
        "API call for project listing from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )

    # Return the projects available for the session
    return aiohttp.web.json_response(
        request.app["Sessions"][session]["Avail"]["projects"]
    )


async def get_os_active_project(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Fetch the project currently displayed to the session."""
    session = api_check(request)
    request.app["Log"].info(
        "API call for current project from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )

    return aiohttp.web.json_response(request.app["Sessions"][session]["active_project"])


async def get_shared_container_address(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Get the project specific object storage address."""
    session = api_check(request)
    request.app["Log"].info(
        "API call for project specific storage from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )
    sess = request.app["Sessions"][session]["OS_sess"]

    host = sess.get_endpoint(service_type="object-store")
    return aiohttp.web.json_response(host)


async def get_access_control_metadata(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Fetch a compilation of ACL information for sharing discovery."""
    session = api_check(request)
    request.app["Log"].info(
        "API call for project ACL info from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )

    serv = request.app["Sessions"][session]["ST_conn"]
    sess = request.app["Sessions"][session]["OS_sess"]

    # Get a list of containers
    containers: typing.List[dict] = []
    [_unpack(i, containers, request) for i in serv.list()]

    host = sess.get_endpoint(service_type="object-store")

    # Get a list of ACL information
    acls = {}
    for c in containers:
        acl = {}

        c_meta = dict(serv.stat(container=c["name"])["items"])
        # Create dictionaries keyed with projects that have access
        if c_meta["Read ACL"]:
            r_meta = c_meta["Read ACL"]
            # Filter non-keystone ACL information out as unnecessary
            r_meta = r_meta.replace(".r:*", "").replace(".rlistings", "")
            # Handle residual double commas possibly left over
            r_meta = r_meta.replace(",,", ",")
            # Handle leading and trailing commas possibly left over
            r_meta = r_meta.lstrip(",").rstrip(",").split(",")
            try:
                acl = {k: {"read": v} for k, v in [i.split(":") for i in r_meta]}
            except ValueError:
                acl = {}
        if c_meta["Write ACL"]:
            # No need for Write ACL filtering as it's project scope only
            write_acl = {
                k: {"write": v}
                for k, v in [i.split(":") for i in c_meta["Write ACL"].split(",")]
            }

            for k, v in write_acl.items():
                try:
                    acl[k].update(v)
                except KeyError:
                    acl[k] = v

        if acl:
            acls[c["name"]] = acl

    return aiohttp.web.json_response(
        {
            "address": host,
            "access": acls,
        }
    )


async def remove_project_container_acl(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Remove access from a project in container acl."""
    session = api_check(request)
    request.app["Log"].info(
        "API call to remove container ACL from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )

    serv = request.app["Sessions"][session]["ST_conn"]

    container = request.match_info["container"]
    project = request.query["project"]

    meta_headers = dict(serv.stat(container=container)["items"])

    read_acl = meta_headers["Read ACL"]
    write_acl = meta_headers["Write ACL"]

    # Remove specific project form both ACLs
    read_acl = read_acl.replace(f"{project}:*", "").replace(",,", ",").rstrip(",")
    read_acl = read_acl.replace(f"{project}:*", "").replace(",,", ",").rstrip(",")

    meta_options = {
        "read_acl": read_acl,
        "write_acl": write_acl,
    }

    serv.post(container=container, options=meta_options)

    return aiohttp.web.Response(status=200)


async def remove_container_acl(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """Remove all allowed projects from container acl."""
    # Since both removes are handled with the same endpoint, try the project
    # specific one first
    try:
        return await remove_project_container_acl(request)
    except KeyError:
        session = api_check(request)
        request.app["Log"].info(
            "API call to remove projects fom container ACL from "
            f"{request.remote}, sess: {session} :: {time.ctime()}"
        )

        serv = request.app["Sessions"][session]["ST_conn"]

        container = request.match_info["container"]

        meta_options = {
            "read_acl": "",
            "write_acl": "",
        }

        serv.post(container=container, options=meta_options)

        return aiohttp.web.Response(status=200)


async def add_project_container_acl(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    """Add access for a project in container acl."""
    session = api_check(request)
    request.app["Log"].info(
        "API call to add access for project in container from "
        f"{request.remote}, sess: {session} :: {time.ctime()}"
    )
    serv = request.app["Sessions"][session]["ST_conn"]

    container = request.match_info["container"]
    projects = request.query["projects"].split(",")
    request.app["Log"].debug(f"Requested container {container} and projects {projects}.")
    meta_headers = dict(serv.stat(container=container)["items"])

    read_acl = meta_headers["Read ACL"]
    write_acl = meta_headers["Write ACL"]
    # Concatenate the new project to the ACL string
    if "r" in request.query["rights"]:
        for project in projects:
            read_acl += f",{project}:*"
        read_acl = read_acl.replace(",,", ",").lstrip(",")
    if "w" in request.query["rights"]:
        for project in projects:
            write_acl += f",{project}:*"
        read_acl = read_acl.replace(",,", ",").lstrip(",")

    meta_options = {
        "read_acl": read_acl,
        "write_acl": write_acl,
    }

    serv.post(container=container, options=meta_options)

    return aiohttp.web.Response(status=201)
