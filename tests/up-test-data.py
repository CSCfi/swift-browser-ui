# -*- coding: utf-8 -*-


import boto3
import random
import hashlib


***REMOVED******REMOVED***AWS_ENDPOINT_URL = 'http://127.0.0.1:9000'


def getRandom():
    return hashlib.sha256(
        str(random.random()).encode('ascii')
    ).hexdigest()


def generateTestData(s3object):
    for i in range(1, 11):
        s3object.create_bucket(
            Bucket=('test-bucket-' + str(i))
        )
    for i in range(1, 11):
        for _ in range(0, random.choice(
            [x for x in range(0, 500)]
        )):
            testdata = ''.join([getRandom() for x in range(0, random.choice(
                [y for y in range(0, 10000)]
            ))])
            s3object.put_object(
                Bucket='test-bucket-' + str(i),
                Key=getRandom(),
                Body=testdata.encode('ascii')
            )


if __name__ == '__main__':
    generateTestData(
        boto3.client(
            's3',
***REMOVED******REMOVED******REMOVED***        )
    )
