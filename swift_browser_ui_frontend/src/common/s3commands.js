// S3 operations for the frontend

import {
  AbortMultipartUploadCommand,
  CompleteMultipartUploadCommand,
  CreateMultipartUploadCommand,
  DeleteBucketCommand,
  DeleteBucketPolicyCommand,
  DeleteObjectsCommand,
  GetBucketPolicyCommand,
  HeadBucketCommand,
  HeadObjectCommand,
  ListObjectsV2Command,
  PutBucketPolicyCommand,
} from "@aws-sdk/client-s3";
import { i18n } from "./i18n";
import { initS3 } from "./s3init";
import store from "./store";
import { DEV } from "./globalFunctions";

async function sendS3Command(command) {
  // Wrapper for S3 commands
  await initS3(
    store.state.active.id,
    store.state.active.name,
    store,
    i18n.global.t,
  );
  try {
    const resp = await store.state.s3client.send(command);
    return resp;
  } catch (e) {
    if (DEV) {
      console.error(`Error executing ${command?.constructor?.name} on bucket ${command?.input?.Bucket}`);
    }
    throw e;
  }
}

/** BUCKETS */

export async function awsDeleteBucket(bucket) {
  const command = new DeleteBucketCommand({
    Bucket: bucket,
  });
  const response = await sendS3Command(command);
  return response;
}

export async function checkBucketAccessible(bucket) {
  const command = new HeadBucketCommand({
    Bucket: bucket,
  });
  try {
    const resp = await sendS3Command(command);
    if (resp?.$metadata?.httpStatusCode === 200) return true;
  } catch {
    return false;
  }
}

export async function checkBucketExists(bucket) {
  const command = new HeadBucketCommand({
    Bucket: bucket,
  });
  try {
    const resp = await sendS3Command(command);
    if (resp?.$metadata?.httpStatusCode === 200) return true;
  } catch (e) {
    if (e?.$metadata?.httpStatusCode === 403) return true;
    return false;
  }
}

/** OBJECTS */

export async function awsDeleteObjects(bucket, objects) {
  const keys = objects.map(obj => ({ Key: obj }));
  const command = new DeleteObjectsCommand({
    Bucket: bucket,
    Delete: {
      Objects: keys,
    },
  });
  const response = await sendS3Command(command);
  return response;
}

export async function awsHeadObject(bucket, object) {
  const command = new HeadObjectCommand({
    Bucket: bucket,
    Key: object,
  });
  const response = await sendS3Command(command);
  return response;
}

