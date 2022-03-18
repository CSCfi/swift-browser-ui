// API fetch functions.

import { 
  getHumanReadableSize, 
  makeGetObjectsMetaURL,
  DEV,
} from "@/common/conv";

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
        case 403:
          window.location.pathname = "/unauth";
          break;
        case 500:
          break;
      }
      
      return response;
    })
    .catch(error => {
      if(DEV) console.log("Fetch error. Might be a networking issue", error);
      throw new Error(error);
    });
}
export async function GET(url, signal) {
  return fetchWithCookie({
    url,
    signal,
    method: "GET",
  });
}
async function POST(url, body) {
  return fetchWithCookie({
    url,
    body,
    method: "POST",
  });
}
async function PUT(url, body) {
  return fetchWithCookie({
    url,
    body,
    method: "PUT",
  });
}
async function DELETE(url, body) {
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
  return await uname.json();
}

export async function getProjects() {
  // Get available projects from the API.
  let getProjectsURL = new URL("/api/projects", document.location.origin);
  let ret = await GET(getProjectsURL);
  return await ret.json();
}

export async function getContainers(
  project,
  marker = "",
) {
  // List buckets for a given project.
  let getBucketsUrl = new URL(
    "/api/" + encodeURI(project), document.location.origin,
  );
  if (marker) {
    getBucketsUrl.searchParams.append("marker", marker);
  }
  let ret = await GET(getBucketsUrl);
  if (ret.status == 200) {
    return await ret.json();
  } else {
    return [];
  }
}

export async function getContainerMeta(
  project,
  container,
  signal,
) {
  // Get metadata for a given bucket, owned by a given project.
  let url = new URL(
    "/api/meta/".concat(
      encodeURI(project), "/",
      encodeURI(container)),
    document.location.origin,
  );
  let ret = await GET(url, signal);
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
  let objects = await GET(objUrl, signal);
  if (objects.status == 200) {
    objects = await objects.json();
    for (let i = 0; i < objects.length; i++) {
      objects[i]["url"] = "/api/".concat(
        encodeURI(project),
        "/",
        encodeURI(container),
        "/",
        encodeURI(objects[i]["name"]),
      );
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
){
  // Batch get metadata for a list of objects
  if (url === undefined) {  
    url = makeGetObjectsMetaURL(project, container, objects);
  }

  let ret = await GET(url, signal);
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

export async function getAccessControlMeta(project) {
  // Fetch the ACL metadata for all project containers.
  let metaURL = new URL(
    "/api/".concat(encodeURI(project), "/acl"), document.location.origin,
  );
  let ret = await GET(metaURL);
  return await ret.json();
}

export async function removeAccessControlMeta(
  project,
  container,
  receiver = undefined,
) {
  // Remove access control metadata from the specified container
  let url = "/api/access/".concat(
    encodeURI(project), "/",
    encodeURI(container),
  );
  if (receiver) {
    url.concat("/", encodeURI(receiver));
  }
  let aclURL = new URL(url, document.location.origin);
  await DELETE(aclURL);
}

export async function addAccessControlMeta(
  project,
  container,
  rights,
  receivers,
) {
  // Add access control metadata to a container for the specified projects
  let aclURL = new URL(
    "/api/access/".concat(
      encodeURI(project), "/",
      encodeURI(container),
    ),
    document.location.origin,
  );
  let projects_csv = receivers.toString();
  let rights_str = rights.toString().replace(",", "");
  aclURL.searchParams.append("projects", projects_csv);
  aclURL.searchParams.append("rights", rights_str);

  await POST(aclURL);
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

export async function swiftCreateContainer(
  project,
  container,
  tags,
) {
  // Create a container matching the specified name.
  let fetchURL = new URL(
    "/api/".concat(
      encodeURI(project), "/",
      encodeURI(container),
    ),
    document.location.origin,
  );
  let body = {
    tags,
  };
  let ret = await PUT(fetchURL, JSON.stringify(body));
  if (ret.status != 201) {
    if (ret.status == 409) {
      throw new Error("Container name already in use.");
    }
    if (ret.status == 400) {
      throw new Error("Invalid container or tag name");
    }
    throw new Error("Container creation unsuccessful.");
  }
}

export async function swiftDeleteContainer(
  project,
  container,
) {
  // Delete a container.
  let fetchURL = new URL("/api/".concat(
    encodeURI(project), "/",
    encodeURI(container),
  ), document.location.origin);

  let ret = await DELETE(fetchURL);
  if (ret.status != 204) {
    throw new Error("Container deletion not successful.");
  }
}

export async function swiftDeleteObjects(
  project,
  container,
  objects,
) {
  let fetchURL = new URL("/api/".concat(
    encodeURI(project), "/",
    encodeURI(container),
  ), document.location.origin);
  fetchURL.searchParams.append("objects", true);

  let ret = await DELETE(
    fetchURL, JSON.stringify(objects),
  );
  if (ret.status != 204) {
    throw new Error("Object / objects deletion not successful.");
  }
}

export async function swiftCopyContainer(
  project,
  container,
  source_project,
  source_container,
) {
  // Replicate the container from a specified source to the location

  let fetchURL = new URL("/replicate/".concat(
    encodeURI(project), "/",
    encodeURI(container),
  ), document.location.origin);

  fetchURL.searchParams.append("from_project", source_project);
  fetchURL.searchParams.append("from_container", source_container);

  let ret = await POST(fetchURL);

  if (ret.status != 202) {
    throw new Error("Container replication not successful.");
  }

  return ret;
}

export async function createExtToken(
  project,
  id,
) {
  // Tell backend to create a new project scoped API token
  let fetchURL = new URL("/token/".concat(
    encodeURI(project), "/",
    encodeURI(id),
  ), document.location.origin);

  let ret = await GET(fetchURL);

  if (ret.status != 201) {
    throw new Error("Token creation failed");
  }

  return ret.json();
}

export async function listTokens(project) {
  // Get all tokens created for the project by id
  let fetchURL = new URL(
    "/token/".concat(encodeURI(project)), document.location.origin,
  );

  let ret = await GET(fetchURL);

  if (ret.status != 200) {
    throw new Error("Token listing fetch failed");
  }

  return ret.json();
}

export async function removeToken(
  project,
  id,
) {
  // Tell backend to delete API tokens matching the ID
  let fetchURL = new URL("/token/".concat(
    encodeURI(project), "/",
    encodeURI(id),
  ), document.location.origin);

  let ret = await DELETE(fetchURL);

  if (ret.status != 204) {
    throw new Error("Token deletion failed");
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
