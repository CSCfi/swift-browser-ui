// S3 operations for the frontend


import {
  S3Client,
  ListObjectsCommand,
  PutBucketPolicyCommand,
} from "@aws-sdk/client-s3";
import { getEC2Credentials, GET } from "./api";
import { DEV } from "./conv";

// Fetch S3 endpoint from backend
export async function discoverEndpoint() {
  let endpointUrl = new URL("/discover/s3", document.location.origin);
  let resp = await GET(endpointUrl);
  resp = await resp.json();
  return resp.s3api_endpoint;
}

// Test that the S3 connection is available and working.
export async function verifyS3ConnectionAvailable(client) {
  if (DEV) {
    const input = {
      Bucket: "nonexistent-test-bucket",
    };
    const command = new ListObjectsCommand(input);
    const response = await client.send(command);

    console.log(response);
  }
}

// Create a client for accessing the S3 API
export async function getClient(project, endpoint) {
  let creds = await getEC2Credentials(project);
  let client = new S3Client({
    region: "RegionOne",
    stsRegionalEndpoints: "legacy",
    s3UsEast1RegionalEndpoint: "legacy",
    s3ForcePathStyle: true,
    forcePathStyle: true,
    endpoint: endpoint,
    credentials: {
      accessKeyId: creds.access,
      secretAccessKey: creds.secret,
    },
  });

  return client;
}

async function checkOldPolicy(client, bucket) {
  const input = {
    Bucket: bucket,
  };
  const command = new GetBucketPolicyCommand(input);
  const resp = await client.send(command);

  if (resp.Policy !== undefined && resp.Policy !== "") {
    return JSON.parse(resp.Policy);
  }

  return {
    Version: "2012-10-17",
    Statement: [],
  };
}

// Add an AWS ARN to the bucket read policy
export async function addUserBucketReadPolicy(client, bucket, account) {
  let d = new Date();
  let version = `${d.getFullYear()}-${d.getMonth()}-${d.getDay()}`;
  let policy = await checkOldPolicy(client, bucket);

  // For now use dirtier way adding statement for each user.
  // In future move to single statment and parse the Principal list.
  policy.Version = version;
  policy.Statement.push({
    Sid: `AllowReadForAccount${account}`,
    Principal: {
      "AWS": [
        `arn:aws:iam::${account}`,
      ],
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetObject",
        "s3:HeadObject",
        "s3:HeadBucket",
      ],
      "Resource": [`arn:aws:s3::${bucket}`],
    },
  });

  const input = {
    Bucket: bucket,
    Policy: JSON.stringify(policy),
  };

  const command = PutBucketPolicyCommand(input);
  const resp = await client.send(command);

  return resp;
}

// Add an AWS ARN to the bucket write policy
export async function addUserBucketWritePolicy(client, bucket, account) {
  let d = new Date();
  let version = `${d.getFullYear()}-${d.getMonth()}-${d.getDay()}`;
  let policy = await checkOldPolicy(client, bucket);

  // For now use dirtier way adding statement for each user.
  // In future move to single statment and parse the Principal list.
  policy.Version = version;
  // Grant the required rights a user needs for writing,
  // e.g. multipart uploads
  policy.Statement.push({
    Sid: `AllowWriteForAccount${account}`,
    Principal: {
      "AWS": [
        `arn:aws:iam::${account}`,
      ],
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:CreateMultipartUpload",
        "s3:UploadPart",
        "s3:CompleteMultipartUpload",
        "s3:AbortMultipartUpload",
      ],
      "Resource": [`arn:aws:s3::${bucket}`],
    },
  });

  const input = {
    Bucket: bucket,
    Policy: JSON.stringify(policy),
  };

  const command = PutBucketPolicyCommand(input);
  const resp = await client.send(command);

  return resp;
}

// Remove an AWS ARN from the bucket read policy
export async function removeUserBucketReadPolicy(client, bucket, account) {
  let d = new Date();
  let version = `${d.getFullYear()}-${d.getMonth()}-${d.getDay()}`;
  let policy = await checkOldPolicy(client, bucket);

  policy.Version = version;
  // Dump the matching statement with a filter
  policy.Statement = policy.Statement.filter(s => s.Sid !== `AllowReadForAccount${account}`);

  const input = {
    Bucket: bucket,
    Policy: JSON.stringify(policy),
  };

  const command = PutBucketPolicyCommand(input);
  const resp = await client.send(command);

  return resp;
}

// Remove an AWS ARN from the bucket write policy
export async function removeUserBucketWritePolicy(client, bucket, account) {
  let d = new Date();
  let version = `${d.getFullYear()}-${d.getMonth()}-${d.getDay()}`;
  let policy = await checkOldPolicy(client, bucket);

  policy.Version = version;
  // Dump the matching statement with a filter
  policy.Statement = policy.Statement.filter(s => s.Sid !== `AllowWriteForAccount${account}`);

  const input = {
    Bucket: bucket,
    Policy: JSON.stringify(policy),
  };

  const command = PutBucketPolicyCommand(input);
  const resp = await client.send(command);

  return resp;
}