export async function awsListObjects(bucket, prefix = undefined) {
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

      const command = new ListObjectsV2Command(listObjectsCommandParams);
      const response = await sendS3Command(command);

      if (response?.Contents) {
        response.Contents.map((item) => {
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
    if (DEV) console.error(`Failed to list objects for bucket ${bucket}`, e);
    if (DEV) console.error(`Returning empty listing for bucket ${bucket}`);
  }
  return objects;
}

export async function checkBucketEmpty(bucket) {
  const command = new ListObjectsV2Command({
    Bucket: bucket,
    MaxKeys: 1,
  });
  const response = await sendS3Command(command);
  return response?.Contents?.length ? false : true;
}

/**UPLOAD */

export async function awsCreateMultipartUpload(bucket, key, acl = undefined) {
  const input = {
    Bucket: bucket,
    Key: key,
  };
  if (acl) input.ACL = acl;

  const command = new CreateMultipartUploadCommand(input);
  const response = await sendS3Command(command);
  return response;
}

export async function awsCompleteMultipartUpload(bucket, key, parts, uploadID) {
  const input = {
    Bucket: bucket,
    Key: key,
    MultipartUpload: {
      Parts: parts,
    },
    UploadId: uploadID,
  };

  const command = new CompleteMultipartUploadCommand(input);
  const response = await sendS3Command(command);
  return response;
}

export async function awsAbortMultipartUpload(bucket, key, uploadID) {
  const input = {
    Bucket: bucket,
    Key: key,
    UploadId: uploadID,
  };

  const command = new AbortMultipartUploadCommand(input);
  const response = await sendS3Command(command);
  return response;
}

/** POLICIES */

export async function getBucketPolicyStatements(bucket) {
  // Get a list of bucket policy statements from S3
  try {
    const command = new GetBucketPolicyCommand({ Bucket: bucket });
    const response = await sendS3Command(command);
    if (response?.Policy !== undefined) {
      const policy = JSON.parse(response.Policy);
      return policy?.Statement ?? [];
    }
  } catch(e) {
    if (e.name === "NoSuchBucket") {
      if (DEV) console.error(`Error retrieving bucket ${bucket} policy: bucket does not exist`);
      throw e;
    }
    return [];
  }
}

export async function putBucketPolicy(bucket, policy) {
  // Override old bucket policy
  const command = new PutBucketPolicyCommand({
    Bucket: bucket,
    Policy: JSON.stringify(policy),
  });
  const response = await sendS3Command(command);
  return response;
}

export async function ensureCollaborateAccessPolicy(bucket) {
  // Check that the active project exists in owned bucket policy list
  // prior to starting the download
  let project = store.state.active;
  let statements = await getBucketPolicyStatements(bucket);

  // If the project already has the read and write policies, skip
  for (const statement of statements) {
    if (statement["Sid"] === "GrantSDConnectPreserveOwnerAccess") return;
  }

  // As the owner we want all access
  statements.push({
    "Sid": "GrantSDConnectPreserveOwnerAccess",
    "Effect": "Allow",
    "Principal": {
      "AWS": `arn:aws:iam::${project.id}:root`,
    },
    "Action": [
      "s3:*",
    ],
    "Resource": [`arn:aws:s3:::${bucket}`, `arn:aws:s3:::${bucket}/*`],
  });

  if (DEV) console.log(`Pushing preserve statement ${statements}`);

  let policy = {
    "Version": "2012-10-17",
    "Statement": statements,
  };

  // Override the old bucket policy
  const response = await putBucketPolicy(bucket, policy);
  return response;
}

/**
 * Adds access permissions to an S3 bucket policy.
 * @param {string} bucket - Name of the S3 bucket.
 * @param {string[]} rights - Array of permission flags: ["v"] or ["r"] or ["r","w"].
 * @param {string[]} receivers - Array of project IDs to grant access to.
 * @returns {Promise<object>} The response from the S3 PutBucketPolicy call.
 */

export async function addAccessControlBucketPolicy(
  bucket,
  rights,
  receivers,
) {
  // Add the bucket policy for receivers without touching existing policies
  // Fetch the existing bucket policy as a baseline
  const statements = await getBucketPolicyStatements(bucket);

  let policy = {
    "Version": "2012-10-17",
    "Statement": statements,
  };

  // Expand the policy with the new policy entries.
  for (const receiver of receivers) {
    let actions = [];
    if (rights.indexOf("r") >= 0 || rights.indexOf("v") >= 0) {
      actions = actions.concat([
        "s3:GetObject",
        "s3:ListBucket",
        "s3:GetObjectTagging",
        "s3:GetObjectVersion",
      ]);
    }
    if (rights.indexOf("w") >= 0) {
      actions = actions.concat([
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:AbortMultipartUpload",
        "s3:ListMultipartUploadParts",
        "s3:ListBucketMultipartUploads",
      ]);
    }

    policy.Statement.push({
      "Sid": "GrantSDConnectSharedAccessToProject",
      "Effect": "Allow",
      "Principal": {
        "AWS": `arn:aws:iam::${receiver}:root`,
      },
      "Action": actions,
      "Resource": [`arn:aws:s3:::${bucket}`, `arn:aws:s3:::${bucket}/*`],
    });
  }

  // Override the old bucket policy
  const response = await putBucketPolicy(bucket, policy);
  return response;
}

export async function removeAccessControlBucketPolicy(
  bucket,
  receivers,
) {
  // Remove the bucket policy for receivers without purging other policies
  // Fetch the existing bucket policy
  const statements = await getBucketPolicyStatements(bucket);

  let policy = {
    "Version": "2012-10-17",
    "Statement": statements,
  };

  // Filter out the old policy entries
  for (const receiver of receivers) {
    policy.Statement = policy.Statement.filter((statement) => {
      if (DEV) {
        console.log(statement);
        console.log(receiver);
        console.log(statement.Principal.AWS.match(receiver) == null);
      }
      return statement.Principal.AWS.match(receiver) == null;
    });
  }

  if (policy.Statement.length === 0) {
    let deleteBucketPolicyCommand = new DeleteBucketPolicyCommand({
      Bucket: bucket,
    });
    try {
      await sendS3Command(deleteBucketPolicyCommand);
    } catch (e) {
      if (DEV) console.log("Failed to delete bucket policy.");
      if (DEV) console.log(e);
    }
    return;
  }

  // Override the old bucket policy
  const response = await putBucketPolicy(bucket, policy);
  return response;
}
