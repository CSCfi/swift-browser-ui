import aiohttp.web
# import boto3
import time
import os
import hashlib
import hmac
from swiftclient.service import SwiftError

# from ._convenience import decrypt_cookie
from ._convenience import api_check


# Toggle S3 function overloading
# SETUP_WITH_S3 = False


# async def s3_list_buckets(request):
#     """
#     The internal API call for fetching a list of buckets available for user
#     """
#     # TODO: Refactor code to store session specific s3 client to app mapping
#     try:
#         if decrypt_cookie(request) not in request.app['Sessions']:
#             raise KeyError()
#
#         s3 = boto3.client(
#             's3',
#         )
#         # Fetch the information about the user's buckets from API
#         ret = s3.list_buckets()['Buckets']
#         for i in ret:
#             # Transform the CreationDate into a user readable string, since
#             # the datetime-object is not JSON-serializeable
#             i['CreationDate'] = i['CreationDate'].ctime()
#
#         return aiohttp.web.json_response(
#             ret
#         )
#     # If can't find user session, reply with 401
#     except KeyError:
#         return aiohttp.web.Response(
#             status=401,
#             reason="No user session was found"
#         )


# async def s3_list_objects(request):
#     """
#     The internal API call for fetching a list of available objects inside
#     a specified bucket
#     """
#     try:
#         if decrypt_cookie(request) not in request.app['Sessions']:
#             raise KeyError()
#         s3 = boto3.client(
#             's3',
#         )
#         # Get all objects in the specified bucket
#         ret = s3.list_objects(
#             Bucket=request.query['bucket']
#         )['Contents']
#         for i in ret:
#             # Transform the LastModified date value into a user readable
#             # string, since the datetime-object is not JSON-serializeable
#             i['LastModified'] = i['LastModified'].ctime()
#
#         return aiohttp.web.json_response(
#             ret
#         )
#     except KeyError:
#         # If can't find user session, reply with 401
#         return aiohttp.web.Response(
#             status=401,
#             reason="No user session was found"
#         )


# async def s3_download_object(dloadrequest):
#     """
#     Function to pull a short-lived presigned download URL from the s3 server
#     """
#     # TODO: implement exception handling and debug messages for URL fetching
#     try:
#         # Check for established session
#         # TODO: change over to API specific cookie
#         if (decrypt_cookie(dloadrequest) not in
#                 dloadrequest.app['Sessions']):
#             raise KeyError()
#         # Open a client to the server
#         s3 = boto3.client(
#             's3',
#         )
#         # Get a presigned url from the server with a 2000ms TTL
#         url = s3.generate_presigned_url(
#             'get_object',
#             Params={
#                 'Bucket': dloadrequest.query['bucket'],
#                 'Key': dloadrequest.query['objkey']
#             },
#             ExpiresIn=2
#         )
#         # Re-direct the user to the presigned URL
#         response = aiohttp.web.Response()
#         response.set_status(303)
#         response.headers.add(
#             'Location', url
#         )
#
#         return response
#     # If can't find user session, reply with 401
#     except KeyError:
#         return aiohttp.web.Response(
#             status=401,
#             reason="No user session was found"
#         )


async def get_os_user(request):
    """
    Function for fetching the user that the OS session has been opened for.
    """
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
    A function for listing buckets through swift and outputting the necessary
    information in a JSON response.
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
    except SwiftError:
        return aiohttp.web.json_response([])


async def swift_list_objects(request):
    """
    A function for listing objects in a given bucket (container) through
    swift and outputting the necessary information in a JSON response.
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

        return aiohttp.web.json_response(
            objects['listing']
        )
    except SwiftError:
        return aiohttp.web.json_response([])


async def swift_download_object(request):
    """
    A function for fetching a temporary pre-signed download URL for a swift
    object.
    """
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
    acc_meta_hdr = serv.stat()['headers']
    if 'x-account-meta-temp-url-key' in acc_meta_hdr.keys():
        temp_url_key = acc_meta_hdr['x-account-meta-temp-url-key']
    elif 'x-acccount-meta-temp-url-key-2' in acc_meta_hdr.keys():
        temp_url_key = acc_meta_hdr['x-account-meta-temp-url-key-2']
    # If the key headers don't exist, assume that the key has to be created by
    # the service
    else:
        # The hash only provides random data for the key, it doesn't have to
        # be cryptographically secure.
        temp_url_key = hashlib.sha256(os.urandom(128))
        pass

    # Generate temporary URL
    host = "https://object.pouta.csc.fi:443"
    container = request.query['bucket']
    object_key = request.query['objkey']
    expires = int(time.time() + 60 * 15)
    path = '/v1/%s/%s/%s' % (stats['items'][0][1], container, object_key)
    hmac_body = '%s\n%s\n%s' % ('GET', expires, path)
    signature = hmac.new(
        bytes(temp_url_key),
        hmac_body.encode('utf-8'),
        hashlib.sha1,
    ).hexdigest()

    dloadurl = "{0}{1}?temp_url_sig={2}&temp_url_expires={3}".format(
        host, path, signature, expires
    )

    response = aiohttp.web.Response(
        status=302,
        body="FOUND"
    )
    response.headers['Location'] = dloadurl
    return response


async def os_list_projects(request):
    """
    A function for responding with the projects available for the session's
    unscoped token.
    """
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


# Re-map functions that are actually used in the program, depending on which
# platform to use – s3 or swift
# if SETUP_WITH_S3:
#     list_buckets = s3_list_buckets
#     list_objects = s3_list_objects
#     download_object = s3_download_object
# else:
list_buckets = swift_list_buckets
list_objects = swift_list_objects
download_object = swift_download_object
