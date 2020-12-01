"""Project functions for handling API requests from front-end."""

import time
import typing

import aiohttp.web
from swiftclient.exceptions import ClientException
from swiftclient.service import SwiftError
from swiftclient.service import SwiftService, get_conn  # for type hints
from swiftclient.utils import generate_temp_url

from ._convenience import api_check, initiate_os_service, get_tempurl_key
from ._convenience import open_upload_runner_session, sign

from .settings import setd


async def get_os_user(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Fetch the session owning OS user."""
    session = api_check(request)
    request.app['Log'].info(
        'API call for username from {0}, sess: {1} :: {2}'.format(
            request.remote,
            session,
            time.ctime(),
        )
    )

    userid = request.app['Creds'][session]['OS_sess'].get_user_id()

    return aiohttp.web.json_response(
        userid
    )


async def swift_list_buckets(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """
    Return necessary information listing swift buckets in a project.

    The function strips out e.g. the information on a success, since that's
    not necessary in this case and returns a JSON response containing all the
    necessary data.
    """
    try:
        session = api_check(request)
        request.app['Log'].info(
            'API call for list buckets from {0}, sess: {1} :: {2}'.format(
                request.remote,
                session,
                time.ctime(),
            )
        )

        # The maximum amount of buckets / containers is measured in thousands,
        # so it's not necessary to think twice about iterating over the whole
        # response at once
        cont: typing.List[dict] = []
        list(map(lambda i: cont.extend(i["listing"]),  # type: ignore
                 request.app['Creds'][session]['ST_conn'].list()))
        # for a bucket with no objects
        if not cont:
            # return empty object
            raise aiohttp.web.HTTPNotFound()
        return aiohttp.web.json_response(cont)

    except SwiftError:
        raise aiohttp.web.HTTPNotFound()
    except ClientException as e:
        request.app['Log'].error(e.msg)
    except KeyError:
        # listing is missing; possible broken swift auth
        return aiohttp.web.json_response([])


async def swift_create_container(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Create a new container according to the name specified."""
    try:
        session = api_check(request)
        request.app['Log'].info(
            'API call for bucket creation from %s, sess %s',
            request.remote,
            session
        )
        # Shamelessly use private methods from SwiftService to avoid writing
        # own implementation
        res = request.app['Creds'][session]['ST_conn']._create_container_job(
            get_conn(request.app['Creds'][session]['ST_conn']._options),
            request.match_info["container"]
        )
    except (SwiftError, ClientException):
        raise aiohttp.web.HTTPServerError(
            reason="Container creation failure"
        )
    # Return HTTPCreated upon a successful creation
    if res["success"]:
        return aiohttp.web.Response(status=201)
    raise aiohttp.web.HTTPClientError(
        reason=res["error"]
    )


async def swift_list_objects(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """
    List objects in a given bucket or container.

    The function strips out e.g. the information on a success, since that's
    not necessary in this case and returns a JSON response containing all the
    necessasry data.
    """
    try:
        session = api_check(request)
        request.app['Log'].info(
            'API call for list objects from {0}, sess: {1} :: {2}'.format(
                request.remote,
                session,
                time.ctime(),
            )
        )

        obj: typing.List[dict] = []
        list(map(lambda i: obj.extend(i['listing']),  # type: ignore
                 request.app['Creds'][session]['ST_conn'].list(
                     container=request.query['bucket'])))

        if not obj:
            raise aiohttp.web.HTTPNotFound()

        # Some tools leave unicode nulls to e.g. file hashes. These must be
        # replaced as they break the utf-8 text rendering in browsers for some
        # reason.
        for i in obj:
            i['hash'] = i['hash'].replace('\u0000', '')
            if 'content_type' not in i.keys():
                i['content_type'] = 'binary/octet-stream'
            else:
                i['content_type'] = i['content_type'].replace('\u0000', '')

        return aiohttp.web.json_response(obj)
    except SwiftError:
        return aiohttp.web.json_response([])
    except ClientException as e:
        request.app['Log'].error(e.msg)
        return aiohttp.web.json_response([])
    except KeyError:
        # listing is missing; possible broken swift auth
        return aiohttp.web.json_response([])


async def swift_list_shared_objects(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """
    List objects in a shared container.

    The function strips out e.g. the information on a success, since that's
    not necessary in this case and returns a JSON response containing all the
    necessary data.
    """
    try:
        session = api_check(request)
        request.app["Log"].info(
            "API call for list shared objects from %s, sess: %s :: %s",
            request.remote,
            session,
            time.ctime()
        )

        # Establish a temporary Openstack SwiftService connection
        tmp_serv = initiate_os_service(
            request.app["Creds"][session]["OS_sess"],
            url=request.query["storageurl"]
        )

        obj: typing.List[dict] = []
        list(map(lambda i: obj.extend(i["listing"]),  # type: ignore
                 tmp_serv.list(
                     container=request.query["container"])))
        if not obj:
            raise aiohttp.web.HTTPNotFound()

        # Some tools leave unicode nulls to e.g. file hashes. These must be
        # replaced as they break the utf-8 text rendering in browsers for some
        # reason.
        for i in obj:
            i['hash'] = i['hash'].replace('\u0000', '')
            if 'content_type' not in i.keys():
                i['content_type'] = 'binary/octet-stream'
            else:
                i['content_type'] = i['content_type'].replace('\u0000', '')

        return aiohttp.web.json_response(obj)

    except SwiftError:
        return aiohttp.web.json_response([])
    except ClientException as e:
        request.app['Log'].error(e.msg)
        return aiohttp.web.json_response([])
    except KeyError:
        # listing is missing; possible broken swift auth
        return aiohttp.web.json_response([])


async def swift_download_object(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Point a user to a temporary pre-signed download URL."""
    session = api_check(request)
    request.app['Log'].info(
        'API call for download object from {0}, sess: {1} :: {2}'.format(
            request.remote,
            session,
            time.ctime(),
        )
    )

    serv = request.app['Creds'][session]['ST_conn']
    sess = request.app['Creds'][session]['OS_sess']

    temp_url_key = await get_tempurl_key(serv)
    request.app['Log'].debug(
        "Using %s as temporary URL key", temp_url_key
    )
    # Generate temporary URL
    host = sess.get_endpoint(service_type="object-store").split('/v1')[0]
    path_begin = sess.get_endpoint(service_type="object-store").replace(
        host, ""
    )
    request.app['Log'].debug(
        "Using %s as host and %s as path start.", host, path_begin
    )
    container = request.query['bucket']
    object_key = request.query['objkey']
    lifetime = 60 * 15
    # In the path creation, the stats['items'][0][1] is the tenant id from
    # server statistics, the order should be significant, so this shouldn't
    # be a problem
    path = f'{path_begin}/{container}/{object_key}'

    dloadurl = (host +
                generate_temp_url(path, lifetime, temp_url_key, 'GET'))

    response = aiohttp.web.Response(
        status=302,
    )
    response.headers['Location'] = dloadurl
    return response


async def swift_download_shared_object(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Point a user to the shared download runner."""
    session = api_check(request)

    project: str = request.match_info['project']
    container: str = request.match_info['container']
    object_name: str = request.match_info['object']

    runner_id = await open_upload_runner_session(
        session,
        request,
        request.app['Creds'][session]['active_project']['id'],
        request.app['Creds'][session]['Token']
    )
    request.app['Creds'][session]['runner'] = runner_id

    path = f"/{project}/{container}/{object_name}"
    signature = await sign(3600, path)

    path += f"?session={runner_id}"
    path += f"&signature={signature['signature']}"
    path += f"&valid={signature['valid_until']}"

    resp = aiohttp.web.Response(status=303)
    resp.headers['Location'] = (
        f"{setd['upload_external_endpoint']}{path}"
    )

    return resp


async def swift_download_container(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Point a user to the container download runner."""
    session = api_check(request)

    project: str = request.match_info['project']
    container: str = request.match_info['container']

    runner_id = await open_upload_runner_session(
        session,
        request,
        request.app['Creds'][session]['active_project']['id'],
        request.app['Creds'][session]['Token']
    )
    request.app['Creds'][session]['runner'] = runner_id

    path = f"/{project}/{container}"
    signature = await sign(3600, path)

    path += f"?session={runner_id}"
    path += f"&signature={signature['signature']}"
    path += f"&valid={signature['valid_until']}"

    resp = aiohttp.web.Response(status=303)
    resp.headers['Location'] = (
        f"{setd['upload_external_endpoint']}{path}"
    )

    return resp


async def swift_upload_object_chunk(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Point a user to the object upload runner."""
    session = api_check(request)

    project: str = request.match_info['project']
    container: str = request.match_info['container']

    runner_id = await open_upload_runner_session(
        session,
        request,
        request.app['Creds'][session]['active_project']['id'],
        request.app['Creds'][session]['Token']
    )

    path = f"/{project}/{container}"
    signature = await sign(3600, path)

    path += f"?session={runner_id}"
    path += f"&signature={signature['signature']}"
    path += f"&valid={signature['valid_until']}"

    resp = aiohttp.web.Response(status=307)
    resp.headers['Location'] = (
        f"{setd['upload_external_endpoint']}{path}"
    )

    return resp


async def swift_replicate_container(
    request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Point the user to container replication endpoint."""
    session = api_check(request)

    project: str = request.match_info['project']
    container: str = request.match_info['container']

    runner_id = await open_upload_runner_session(
        session,
        request,
        request.app['Creds'][session]['active_project']['id'],
        request.app['Creds'][session]['Token']
    )

    path = f"/{project}/{container}"
    signature = await sign(3600, path)

    path += f"?session={runner_id}"
    path += f"&signature={signature['signature']}"
    path += f"&valid={signature['valid_until']}"

    for i in request.query.keys():
        path += f"&{i}={request.query[i]}"

    resp = aiohttp.web.Response(status=307)
    resp.headers['Location'] = (
        f"{setd['upload_external_endpoint']}{path}"
    )

    return resp


async def swift_check_object_chunk(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Point check for object existence to the upload runner."""
    session = api_check(request)

    project: str = request.match_info['project']
    container: str = request.match_info['container']

    runner_id = await open_upload_runner_session(
        session,
        request,
        request.app['Creds'][session]['active_project']['id'],
        request.app['Creds'][session]['Token']
    )

    path = f"/{project}/{container}"
    signature = await sign(3600, path)

    path += f"?{request.query_string}"
    path += f"&session={runner_id}"
    path += f"&signature={signature['signature']}"
    path += f"&valid={signature['valid_until']}"

    resp = aiohttp.web.Response(status=307)
    resp.headers['Location'] = (
        f"{setd['upload_external_endpoint']}{path}"
    )

    return resp


async def get_object_metadata(
        conn: SwiftService,
        meta_cont: str,
        meta_obj: typing.Union[typing.List[str], None]
) -> typing.List[dict]:
    """Get object metadata."""
    try:
        res = list(conn.stat(meta_cont, meta_obj))

        # Fail if an object wasn't usable
        if False in [i['success'] for i in res]:
            raise aiohttp.web.HTTPNotFound()

        # Filter for metadata not already served with the list request
        res = [
            [i['object'], dict(filter(
                lambda j: "x-object-meta" in j[0],
                i['headers'].items()
            ))] for i in res
        ]

        # Strip unnecessary specifcations from header names and split open s3
        # information so that it doesn't have to be done in the browser
        for i in res:
            i[1] = {
                k.replace("x-object-meta-", ""): v for k, v in i[1].items()
            }
            if "s3cmd-attrs" in i[1].keys():
                i[1]["s3cmd-attrs"] = {
                    k: v for k, v in [
                        j.split(":")
                        for j in i[1]["s3cmd-attrs"].split("/")
                    ]
                }
        return res
    except SwiftError:
        # Fail if container wasn't found
        raise aiohttp.web.HTTPNotFound()


async def get_metadata_bucket(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Get metadata for a container."""
    session = api_check(request)
    request.app['Log'].info(
        'API cal for project listing from {0}, sess: {1} :: {2}'.format(
            request.remote,
            session,
            time.ctime(),
        )
    )

    # Get required variables from query string
    meta_cont = (
        request.query['container']
        if 'container' in request.query.keys()
        else None
    )
    conn = request.app['Creds'][session]['ST_conn']
    # Get container listing if no object list was specified
    ret = conn.stat(meta_cont)

    if not ret['success']:
        raise aiohttp.web.HTTPNotFound()

    # Strip any unnecessary information from the metadata headers
    ret['headers'] = dict(filter(
        lambda i: "x-container-meta" in i[0],
        ret['headers'].items()
    ))
    ret['headers'] = {
        k.replace("x-container-meta-", ""): v
        for k, v in ret['headers'].items()
    }

    return aiohttp.web.json_response(
        [ret['container'], ret['headers']]
    )


async def get_metadata_object(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Get metadata for a container or for an object."""
    session = api_check(request)
    request.app['Log'].info(
        'API cal for project listing from {0}, sess: {1} :: {2}'.format(
            request.remote,
            session,
            time.ctime(),
        )
    )

    # Get required variables from query string
    meta_cont = (
        request.query['container']
        if 'container' in request.query.keys()
        else None
    )
    meta_obj = (
        request.query['object'].split(',')
        if 'object' in request.query
        else None
    )

    # If no container was specified, raise an Unauthorized error – the user is
    # not meant to see the account metadata information directly since it may
    # contain sensitive data. This is not needed directly for the UI, but
    # the API is exposed for the user and thus can't expose any sensitive info
    if not meta_cont:
        raise aiohttp.web.HTTPClientError()

    conn = request.app['Creds'][session]['ST_conn']

    # Otherwise get object listing (object listing won't need to throw an
    # exception here incase of a failure – the function handles that)
    return aiohttp.web.json_response(
        await get_object_metadata(conn, meta_cont, meta_obj)
    )


async def get_project_metadata(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Get the bare minimum required project metadata from OS."""
    # The project metadata needs to be filtered for sensitive information, as
    # it contains e.g. temporary URL keys. These keys can be used to pull any
    # object from the object storage, and thus shouldn't be provided for the
    # user.
    session = api_check(request)
    request.app['Log'].info(
        'Api call for project metadata check from {0}, sess: {1}'.format(
            request.remote,
            session,
        )
    )

    conn = request.app['Creds'][session]['ST_conn']

    # Get the account metadata listing
    ret = dict(conn.stat()['items'])
    ret = {
        'Account': ret['Account'],
        'Containers': ret['Containers'],
        'Objects': ret['Objects'],
        'Bytes': ret['Bytes'],
    }
    return aiohttp.web.json_response(ret)


async def os_list_projects(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Fetch the projects available for the open session."""
    session = api_check(request)
    request.app['Log'].info(
        'API call for project listing from {0}, sess: {1} :: {2}'.format(
            request.remote,
            session,
            time.ctime(),
        )
    )

    # Return the projects available for the session
    return aiohttp.web.json_response(
        request.app['Creds'][session]['Avail']['projects']
    )


async def get_os_active_project(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Fetch the project currently displayed to the session."""
    session = api_check(request)
    request.app['Log'].info(
        'API call for current project from {0}, sess: {1} :: {2}'.format(
            request.remote,
            session,
            time.ctime(),
        )
    )

    return aiohttp.web.json_response(
        request.app['Creds'][session]['active_project']
    )


async def get_shared_container_address(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Get the project specific object storage address."""
    session = api_check(request)
    sess = request.app['Creds'][session]['OS_sess']

    host = sess.get_endpoint(service_type="object-store")
    return aiohttp.web.json_response(host)


async def get_access_control_metadata(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Fetch a compilation of ACL information for sharing discovery."""
    session = api_check(request)

    serv = request.app['Creds'][session]['ST_conn']
    sess = request.app['Creds'][session]['OS_sess']

    # Get a list of containers
    containers: typing.List[dict] = []
    list(map(lambda i: containers.extend(i['listing']),  # type: ignore
             serv.list()))

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
                acl = {k: {"read": v} for k, v in [
                    i.split(":") for i in r_meta
                ]}
            except ValueError:
                acl = {}
        if c_meta["Write ACL"]:
            # No need for Write ACL filtering as it's project scope only
            write_acl = {k: {"write": v} for k, v in [
                i.split(":") for i in c_meta["Write ACL"].split(",")
            ]}

            for k, v in write_acl.items():
                try:
                    acl[k].update(v)
                except KeyError:
                    acl[k] = v

        if acl:
            acls[c["name"]] = acl

    return aiohttp.web.json_response({
        "address": host,
        "access": acls,
    })


async def remove_project_container_acl(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Remove access from a project in container acl."""
    session = api_check(request)

    serv = request.app['Creds'][session]['ST_conn']

    container = request.match_info["container"]
    project = request.query["project"]

    meta_headers = dict(serv.stat(container=container)["items"])

    read_acl = meta_headers["Read ACL"]
    write_acl = meta_headers["Write ACL"]

    # Remove specific project form both ACLs
    read_acl = read_acl.replace(
        f'{project}:*', ''
    ).replace(',,', ',').rstrip(',')
    read_acl = read_acl.replace(
        f'{project}:*', ''
    ).replace(',,', ',').rstrip(',')

    meta_options = {
        "read_acl": read_acl,
        "write_acl": write_acl,
    }

    serv.post(
        container=container,
        options=meta_options
    )

    return aiohttp.web.Response(
        status=200
    )


async def remove_container_acl(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Remove all allowed projects from container acl."""
    # Since both removes are handled with the same endpoint, try the project
    # specific one first
    try:
        return await remove_project_container_acl(request)
    except KeyError:
        session = api_check(request)

        serv = request.app['Creds'][session]['ST_conn']

        container = request.match_info["container"]

        meta_options = {
            "read_acl": "",
            "write_acl": "",
        }

        serv.post(
            container=container,
            options=meta_options
        )

        return aiohttp.web.Response(
            status=200
        )


async def add_project_container_acl(
        request: aiohttp.web.Request
) -> aiohttp.web.Response:
    """Add access for a project in container acl."""
    session = api_check(request)

    serv = request.app['Creds'][session]['ST_conn']

    container = request.match_info["container"]
    projects = request.query["projects"].split(",")

    meta_headers = dict(serv.stat(container=container)["items"])

    read_acl = meta_headers["Read ACL"]
    write_acl = meta_headers["Write ACL"]
    # Concatenate the new project to the ACL string
    if "r" in request.query["rights"]:
        for project in projects:
            read_acl += f',{project}:*'
        read_acl = read_acl.replace(',,', ',').lstrip(',')
    if "w" in request.query["rights"]:
        for project in projects:
            write_acl += f',{project}:*'
        read_acl = read_acl.replace(',,', ',').lstrip(',')

    meta_options = {
        "read_acl": read_acl,
        "write_acl": write_acl,
    }

    serv.post(
        container=container,
        options=meta_options
    )

    return aiohttp.web.Response(
        status=201
    )
