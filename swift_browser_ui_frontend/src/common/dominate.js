/*
SD Submit sharing functionality
*/

import { PutBucketPolicyCommand } from "@aws-sdk/client-s3";
import { GET } from "./api";
import { DEV } from "./conv";
import { getCurrentISOtime } from "./globalFunctions";
import { getDB } from "./db";

// Fetch resources for SD Submit integration
export async function discoverSubmitConfiguration() {
  let submitUrl = new URL("/discover/submit", document.location.origin);
  let resp = await GET(submitUrl);
  return await resp.json();
}

// Sign an API request to SD Submit using a given user token
async function sign_submit_api_request(userToken, valid, userId) {
  let tokenEncoder = new TextEncoder;
  let rawToken = tokenEncoder.encode(userToken);
  let k = await window.crypto.subtle.importKey(
    "raw",
    rawToken,
    {
      name: "HMAC",
      hash: "SHA-256",
      length: rawToken.length,
    },
    false,
    ["sign"],
  );

  let signature = await window.crypto.subtle.sign(
    "HMAC",
    k,
    tokenEncoder.encode(`${valid}${userId}`),
  );

  return signature;
}

// Flag a bucket for submission to SD Submit
export async function submit_bucket(
  client,
  config,
  userToken,
  project,
  bucket,
  objects,
) {
  // Update object metadata with submit information and gather checksums
  let files = [];

  for (let object of objects) {
    if (DEV) {
      console.log(`Marking object ${object.name} as shared to SD Submit`);
      console.log(object);
    }

    let tags = object.tags;
    tags.push("submitted");

    await updateObjectMeta(
      project.id,
      bucket.name,
      [object.name, {usertags: tags.join(";")}],
    );

    // Add a formatted file entry for the submission file list
    files.push({
      "name": object.name.split("/").pop(),
      "path": `s3:/${bucket.name}/${object.name}`,
      "bytes": object.bytes,
      "encrypted_checksums": [
        {
          "type": md5,
          "value": "PLACEHOLDER",
        },
      ],
      "unencrypted_checksums": [
        {
          "type": md5,
          "value": "PLACEHOLDER",
        },
      ],
    });
  }

  // Update bucket metadata with submit information
  if (DEV) {
    console.log(`Marking bucket ${bucket.name} as containing items shared to SD Submit`);
    console.log(bucket);
  }
  let bucketTags = bucket.tags;
  tags.push("submitted");
  await getDB().containers
    .where({
      projectID: project.id,
      name: bucket.name,
    })
    .modify({ tags, last_modified: getCurrentISOtime() });

  // Update bucket ACL with grants for SD Submit robot accounts
  let submitReadAccessPolicy = {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "GrantReadAccess",
        "Effect": "Allow",
        "Principal": {
          "AWS": `arn:aws:iam::${config.sd_submit_id}:root`,
        },
        "Action": "s3:GetObject",
        "Resource": `arn:aws:s3:::${bucket.name}/*`,
      },
    ],
  };
  if (DEV) {
    console.log("Updating bucket policy to add read rights to SD Submit.");
    console.log(submitReadAccessPolicy);
  }
  let bucketPolicyParams = {
    "Bucket": bucket.name,
    "Policy": JSON.stringify(submitReadAccessPolicy),
  };
  const putSubmitPolicyCommand = new PutBucketPolicyCommand(bucketPolicyParams);
  let response = await client.send(putSubmitPolicyCommand);
  if (DEV) {
    console.log(response);
  }

  await getDB().containers
    .where({
      projectID: project.id,
      name: bucket.name,
    })
    .modify({ last_modified: getCurrentISOtime() });

  // POST the file listing to SD Submit
  if (DEV) {
    console.log("Pushing the object list to SD Submit");
  }

  let filePostRequest = {
    "userId": "placeholder",
    "projectId": "placeholder",
    "files": files,
  };

  let publishUrl = new URL("/v1/files", config.sd_submit_endpoint);
  let valid = (new Date().getTime() / 1000) + 600;
  publishUrl.searchParams.append("valid", valid);
  publishUrl.searchParams.append("userId", project.id);

  let publishSignature = await sign_submit_api_request(
    userToken,
    (new Date().getTime() / 1000) + 600,
    project.id,
  );
  response = await fetch(publishUrl, {
    method: "POST",
    body: JSON.stringify(filePostRequest),
    headers: {
      "Authorization": `Bearer ${publishSignature}`,
    },
  });
}
