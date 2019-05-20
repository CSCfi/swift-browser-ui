# -*- coding: utf-8 -*_

"""
Test dictionaries for API data, directly dumped from boto3. This way we can
fore-go setting up an s3 server for testing the API access from website, and
just use temporary static JSON-data when programming in the local environment.
"""


import datetime


bucketReturnExample = [
    {
        'Name': 'test-bucket-0',
        'CreationDate': datetime.datetime(2019, 5, 7, 11, 57, 54, 657000)
    },
    {
        'Name': 'test-bucket-1',
        'CreationDate': datetime.datetime(2019, 5, 7, 11, 57, 54, 662000)
    },
    {
        'Name': 'test-bucket-2',
        'CreationDate': datetime.datetime(2019, 5, 7, 11, 57, 54, 666000)
    },
    {
        'Name': 'test-bucket-3',
        'CreationDate': datetime.datetime(2019, 5, 7, 11, 57, 54, 669000)
    },
    {
        'Name': 'test-bucket-4',
        'CreationDate': datetime.datetime(2019, 5, 7, 11, 57, 54, 672000)
    },
    {
        'Name': 'test-bucket-5',
        'CreationDate': datetime.datetime(2019, 5, 7, 11, 57, 54, 675000)
    },
    {
        'Name': 'test-bucket-6',
        'CreationDate': datetime.datetime(2019, 5, 7, 11, 57, 54, 678000)
    },
    {
        'Name': 'test-bucket-7',
        'CreationDate': datetime.datetime(2019, 5, 7, 11, 57, 54, 683000)
    },
    {
        'Name': 'test-bucket-8',
        'CreationDate': datetime.datetime(2019, 5, 7, 11, 57, 54, 686000)
    },
    {
        'Name': 'test-bucket-9',
        'CreationDate': datetime.datetime(2019, 5, 7, 11, 57, 54, 690000)
    },
]


objectReturnExample = [
    {
        'Key':
            '01fca9355b818523bdf1b75f389a28ca85398e2a4b451fd6900809aeeef2a93a',
        'LastModified': datetime.datetime(2019, 5, 8, 6, 59, 13, 77000),
        'ETag': '"d41d8cd98f00b204e9800998ecf8427e"',
        'Size': 0,
        'StorageClass': 'STANDARD',
        'Owner': {
            'DisplayName': '',
            'ID':
            '02d6176db174dc93cb1b899f7c6078f08654445fe8cf1b6ce98d8855f66bdbf4'
        }
    },
    {
        'Key':
            '063a476867ef985f361d09674025ba5a8f05ea7d410b8fd47b247e2050aca31c',
        'LastModified': datetime.datetime(2019, 5, 8, 6, 59, 13, 56000),
        'ETag': '"d41d8cd98f00b204e9800998ecf8427e"',
        'Size': 0,
        'StorageClass': 'STANDARD',
        'Owner': {
            'DisplayName': '',
            'ID':
            '02d6176db174dc93cb1b899f7c6078f08654445fe8cf1b6ce98d8855f66bdbf4'
        }
    },
    {
        'Key':
        '59bd8a6d832ebf281f2454c0942ff27275040bc17213e52ba79dc962ed3345d9',
        'LastModified': datetime.datetime(2019, 5, 8, 6, 59, 12, 992000),
        'ETag': '"d41d8cd98f00b204e9800998ecf8427e"',
        'Size': 0,
        'StorageClass': 'STANDARD',
        'Owner': {
            'DisplayName': '',
            'ID':
            '02d6176db174dc93cb1b899f7c6078f08654445fe8cf1b6ce98d8855f66bdbf4'
        }
    },
    {
        'Key':
        '5ee54796bbfea81eab469b7a33ccd3cc2c4bb8315b84a22c2f058f8bccb5d315',
        'LastModified': datetime.datetime(2019, 5, 8, 6, 59, 12, 979000),
        'ETag': '"d41d8cd98f00b204e9800998ecf8427e"',
        'Size': 0,
        'StorageClass': 'STANDARD',
        'Owner': {
            'DisplayName': '',
            'ID':
            '02d6176db174dc93cb1b899f7c6078f08654445fe8cf1b6ce98d8855f66bdbf4'
        }
    },
    {
        'Key':
        '6e47ece35796fae56a07ace595bfa0043496535db4e16ef852b54eea6b456d51',
        'LastModified': datetime.datetime(2019, 5, 8, 6, 59, 13, 22000),
        'ETag': '"d41d8cd98f00b204e9800998ecf8427e"',
        'Size': 0,
        'StorageClass': 'STANDARD',
        'Owner': {
            'DisplayName': '',
            'ID':
            '02d6176db174dc93cb1b899f7c6078f08654445fe8cf1b6ce98d8855f66bdbf4'
        }
    },
]


for i in range(0, len(bucketReturnExample)):
    bucketReturnExample[i]['CreationDate'] =\
        bucketReturnExample[i]['CreationDate'].timestamp()


for i in range(0, len(objectReturnExample)):
    objectReturnExample[i]['LastModified'] =\
        objectReturnExample[i]['LastModified'].timestamp()
