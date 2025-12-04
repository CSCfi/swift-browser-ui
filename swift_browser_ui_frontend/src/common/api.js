// API fetch functions.

import {
  DEV,
} from "@/common/conv";

import {
  GetBucketPolicyCommand,
  HeadBucketCommand,
  PutBucketPolicyCommand,
  DeleteBucketPolicyCommand,
} from "@aws-sdk/client-s3";

async function fetchWithCookie({method, url, body, signal}) {
  return fetch(url, {
    method,
    body,
    signal,
    credentials: "same-origin",
  })
    .then(response => {
      switch (response.status) {
        case 401:
          if (window.location.pathname !== "/accessibility") {
            window.location.pathname = "/unauth";
          }
          break;
        case 403:
          window.location.pathname = "/forbid";
          break;
        case 503:
          window.location.pathname = "/uidown";
          break;
      }

      return response;
    })
    .catch(error => {
      if (!signal?.aborted) {
        if (DEV) {
          console.log("Fetch error. Might be a networking issue", error);
        }
        throw new Error(error);
      }
    });
}
export async function GET(url, signal) {
  return fetchWithCookie({
    url,
    signal,
    method: "GET",
  });
}
export async function POST(url, body) {
  return fetchWithCookie({
    url,
    body,
    method: "POST",
  });
}
export async function PUT(url, body) {
  return fetchWithCookie({
    url,
    body,
    method: "PUT",
  });
}
export async function DELETE(url, body) {
  return fetchWithCookie({
    url,
    body,
    method: "DELETE",
  });
}

export async function getUser() {
  // Get username of the currently displayed user.
  let getUserURL = new URL("/api/username", document.location.origin);
  let uname = await GET(getUserURL);

  if (uname.status !== 401) {
    return await uname.json();
  }
  else {
    return "";
  }
}

export async function getProjects() {
  // Get available projects from the API.
  let getProjectsURL = new URL("/api/projects", document.location.origin);
  let ret = await GET(getProjectsURL);
  return await ret.json();
}

export async function copyBucket(
  project,
  bucket,
  source_bucket,
) {
  // Replicate the bucket from a specified source to the location
  let fetchURL = new URL("/replicate/".concat(
    encodeURI(project), "/",
    encodeURI(bucket),
  ), document.location.origin);

  fetchURL.searchParams.append("from_bucket", source_bucket);

  let ret = await POST(fetchURL);

  if (ret.status != 202) {
    throw new Error("Bucket replication not successful.");
  }

  return ret;
}

export async function createAPIKey(
  project,
  id,
) {
  // Tell backend to create a new project scoped API key
  let fetchURL = new URL("/token/".concat(
    encodeURI(project), "/",
    encodeURI(id),
  ), document.location.origin);

  let ret = await GET(fetchURL);

  if (ret.status != 201) {
    throw new Error("API key creation failed");
  }

  return ret.json();
}

export async function listAPIKeys(project) {
  // Get all API keys created for the project by id
  let fetchURL = new URL(
    "/token/".concat(encodeURI(project)), document.location.origin,
  );

  let ret = await GET(fetchURL);

  if (ret.status != 200) {
    throw new Error("API key listing fetch failed");
  }

  return ret.json();
}

export async function removeAPIKey(
  project,
  id,
) {
  // Tell backend to delete API keys matching the ID
  let fetchURL = new URL("/token/".concat(
    encodeURI(project), "/",
    encodeURI(id),
  ), document.location.origin);

  let ret = await DELETE(fetchURL);

  if (ret.status != 204) {
    throw new Error("API key deletion failed");
  }
}

export async function getUploadEndpoint(
  project,
  owner,
  container,
) {
  // Fetch upload endpoint, session and signature information
  let fetchURL = new URL("/upload/".concat(
    encodeURI(owner),
    "/",
    encodeURI(container),
  ),
  document.location.origin,
  );
  fetchURL.searchParams.append("project", project);
  let ret = await GET(fetchURL);

  if (ret.status != 200) {
    throw new Error("Failed to get upload session information.");
  }

  return ret.json();
}

