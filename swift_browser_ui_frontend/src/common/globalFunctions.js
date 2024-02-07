import store from "@/common/store";
import { taginputConfirmKeys } from "@/common/conv";
import { getDB } from "@/common/db";

export function toggleCreateFolderModal() {
  store.commit("toggleCreateFolderModal", true);
}

export function toggleEditTagsModal(objectName, containerName) {
  if (objectName) {
    store.commit("setObjectName", objectName);
  }
  if (containerName) {
    store.commit("setFolderName", containerName);
  }
  store.commit("toggleEditTagsModal", true);
}

export function toggleCopyFolderModal(folderName, sourceProjectId) {
  if (folderName) {
    store.commit("setFolderName", folderName);
  }
  if(sourceProjectId) {
    store.commit("setSourceProjectId", sourceProjectId);
  }
  store.commit("toggleCopyFolderModal", true);
}

export function toggleDeleteModal(objects, containerName) {
  if (objects) {
    store.commit("setDeletableObjects", objects);
  }
  if (containerName) {
    store.commit("setFolderName", containerName);
  }
  store.commit("toggleDeleteModal", true);
}

export function getProjectNumber(project) {
  if (project.name) {
    const splitProjectName = project.name.split("_");
    return splitProjectName.length > 1 ? splitProjectName[1] : "";
  } else {
    return "";
  }
}

export async function getSharingContainers (projectId, signal) {
  return store.state.client && projectId
    ? await store.state.client.getShare(projectId, signal)
    : [];
}

export async function getSharedContainers (projectId, signal) {
  return store.state.client
    ? await store.state.client.getAccess(projectId, signal)
    : [];
}

export async function getAccessDetails (
  projectId,
  folderName,
  sourceProjectId,
  signal)
{
  return store.state.client
    ? await store.state.client.getAccessDetails(
      projectId,
      folderName,
      sourceProjectId,
      signal)
    : [];
}

export function addNewTag (event, currentTags, onBlur) {
  if (taginputConfirmKeys.includes(event.key) || onBlur) {
    event.preventDefault();
    const newTag = event.target.value.trim();
    event.target.value = "";
    if (newTag !== "" && !currentTags.includes(newTag)) {
      currentTags.push(newTag);
    }
  }
  return currentTags;
}

export function deleteTag (event, tag, currentTags) {
  event.preventDefault();
  return currentTags.filter(el => el !== tag);
}

export function getPrefix(route) {
  // Get current pseudofolder prefix
  if (route.query.prefix == undefined) {
    return "";
  }
  return `${route.query.prefix}/`;
}

export function getFolderName(folderName, route) {
  // Get the name of the currently displayed pseudofolder
  let endregex = new RegExp("/.*$");
  return folderName.replace(getPrefix(route), "").replace(endregex, "");
}

export function isFile(path, route) {
  // Return true if path represents a file in the active prefix context
  return path.replace(getPrefix(route), "").match("/") ? false : true;
}

export function getPaginationOptions(t) {
  const itemText = count => count === 1 ? t("message.table.item")
    : t("message.table.items").toLowerCase();

  const paginationOptions = {
    itemCount: 0,
    itemsPerPage: 10,
    currentPage: 1,
    startFrom: 0,
    endTo: 9,
    textOverrides: {
      itemsPerPageText: t("message.table.itemsPerPage"),
      nextPage: t("message.table.nextPage"),
      prevPage: t("message.table.prevPage"),
      pageText: ({ start, end, count }) =>
        start + " - " + end + " / " + count + " " + itemText(count),
      pageOfText: ({ pageNumber, count }) =>
        t("message.table.page") + pageNumber + " / " + count + "",
    },
  };
  return paginationOptions;
}

