// S3 operations for the frontend


import { S3Client } from "@aws-sdk/client-s3";
import SDK from "aws-sdk";
import { getEC2Credentials, GET } from "./api";
import { DEV } from "./conv";

// Fetch S3 endpoint from backend
export async function discoverEndpoint() {
  let endpointUrl = new URL("/discover/s3", document.location.origin);
  let resp = await GET(endpointUrl);
  resp = await resp.json();
  return resp.s3api_endpoint;
}

// Create a client using S3 legacy version
export async function getLegacyClient(project, endpoint) {
  let creds = await getEC2Credentials(project);

  SDK.config.update({
    region: "RegionOne",
    s3ForcePathStyle: true,
    endpoint: endpoint,
    credentials: {
      accessKeyId: creds.access,
      secretAccessKey: creds.secret,
    },
  });

  console.log(SDK.config);

  let client = new SDK.S3();

  return client;
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
    credentials: { // Who was the 'bright' fellow who named these‽‽
      accessKeyId: creds.access,
      secretAccessKey: creds.secret,
    },
  });

  return client;
}