export async function killUploadEndpoint(
  project,
  owner,
) {
  let fetchURL = new URL(
    `/upload/${encodeURI(owner)}`,
    document.location.origin,
  );
  fetchURL.searchParams.append("project", project);
  let ret = await DELETE(fetchURL);

  if (ret.status != 204) {
    throw new Error("Failed to kill upload session.");
  }
}

// Convenience function for performing a signed fetch
export async function signedFetch(
  method,
  base,
  path,
  body,
  params,
  lifetime = 60,
) {
  let signatureUrl = new URL(`/sign/${lifetime}`, document.location.origin);
  signatureUrl.searchParams.append("path", path);
  let signed = await GET(signatureUrl);
  signed = await signed.json();

  let fetchUrl = new URL(base.concat(path));
  fetchUrl.searchParams.append("valid", signed.valid);
  fetchUrl.searchParams.append("signature", signed.signature);
  if (params !== undefined) {
    for (const param in params) {
      fetchUrl.searchParams.append(param, params[param]);
    }
  }

  let resp = await fetch(
    fetchUrl,
    {
      method,
      body,
    },
  );

  return resp;
}

// Get the EC2 credentials from backend, for S3 operations in frontend.
export async function getEC2Credentials(
  project,
) {
  let fetchURL = new URL(`/api/${encodeURI(project)}/OS-EC2`, document.location.origin);
  let resp = await GET(fetchURL);

  if (resp.status != 200) {
    throw new Error("Failed to retrieve EC2 credentials.");
  }

  return await resp.json();
}

// Proxy ListBuckets command through the backend
export async function awsListBuckets(
  project,
  continuation_token = undefined,
  max_buckets = undefined,
) {
  let fetchURL = new URL(`/api/s3/${encodeURI(project)}`, document.location.origin);

  if (continuation_token !== undefined) {
    fetchURL.searchParams.append("continuation_token", continuation_token);
  }
  if (max_buckets !== undefined && max_buckets > 0) {
    fetchURL.searchParams.append("max_buckets", max_buckets);
  }

  let resp = await GET(fetchURL);
  if (resp.status != 200) {
    throw new Error("Failed to retrieve the bucket page.");
  }

  let ret = await resp.json();
  for (const bucket of ret.Buckets) {
    bucket.CreationDate = new Date(bucket.CreationDate);
  }

  if (DEV) console.log(ret);

  return ret;
}

// Proxy CreateBucket command through the backend
export async function awsCreateBucket(
  project,
  bucket,
) {
  let fetchURL = new URL(`/api/s3/${encodeURI(project)}/${encodeURI(bucket)}`, document.location.origin);
  let resp = await PUT(fetchURL);

  return resp;
}

// Update all bucket cors
export async function awsBulkAddBucketCors(
  project,
) {
  let fetchURL = new URL(`/api/s3/${encodeURI(project)}/cors`, document.location.origin);
  let resp = await POST(fetchURL);

  if (resp.status != 204) {
    throw new Error("Failed to fix the bucket cors in all buckets.");
  }
}

// Update CORS for a list of buckets
export async function awsBulkAddBucketListCors(
  project,
  buckets,
) {
  let fetchURL = new URL(`/api/s3/${encodeURI(project)}/cors`, document.location.origin);
  fetchURL.searchParams.append("buckets", buckets);

  let resp = await POST(fetchURL);

  if (resp.status != 204) {
    throw new Error("Failed to fix the bucket cors in the listed buckets.");
  }
}

// Update single bucket cors
export async function awsAddBucketCors(
  project,
  bucket,
) {
  let fetchURL = new URL(`/api/s3/${encodeURI(project)}/${bucket}/cors`, document.location.origin);
  let resp = await POST(fetchURL);

  if (resp.status != 204) {
    throw new Error("Failed to fix the bucket cors.");
  }
}

