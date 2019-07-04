"""Project functions for handling API requests from front-end."""

import aiohttp.web
# import boto3
import time
import os
import hashlib
from swiftclient.service import SwiftError
from swiftclient.utils import generate_temp_url

# from ._convenience import decrypt_cookie
from ._convenience import api_check
from .settings import setd


async def get_os_user(request):
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


async def swift_list_buckets(request):
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
        containers = [
            i for i in request.app['Creds'][session]['ST_conn'].list()
        ]

        # For some reason the return value is a generator object, which creates
        # a list with just a single item -> get this one item as the new value
        if len(containers) == 1:
            containers = containers[0]

            return aiohttp.web.json_response(
                containers['listing']
            )
        # TBD if this is how to implement
        # for a bucket with no objects
        elif len(containers) == 0:
            # return empty object
            return aiohttp.web.json_response()
    except SwiftError:
        return aiohttp.web.json_response([])


async def swift_list_objects(request):
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

        objects = [i for i in request.app['Creds'][session]['ST_conn'].list(
            container=request.query['bucket']  # named bucket for compatibility
        )]

        # Again, get the only item in the generated list
        if len(objects) == 1:
            objects = objects[0]
        else:
            tmp = []
            for i in objects:
                tmp = tmp + i
            objects = tmp

        ret = objects['listing']
        for i in range(0, len(ret)):
            ret[i]['hash'] = ret[i]['hash'].replace('\u0000', '')
            if 'content_type' not in ret[i].keys():
                ret[i]['content_type'] = "binary/octet-stream"
            else:
                ret[i]['content_type'] = \
                    ret[i]['content_type'].replace('\u0000', '')

        return aiohttp.web.json_response(
            ret
        )
    except SwiftError:
        return aiohttp.web.json_response([])


async def swift_download_object(request):
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
    host = setd['swift_endpoint_url']
    container = request.query['bucket']
    object_key = request.query['objkey']
    lifetime = 60 * 15
    # In the path creation, the stats['items'][0][1] is the tenant id from
    # server statistics, the order should be significant, so this shouldn't
    # be a problem
    path = '/v1/%s/%s/%s' % (stats['items'][0][1], container, object_key)

    dloadurl = (
        host +
        generate_temp_url(path, lifetime, temp_url_key, 'GET')
    )

    response = aiohttp.web.Response(
        status=302,
    )
    response.headers['Location'] = dloadurl
    return response


async def os_list_projects(request):
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


async def get_os_active_project(request):
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
