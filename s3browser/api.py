import aiohttp.web
import boto3
import datetime
from ._convenience import decrypt_cookie


# TODO: Check if it's necessary to change the API from s3 -> swift
# Hardcoded s3 access keys for testing purposes, will be redundant when
# authentication is implemented (hopefully at least)
***REMOVED******REMOVED***AWS_ENDPOINT_URL = "http://127.0.0.1:9000"
SETUP_WITH_S3 = True


async def s3_list_buckets(request):
    """
    The internal API call for fetching a list of buckets available for user
    """
    # TODO: Refactor code to store session specific s3 client to app mapping
    try:
        if await decrypt_cookie(request) not in request.app['Sessions']:
            raise KeyError()

        s3 = boto3.client(
            's3',
***REMOVED******REMOVED******REMOVED***        )
        # Fetch the information about the user's buckets from API
        ret = s3.list_buckets()['Buckets']
        for i in ret:
            # Transform the CreationDate into a user readable string, since
            # the datetime-object is not JSON-serializeable
            i['CreationDate'] = i['CreationDate'].ctime()

        return aiohttp.web.json_response(
            ret
        )
    # If can't find user session, reply with 401
    except KeyError:
        return aiohttp.web.Response(
            status=401,
            reason="No user session was found"
        )


async def s3_list_objects(request):
    """
    The internal API call for fetching a list of available objects inside
    a specified bucket
    """
    try:
        if await decrypt_cookie(request) not in request.app['Sessions']:
            raise KeyError()
        s3 = boto3.client(
            's3',
***REMOVED******REMOVED******REMOVED***        )
        # Get all objects in the specified bucket
        ret = s3.list_objects(
            Bucket=request.query['bucket']
        )['Contents']
        for i in ret:
            # Transform the LastModified date value into a user readable
            # string, since the datetime-object is not JSON-serializeable
            i['LastModified'] = i['LastModified'].ctime()

        return aiohttp.web.json_response(
            ret
        )
    # If can't find user session, reply with 401
    except KeyError:
        return aiohttp.web.Response(
            status=401,
            reason="No user session was found"
        )


async def s3_download_object(dloadrequest):
    """
    Function to pull a short-lived presigned download URL from the s3 server
    """
    # TODO: implement exception handling and debug messages for URL fetching
    try:
        # Check for established session
        # TODO: change over to API specific cookie
        if (await decrypt_cookie(dloadrequest) not in
                dloadrequest.app['Sessions']):
            raise KeyError()
        # Open a client to the server
        s3 = boto3.client(
            's3',
***REMOVED******REMOVED******REMOVED***        )
        # Get a presigned url from the server with a 2000ms TTL
        url = s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': dloadrequest.query['bucket'],
                'Key': dloadrequest.query['objkey']
            },
            ExpiresIn=2
        )
        # Re-direct the user to the presigned URL
        response = aiohttp.web.Response()
        response.set_status(303)
        response.headers.add(
            'Location', url
        )

        return response
    # If can't find user session, reply with 401
    except KeyError:
        return aiohttp.web.Response(
            status=401,
            reason="No user session was found"
        )


async def swift_list_buckets(request):
    """
    A function for listing buckets through swift and outputting the necessary
    information in a JSON response.
    """
    pass


async def swift_list_objects(request):
    """
    A function for listing objects in a given bucket (container) through
    swift and outputting the necessary information in a JSON response.
    """
    pass


async def swift_download_object(request):
    """
    A function for fetching a temporary pre-signed download URL for a swift
    object.
    """
    pass


# Re-map functions that are actually used in the program, depending on which
# platform to use – s3 or swift
if SETUP_WITH_S3:
    list_buckets = s3_list_buckets
    list_objects = s3_list_objects
    download_object = s3_download_object
else:
    list_buckets = swift_list_buckets
    list_objects = swift_list_objects
    download_object = swift_download_object
