# -*- coding: utf-8 -*-


import aiohttp.web
import boto3
import datetime


# TODO: Implement dynamic credential passing
# TODO: Check if it's necessary to change the API from s3 -> swift
# Hardcoded s3 access keys for testing purposes, will be redundant when
# authentication is implemented (hopefully at least)
***REMOVED******REMOVED***AWS_ENDPOINT_URL = "http://127.0.0.1:9000"


API_ENDPOINT = '/api'


async def listBuckets(request):
    """
    The internal API call for fetching a list of buckets available for user
    """
    # TODO: Perhaps think up a way to keep the s3 sessions persistent?
    s3 = boto3.client(
        's3',
***REMOVED******REMOVED******REMOVED***    )
    ret = s3.list_buckets()['Buckets']
    for i in ret:
        i['CreationDate'] = i['CreationDate'].ctime()

    return aiohttp.web.json_response(
        ret
    )


async def listObjects(request):
    """
    The internal API call for fetching a list of available objects inside
    a specified bucket
    """
    s3 = boto3.client(
        's3',
***REMOVED******REMOVED******REMOVED***    )
    ret = s3.list_objects(
        Bucket=request.query['bucket']
    )['Contents']
    for i in ret:
        i['LastModified'] = i['LastModified'].ctime()

    return aiohttp.web.json_response(
        ret
    )


# TODO: refactor object downloadin completely
async def downloadObject(dloadrequest):
    """
    The internal API call for mapping an object to a websocket, to make enable
    object streaming.
    """
    s3 = boto3.client(
        's3',
***REMOVED******REMOVED******REMOVED***    )
    s3object = s3.get_object(
        Bucket=dloadrequest.query['bucket'],
        Key=dloadrequest.query['objkey']
    )

    retws = aiohttp.web.WebSocketResponse(
        compress=False,  # Data already compressed when downloading
    )
    await retws.prepare(dloadrequest)

    await retws.ping(message='test')

    return retws
