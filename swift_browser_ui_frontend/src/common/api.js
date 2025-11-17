// API fetch functions.

import {
  getHumanReadableSize,
  makeGetObjectsMetaURL,
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

export async function getContainers(
  project,
  marker,
  signal,
) {
  // List buckets for a given project.
  let getBucketsUrl = new URL(
    "/api/" + encodeURI(project), document.location.origin,
  );
  if (marker) {
    getBucketsUrl.searchParams.append("marker", marker);
  }
  let ret = await GET(getBucketsUrl, signal);
  if (ret.status == 200 && !signal?.aborted) {
    return await ret.json();
  }
  return [];
}

export async function getContainerMeta(
  project,
  container,
  signal,
  owner = "",
) {
  // Get metadata for a given bucket, owned by a given project.
  let url = new URL(
    "/api/meta/".concat(
      encodeURI(project), "/",
      encodeURI(container)),
    document.location.origin,
  );
  if (owner !== "") {
    url.searchParams.append("owner", owner);
  }

  let ret = await GET(url, signal);
  if (signal?.aborted) {
    return ["", {}];
  }
  return await ret.json();
}

export async function updateContainerMeta(
  project,
  container,
  metadata,
) {
  // Update bucket metadata.
  let url = new URL(
    "/api/".concat(encodeURI(project), "/", encodeURI(container)),
    document.location.origin,
  );
  let ret = await POST(url, JSON.stringify(metadata));
  return ret;
}

export async function getObjects(
  project,
  container,
  marker = "",
  signal,
  shared = false,
  owner = "",
) {
  // Fetch object listing for a container.
  let objUrl = new URL(
    "/api/".concat(
      encodeURI(project), "/",
      encodeURI(container),
    ),
    document.location.origin,
  );
  if (marker) {
    objUrl.searchParams.append("marker", marker);
  }
  if (shared && (owner != "")) {
    objUrl.searchParams.append("owner", owner);
  }
  let objects = await GET(objUrl, signal);

  if (objects?.status == 200 && !signal?.aborted) {
    objects = await objects.json();
    for (let i = 0; i < objects.length; i++) {
      if (shared) {
        objects[i]["url"] = "/download/".concat(
          encodeURI(project),
          "/",
          encodeURI(container),
          "/",
          encodeURI(objects[i]["name"]),
        );
      } else {
        objects[i]["url"] = "/api/".concat(
          encodeURI(project),
          "/",
          encodeURI(container),
          "/",
          encodeURI(objects[i]["name"]),
        );
      }
    }
    return objects;
  } else {
    return [];
  }
}

export async function getObjectsMeta (
  project,
  container,
  objects,
  url,
  signal,
  owner = "",
){
  // Batch get metadata for a list of objects
  if (url === undefined) {
    url = makeGetObjectsMetaURL(project, container, objects);
  }

  if (owner !== "") {
    url.searchParams.append("owner", owner);
  }

  let ret = await GET(url, signal);
  if (signal?.aborted) {
    return [];
  }
  return ret.json();
}

export async function updateObjectMeta (
  project,
  container,
  objectMeta,
) {
  // Update metadata for object.
  let url = new URL(
    "/api/".concat(
      encodeURI(project), "/",
      encodeURI(container),
    ),
    document.location.origin,
  );
  url.searchParams.append("objects", "true");
  let ret = await POST(url, JSON.stringify([objectMeta]));
  return ret;
}

export async function getProjectMeta(project) {
  // Fetch project metadata for the specified project
  let metaURL = new URL(
    "/api/meta/".concat(encodeURI(project)), document.location.origin,
  );
  let ret = GET(metaURL).then(function (resp) { return resp.json(); })
    .then(function (json_ret) {
      let newRet = json_ret;
      newRet["Size"] = getHumanReadableSize(newRet["Bytes"]);
      if (newRet["Bytes"] > 10995116277760) {
        newRet["ProjectSize"] = newRet["Size"];
      } else {
        newRet["ProjectSize"] = "10TiB";
      }
      // we check if it is greather than 0.4Mib if not we display with 10
      // decimal points
      if (newRet["Bytes"] > 900000) {
        newRet["Billed"] = parseFloat(newRet["Bytes"] / 10995116277760)
          .toPrecision(4);
      } else {
        newRet["Billed"] = parseFloat(newRet["Bytes"] / 10995116277760)
          .toFixed(10);
      }
      return newRet;
    });
  return ret;
}

export async function getSharedContainerAddress(project) {
  // Get the project specific address for container sharing
  let addrURL = new URL(
    "/api/".concat(
      encodeURI(project), "/address",
    ),
    document.location.origin,
  );

  let ret = await GET(addrURL);
  return ret.json();
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

export async function getUploadSocket(
  project,
  owner,
) {
  let fetchURL = new URL(
    "/enupload/".concat(encodeURI(owner)),
    document.location.origin,
  );

  fetchURL.searchParams.append("project", project);
  let ret = await GET(fetchURL);

  if (ret.status != 200) {
    throw new Error("Failed to get upload socket information.");
  }

  return ret.json();
}

export async function getUploadCryptedEndpoint(
  project,
  owner,
  container,
  object,
) {
  // Fetch upload endpoint information for encrypted upload
  let fetchURL = new URL("/enupload/".concat(
    encodeURI(owner),
    "/",
    encodeURI(container),
    "/",
    encodeURI(object),
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
) {
  let fetchURL = new URL(`/api/s3/${encodeURI(project)}`, document.location.origin);

  if (continuation_token !== undefined) {
    fetchURL.searchParams.append("continuation_token", continuation_token);
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

  return resp.status;
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
      "Resource": `arn:aws:s3:::${bucket}`,
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