export function validateFolderName(str, t, containers) {
  //minimum length 3 chars
  let error = "";
  //forbid !"#$%&'()*+,/:;<=>?@[\]^`{|}~  allow .-_
  const re = new RegExp("[!-,/:-@\\[-\\^`\\{-~]");
  if (str.length <= 2) {
    error = t("message.error.tooShort");
  }
  else if (str.match(re)) {
    error= t("message.error.forbiddenChars");
  }
  else if (str.endsWith("_segments")) {
    error= t("message.error.segments");
  }
  else {
    if (containers) {
      const found = containers.find(cont => cont.name === str);
      if (found) error = t("message.error.inUse");
    }
  }
  return error;
}

export function getCurrentISOtime(time) {
  return time ? new Date(time).toISOString() : new Date().toISOString();
}

export function getContainerLastmodified(containers, cont) {
  // Get the current container and its last_modified from IDB
  const idb_cont = containers.find(
    el => el.name === cont.name && el.last_modified);
  const idb_last_modified = idb_cont ? idb_cont.last_modified : null;

  // Compare the last_modified from current container with
  // IDB container, choose the latest one
  if (idb_last_modified &&
    (idb_last_modified > cont.last_modified) ||
    (!cont.last_modified)
  ) {
    return idb_last_modified;
  }
  return cont.last_modified;
}

export async function updateContainerLastmodified(
  projectID,
  container,
  objects,
) {
  // Declare the latest last_modified of container
  let cont_last_modified = container.last_modified;

  const last_modified_arr = objects.map(obj => obj.last_modified);

  // Find the latest last_modified among all objects,
  // compare it with the current last_modified of container,
  // assign the latest last_modified for container
  for (let i = 0; i < last_modified_arr.length; i++) {
    if (last_modified_arr[i] > cont_last_modified) {
      cont_last_modified = last_modified_arr[i];
    }
  }

  // Assign the latest last_modified of objects to parent container
  if (cont_last_modified) {
    await getDB().containers
      .where({ projectID: projectID, name: container.name})
      .modify({ last_modified: cont_last_modified });
  }
}

export function checkIfItemIsLastOnPage(paginationOptions){
  //Checks if item is last on page and reverts to previous page
  if(paginationOptions.currentPage - 1 === 0){
    return 1;
  }
  if(paginationOptions.itemCount ===
    (paginationOptions.currentPage - 1)
    * paginationOptions.itemsPerPage){
    return paginationOptions.currentPage-=1;
  }
  return paginationOptions.currentPage;
}

export async function updateObjectsAndObjectTags(
  containers,
  projectID,
  signal,
  updateTags = true, // Obj tags don't need to be updated when uploading objs
) {
  if (containers.length > 0) {
    for (let i = 0; i < containers.length; i++) {
      const currentContainer = containers[i];

      await store.dispatch("updateObjects", {
        projectID,
        owner: currentContainer.container.owner,
        container: {
          id: currentContainer.key,
          ...currentContainer.container,
        },
        signal,
        updateTags,
      });

      if (i === containers.length - 1) {
        store.commit("setLoaderVisible", false);
      }
    }
  }
}

export function checkIfCanDownloadTar(objs, isSubfolder) {
  if (!objs) {
    return true;
  }
  else if (isSubfolder && objs.length === 1) {
    //no tar when single file in a subfolder
    return true;
  }
  else {
    //file or subfolder name max 99 chars, prefix max 154
    const pathOk = objs.every(
      (path) => {
        const elements = path.split("/");
        if (elements.find(el => el.length > 99)) return false;
        if (elements.length > 2 &&
          path.length - elements.slice(-1)[0].length > 154) return false;
        return true;
      });
    return pathOk;
  }
}

export function timeout(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export function addErrorToastOnMain(msg) {
  document.querySelector("#container-error-toasts")
    .addToast(
      { progress: false,
        type: "error",
        duration: 6000,
        message: msg },
    );
}

export function moveToast(toastToMove, otherElement, restore) {
  //restore toast to original position or
  //move toast above another element
  if (toastToMove && restore) {
    toastToMove.style.marginBottom = "0";
  }
  else if (toastToMove && otherElement){
    const h = otherElement.getBoundingClientRect().height;
    toastToMove.style.marginBottom = h + "px";
  }
}
