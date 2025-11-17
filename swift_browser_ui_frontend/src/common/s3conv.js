// S3 operations for the frontend


import {
  S3Client,
  CreateBucketCommand,
  ListObjectsV2Command,
  ListBucketsCommand,
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

// Create a client for accessing the S3 API
export async function getClient(project, endpoint) {
  let creds = await getEC2Credentials(project);
  let client = new S3Client({
    region: "us-east-1",
    endpoint: endpoint,
    credentials: {
      accessKeyId: creds.access,
      secretAccessKey: creds.secret,
    },
  });

  return client;
}

export async function listBuckets(client) {
  const input = {
    MaxBuckets: 1000,
    BucketRegion: "us-east-1",
  };

  const command = new ListBucketsCommand(input);
  const resp = await client.send(command);
  console.log(resp);
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

  const command = new PutBucketPolicyCommand(input);
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

  const command = new PutBucketPolicyCommand(input);
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

  const command = new PutBucketPolicyCommand(input);
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

  const command = new PutBucketPolicyCommand(input);
  const resp = await client.send(command);

  return resp;
}

export async function getBucketMetadata(client, bucket) {
  let continuationToken;
  let lastModified = bucket.CreationDate;
  let count = 0;
  let bytes = 0;

  try {
    do {
      const response = await client.send(new ListObjectsV2Command({
        Bucket: bucket.Name,
        ContinuationToken: continuationToken,
      }));

      if (response?.Contents) {
        count += response.Contents.length;
        response.Contents.forEach((obj) => {
          bytes += obj.Size;
          if (obj.LastModified > lastModified) {
            lastModified = obj.LastModified;
          }
        });
      }

      continuationToken = response?.NextContinuationToken;

    } while (continuationToken);
  } catch (e) {
    console.error(`Failed to get metadata for bucket "${bucket.Name}":`, e);
  }

  const metadata = {
    last_modified: lastModified?.toISOString(),
    bytes: bytes,
    count: count,
  };

  return metadata;
}
