// S3 operations for the frontend


import {
  S3Client,
  ListObjectsV2Command,
  ListBucketsCommand,
} from "@aws-sdk/client-s3";
import { getEC2Credentials, GET } from "./api";

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

export async function awsListObjects(client, bucket, prefix = undefined) {
  let continuationToken;
  let objects = [];

  try {
    do {
      let listObjectsCommandParams = {
        Bucket: bucket,
        ContinuationToken: continuationToken,
      };
      if (prefix !== undefined) {
        listObjectsCommandParams.Prefix = prefix;
      }

      const response = await client.send(
        new ListObjectsV2Command(listObjectsCommandParams),
      );

      if (response?.Contents) {
        response.Contents.map(item => {
          objects.push({
            name: item.Key,
            bytes: item.Size,
            last_modified: item.LastModified.toISOString(),
          });
        });
      }

      continuationToken = response?.NextContinuationToken;
    } while (continuationToken);
  } catch (e) {
    if (DEV) console.error(
      `Failed to list objects for bucket ${bucket}`,
      e,
    );
    if (DEV) console.error(`Returning empty listing for bucket ${bucket}`);
  }

  return objects;
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
