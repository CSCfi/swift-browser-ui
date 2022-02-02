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
      return error;
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
async function DELETE(url) {
  return fetchWithCookie({
    url,
    method: "DELETE",
  });
}

export async function getUser() {
  // Function to get the username of the currently displayed user.
  let getUserURL = new URL("/api/username", document.location.origin);
  let uname = GET(getUserURL)
    .then(
      function (response) { return response.json(); },
    ).then(
      function (uname) { return uname; },
    );
  return uname;
}

export async function getProjects() {
  // Fetch available projects from the API
  let getProjectsURL = new URL("/api/projects", document.location.origin);
  let projects = GET(getProjectsURL)
    .then(
      function (response) { return response.json(); },
    ).then(
      function (ret) {
        return ret;
      },
    );
  return projects;
}

export async function changeProjectApi(newProject) {
  // Change the project that the user is currently browsing
  // Returns true if the project change is successful, otherwise false
  let rescopeURL = new URL("/login/rescope", document.location.origin);
  rescopeURL.searchParams.append("project", newProject);
  let ret = GET(rescopeURL)
    .then(
      function (resp) {
        return resp.status == 204 ? true : false;
      },
    );
  return ret;
}

export default async function getActiveProject() {
  // Fetch the active project from the API
  // Returns the active project name if the fetch is successful, otherwise
  // returns nothing
  let getProjectURL = new URL("/api/project/active",
    document.location.origin);
  let activeProj = GET(getProjectURL)
    .then(
      function (resp) {
        return resp.json();
      },
    );
  return activeProj;
}

export async function getContainers() {
  let getContainersUrl = new URL("/api/containers", document.location.origin);
  // Fetch containers from the API for the user that's currently logged in
  let containers = GET(getContainersUrl)
    .then(
      function (resp) { return resp.json(); },
    );
  return containers;
}

export async function getContainerMeta(
  container,
  signal,
){
  let url = new URL(
    "/api/container/meta?container=".concat(encodeURI(container)),
    document.location.origin,
  );

  let ret = await GET(url, signal);
  return ret.json();
}

export async function updateContainerMeta(
  container,
  metadata,
){
  let url = new URL(
    "/api/container/meta?container=".concat(encodeURI(container)),
    document.location.origin,
  );

  let ret = await POST(url, JSON.stringify(metadata));
  return ret;
}

export async function getObjects(container, signal) {
  // Fetch objects contained in a container from the API for the user
  // that's currently logged in.
  let objUrl = new URL("/api/container/objects", document.location.origin);
  objUrl.searchParams.append("container", container);
  let objects = GET(objUrl, signal)
    .then(
      function (resp) { return resp.json(); },
    ).then(
      function (ret) {
        for (let i = 0; i < ret.length; i++) {
          ret[i]["url"] = (
            "/api/object/dload?container=" + container +
            "&objkey=" + ret[i]["name"]
          );
        }
        return ret;
      },
    );
  return objects;
}

export async function getObjectsMeta (
  container,
  objects,
  url,
  signal,
){
  if (url === undefined) {  
    url = makeGetObjectsMetaURL(container, objects);
  }

  let ret = await GET(url, signal);
  return ret.json();
}

export async function updateObjectMeta (
  container,
  objectMeta,
){
  let url = new URL(
    "/api/container/object/meta?container=".concat(encodeURI(container)),
    document.location.origin,
  );

  let ret = await POST(url, JSON.stringify([objectMeta]));
  return ret;
}

export async function getSharedObjects (
  project,
  container,
  url,
) {
  // Fetch objects contained in a container from the API for the user
  // that's currently logged in.
  let objUrl = new URL("/api/shared/objects", document.location.origin);
  objUrl.searchParams.append("storageurl", url);
  objUrl.searchParams.append("container", container);
  let objects = GET(objUrl)
    .then(
      function (resp) { return resp.json(); },
    ).then(
      function (ret) {
        for (let i = 0; i < ret.length; i++) {
          ret[i]["url"] = (
            "/download/" + project +
            "/" + container +
            "/" + ret[i]["name"]
          );
        }
        return ret;
      },
    );
  return objects;
}

