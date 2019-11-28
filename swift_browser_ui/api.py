"""Project functions for handling API requests from front-end."""

import time
import os
import hashlib
import typing

import aiohttp.web
from swiftclient.service import SwiftError
from swiftclient.service import SwiftService  # for type hints
from swiftclient.utils import generate_temp_url

from ._convenience import api_check, initiate_os_service


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
        cont = []
        list(map(lambda i: cont.extend(i['listing']),
                 request.app['Creds'][session]['ST_conn'].list()))
        # for a bucket with no objects
        if not cont:
            # return empty object
            raise aiohttp.web.HTTPNotFound()
        return aiohttp.web.json_response(cont)

    except SwiftError:
        raise aiohttp.web.HTTPNotFound()


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

        obj = []
        list(map(lambda i: obj.extend(i['listing']),
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

        obj = []
        list(map(lambda i: obj.extend(i["listing"]),
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
    stats = serv.stat()

    # Check for the existence of the key headers
    acc_meta_hdr = stats['headers']
    if 'x-account-meta-temp-url-key' in acc_meta_hdr.keys():
        temp_url_key = acc_meta_hdr['x-account-meta-temp-url-key']
    elif 'x-acccount-meta-temp-url-key-2' in acc_meta_hdr.keys():
        temp_url_key = acc_meta_hdr['x-account-meta-temp-url-key-2']
    # If the key headers don't exist, assume that the key has to be created by
    # the service
    else:
        # The hash only provides random data for the key, it doesn't have to
        # be cryptographically secure.
        temp_url_key = hashlib.md5(os.urandom(128)).hexdigest()  # nosec
        # This service will use the X-Account-Meta-Temp-URL-Key-2 header for
        # its own key storage, if no existing keys are provided.
        meta_options = {
            "meta": ["Temp-URL-Key-2:{0}".format(
                temp_url_key
            )]
        }
        retval = serv.post(
            options=meta_options
        )
        if not retval['success']:
            raise aiohttp.web.HTTPServerError()
        request.app['Log'].info(
            "Created a temp url key for account {0} Key:{1} :: {2}".format(
                stats['items'][0][1], temp_url_key, time.ctime()
            )
        )
    request.app['Log'].debug(
        "Using {0} as temporary URL key :: {1}".format(
            temp_url_key, time.ctime()
        )
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
    path = '%s/%s/%s' % (path_begin, container, object_key)

    dloadurl = (host +
                generate_temp_url(path, lifetime, temp_url_key, 'GET'))

    response = aiohttp.web.Response(
        status=302,
    )
    response.headers['Location'] = dloadurl
    return response


async def get_object_metadata(
        conn: SwiftService,
        meta_cont: str,
        meta_obj: str
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


list_buckets = swift_list_buckets
list_objects = swift_list_objects
download_object = swift_download_object
