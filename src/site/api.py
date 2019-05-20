# -*- coding: utf-8 -*-


import aiohttp.web
import boto3
import datetime


# TODO: Check if it's necessary to change the API from s3 -> swift
# Hardcoded s3 access keys for testing purposes, will be redundant when
# authentication is implemented (hopefully at least)
***REMOVED******REMOVED***AWS_ENDPOINT_URL = "http://127.0.0.1:9000"


async def list_buckets(request):
    """
    The internal API call for fetching a list of buckets available for user
    """
    # TODO: Perhaps think up a way to keep the s3 sessions persistent?
    try:
        session = request.cookies['S3BROW_SESSION']
        s3 = boto3.client(
            's3',
***REMOVED******REMOVED******REMOVED***        )
        ret = s3.list_buckets()['Buckets']
        for i in ret:
            i['CreationDate'] = i['CreationDate'].ctime()

        return aiohttp.web.json_response(
            ret
        )
    except KeyError:
        return aiohttp.web.Response(
            status=403,
            reason="No user session was found"
        )


async def list_objects(request):
    """
    The internal API call for fetching a list of available objects inside
    a specified bucket
    """
    try:
        session = request.cookies['S3BROW_SESSION']
        s3 = boto3.client(
            's3',
***REMOVED******REMOVED******REMOVED***        )
        ret = s3.list_objects(
            Bucket=request.query['bucket']
        )['Contents']
        for i in ret:
            i['LastModified'] = i['LastModified'].ctime()

        return aiohttp.web.json_response(
            ret
        )
    except KeyError:
        return aiohttp.web.Response(
            status=403,
            reason="No user session was found"
        )


async def download_object(dloadrequest):
    """
    The internal API call for mapping an object to a websocket, to make enable
    object streaming.
    """
    try:
        session = dloadrequest.cookies['S3BROW_SESSION']
        s3 = boto3.client(
            's3',
***REMOVED******REMOVED******REMOVED***        )

        url = s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': dloadrequest.query['bucket'],
                'Key': dloadrequest.query['objkey']
            },
            ExpiresIn=1
        )

        response = aiohttp.web.Response()
        response.set_status(303)
        response.headers.add(
            'Location', url
        )

        return response
    except KeyError:
        return aiohttp.web.Response(
            status=403,
            reason="No user session was found"
        )