export async function getProjectMeta() {
  // Fetch project metadata for the currently active project, containing
  // the project data usage, container amount and object amount.
  let metaURL = new URL("/api/project/meta", document.location.origin);
  let ret = GET(metaURL)
    .then(function (resp) { return resp.json(); })
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


export async function getAccessControlMeta() {
  // Fetch the ACL metadata for all project containers.
  let metaURL = new URL("/api/project/acl", document.location.origin);
  let ret = GET(metaURL)
    .then(function (ret) { return ret.json(); });
  return ret;
}


export async function removeAccessControlMeta(
  container,
  project = undefined,
) {
  // Remove access control metadata from the container specified
  let aclURL = new URL(
    "/api/access/".concat(container),
    document.location.origin,
  );

  if (project) {
    aclURL.searchParams.append("project", project);
  }

  await DELETE(aclURL);
}


export async function addAccessControlMeta(
  container,
  rights,
  projects,
) {
  // Add access control metadata for the projects specified in a container
  let aclURL = new URL(
    "/api/access/".concat(container),
    document.location.origin,
  );

  let projects_csv = projects.toString();
  let rights_str = rights.toString().replace(",", "");

  aclURL.searchParams.append("projects", projects_csv);
  aclURL.searchParams.append("rights", rights_str);

  await POST(aclURL);
}


export async function getSharedContainerAddress() {
  // Get the project specific address for container sharing
  let addrURL = new URL(
    "/api/project/address",
    document.location.origin,
  );

  let ret = await GET(addrURL);
  return ret.json();
}


export async function swiftCreateContainer(
  container,
  tags,
) {
  // Create a container matching the specified name.
  let fetchURL = new URL("/api/containers/".concat(
    container,
  ), document.location.origin);

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
    throw new Error("Container creation not successful.");
  }
}


export async function swiftDeleteContainer(
  container,
) {
  let fetchURL = new URL("/api/containers/".concat(
    container,
  ), document.location.origin);

  let ret = await DELETE(fetchURL);
  if (ret.status != 204) {
    throw new Error("Container deletion not successful.");
  }
}


export async function swiftDeleteObjects(
  container,
  objects,
) {
  let fetchURL = new URL("/api/containers/".concat(
    container,
  ), document.location.origin);
  fetchURL.searchParams.append("objects", objects.toString());

  let ret = await DELETE(fetchURL);
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
    project, "/",
    container,
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
  id,
) {
  // Tell backend to create a new project scoped API token

  let fetchURL = new URL("/token/".concat(
    id,
  ), document.location.origin);

  let ret = await GET(fetchURL);

  if (ret.status != 201) {
    throw new Error("Token creation failed");
  }

  return ret.json();
}


export async function listTokens() {
  // Get all tokens created for the project by id

  let fetchURL = new URL("/token", document.location.origin);

  let ret = await GET(fetchURL);

  if (ret.status != 200) {
    throw new Error("Token listing fetch failed");
  }

  return ret.json();
}


export async function removeToken(
  id,
) {
  // Tell backend to delete API tokens matching the ID

  let fetchURL = new URL("/token/".concat(
    id,
  ), document.location.origin);

  let ret = await DELETE(fetchURL);

  if (ret.status != 204) {
    throw new Error("Token deletion failed");
  }
}


export async function getUploadEndpoint(
  project,
  container,
) {
  // Fetch upload endpoint, session and signature information
  let fetchURL = new URL("/upload/".concat(
    project,
    "/",
    container,
  ),
  document.location.origin,
  );
  let ret = await GET(fetchURL);

  if (ret.status != 200) {
    throw new Error("Failed to get upload session information.");
  }

  return ret.json();
}