// Add the bucket policy for receivers without touching existing policies
export async function addAccessControlBucketPolicy(
  bucket,
  rights,
  receivers,
  client,
) {
  // Fetch the existing bucket policy as a baseline
  let policy = {
    "Version": "2012-10-17",
    "Statement": [],
  };
  let getBucketPolicyCommand = new GetBucketPolicyCommand({
    Bucket: bucket,
  });
  let currentPolicyResp = await client.send(getBucketPolicyCommand).catch(e => {
    switch(e.name) {
      case "NoSuchBucketPolicy":
        if (DEV) console.log("No existing bucket policy could be retrieved.");
        break;
      case "NoSuchBucket":
        if (DEV) {
          console.log(
            "Policy could not be retrieved due to nonexistent bucket.",
          );
        }
        return "NoSuchBucket";
      default:
        throw e;
    }
  });
  if (currentPolicyResp === "NoSuchBucket") {
    return;
  }
  if (currentPolicyResp?.Policy !== undefined) {
    policy = JSON.parse(currentPolicyResp.Policy);
  }

  // Expand the policy with the new policy entries.
  for (const receiver of receivers) {
    let actions = [];
    if (rights.indexOf("r") >= 0) {
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
  let putBucketPolicyCommand = new PutBucketPolicyCommand({
    Bucket: bucket,
    Policy: JSON.stringify(policy),
  });
  await client.send(putBucketPolicyCommand);
}

// Remove thebucket policy for receivers without purging other policies
export async function removeAccessControlBucketPolicy(
  bucket,
  receivers,
  client,
) {
  // Fetch the existing bucket policy
  let policy = {
    Version: "2012-10-17",
    Statement: [],
  };
  let getBucketPolicyCommand = new GetBucketPolicyCommand({
    Bucket: bucket,
  });
  let currentPolicyResp = await client.send(getBucketPolicyCommand).catch(
    e => {
      switch(e.name) {
        // Policy has already been removed, we can skip the logic.
        case "NoSuchBucketPolicy":
          if (DEV) console.log("Current policy could not be retrieved.");
          return;
        case "NoSuchBucket":
          if (DEV) {
            console.log("Could not delete policy due to nonexistent bucket.");
          }
          return "NoSuchBucket";
        default:
          throw e;
      }
    },
  );
  if (currentPolicyResp === "NoSuchBucket") {
    return;
  }
  if (currentPolicyResp?.Policy !== undefined) {
    policy = JSON.parse(currentPolicyResp.Policy);
  }

  // Filter out the old policy entries
  for (const receiver of receivers) {
    policy.Statement = policy.Statement.filter(statement => {
      console.log(statement);
      console.log(receiver);
      console.log(statement.Principal.AWS.match(receiver) == null);
      return (statement.Principal.AWS.match(receiver) == null);
    });
  }

  if (policy.Statement.length === 0) {
    let deleteBucketPolicyCommand = new DeleteBucketPolicyCommand({
      Bucket: bucket,
    });
    await client.send(deleteBucketPolicyCommand).catch(e => {
      if (DEV) console.log("Failed to delete bucket policy.");
      if (DEV) console.log(e);
    });
    return;
  }

  // Override the old bucket policy
  let putBucketPolicyCommand = new PutBucketPolicyCommand({
    Bucket: bucket,
    Policy: JSON.stringify(policy),
  });
  await client.send(putBucketPolicyCommand);
}

export async function checkBucketExists(client, bucketName) {
  try {
    const resp = await client.send(new HeadBucketCommand({
      Bucket: bucketName,
    }));
    if (resp?.$metadata?.httpStatusCode === 200) return true;
  } catch (e) {
    if (e?.$metadata?.httpStatusCode === 403) return true;
    if (e?.$metadata?.httpStatusCode === 404) return false;
  }
}
