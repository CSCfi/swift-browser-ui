/*
SD Submit sharing functionality
*/

import { ListBucketsCommand, ListObjectsCommand } from "@aws-sdk/client-s3";
import { GET } from "./api";
import { getClient, getLegacyClient } from "./s3conv";

// Vue proxies b0rk the aws-sdk completely, so we have to revert to using a
// singleton
export var s3client;
export var s3LegacyClient;
export var s3MinioClient;

// Fetch resources for SD Submit integration
export async function discoverSubmitConfiguration() {
  let submitUrl = new URL("/discover/submit", document.location.origin);
  let resp = await GET(submitUrl);
  return await resp.json();
}

export async function validateLegacyS3Access($store) {
  console.log($store.state.s3endpoint);

  s3LegacyClient = await getLegacyClient(
    $store.state.active.id,
    $store.state.s3endpoint,
  );

  console.log(s3LegacyClient);

  s3LegacyClient.listBuckets(function(err, data) {
    if (err) {
      console.log("Error", err);
    } else {
      console.log("Success", data.Buckets);
    }
  });
}

export async function validateS3Access($store) {
  s3client = await getClient(
    $store.state.active.id,
    $store.state.s3endpoint,
  );

  console.log(s3client);

  let bucketQuery = new ListObjectsCommand({
    Bucket: "test-bucket",
  });
  let response = await s3client.send(bucketQuery);
  console.log(response);
}

// Flag a bucket for submission to SD Submit
async function submit_bucket(config, bucket, objects) {
  // Update object metadata with submit information and gather checksums
  for (let object of objects) {

  }

  // Update bucket metadata with submit information

  // Update bucket ACL with grants for SD Submit robot accounts

  // POST the file listing to SD Submit
}
