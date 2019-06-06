# -*- coding: utf-8 -*-


import boto3
import random
import os
import hashlib
import openstack
import keystoneauth1
import keystoneauth1.identity.v3 as v3


def getRandom():
    """
    Get 1K of random data
    """
    return os.urandom(1024)


def getRandomKey():
    """
    Create a 256bit sha2 hash to act as a unique identifier for the object
    """
    return hashlib.sha256(
        str(os.urandom(1024)).encode('ascii')
    ).hexdigest()


def s3_generateTestData(key, secret, endpoint):
    """
    Generate test data inside object storage that's compatible with the Amazon
    S3 API.
    """
    s3object = boto3.client(
        's3',
        aws_access_key_id=key,
        aws_secret_access_key=secret,
        endpoint_url=endpoint,
    )
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
                Key=getRandomKey(),
                Body=testdata.encode('ascii')
            )


def swift_generate_test_data(
    containers=1,  # Create only one test container by default
    objects=50000,  # Default object amount at max 50000 pcs
    max_filesize=1048576,  # Default files at max 1M large
    endpoint='127.0.0.1',  # Assume local testing environment
    user_domain_id='default',  # Assume default domain id
    user_project_id='default'  # Assume default project id
        ):
    """
    Generate test data inside object storage that's compatible with the OS
    Swift (Openstack Object Storage) API.
    """
    # Setup authentication plugin
    auth_plugin = v3.Password(
        auth_url='http://' + 'endpoint' + ':5000/v3',
        domain_id=user_domain_id,
        project_id=user_project_id
    )
    sess = keystoneauth1.session.Session(
        auth=auth_plugin,
        verify=False,
    )

    # Next set up the client
    os_con = openstack.connection.Connection(
        session=sess,
    )

    # Add the object-store service to the connected services
    os_con.add_service('object-store')

    # Generate the desired amount of containers
    for i in range(0, containers):
        os_con.object_store.create_container('test-container-' + str(i))
        for _ in range(0, random.choice(
            [x for x in range(0, objects)]
        )):
            testdata = ''.join([getRandom() for _ in range(0, random.choice(
                [y for y in range(0, max_filesize / 1024)]
            ))])
            os_con.object_store.upload_object(
                container='test-container-' + str(i),
                name=getRandomKey(),
                data=testdata,
            )


def main():
    swift_generate_test_data(
        containers=10,
        endpoint='',
        user_project_id='testproj',
    )


if __name__ == '__main__':
    main()
