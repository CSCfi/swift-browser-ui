import store from "@/common/store";
import { taginputConfirmKeys } from "@/common/conv";

export function toggleCreateFolderModal(folderName) {
  store.commit("toggleCreateFolderModal", true);
  if (folderName) {
    store.commit("setFolderName", folderName);
  }
}

export function toggleEditTagsModal(objectName, containerName) {
  store.commit("toggleEditTagsModal", true);
  if (objectName) {
    store.commit("setObjectName", objectName);
  }
  if (containerName) {
    store.commit("setFolderName", containerName);
  }
}

export function toggleCopyFolderModal(folderName, sourceProjectId) {
  store.commit("toggleCopyFolderModal", true);
  if (folderName) {
    store.commit("setFolderName", folderName);
  }
  if(sourceProjectId) {
    store.commit("setSourceProjectId", sourceProjectId);
  }
}

export function toggleDeleteModal(objects, containerName) {
  store.commit("toggleDeleteModal", true);
  if (objects) {
    store.commit("setDeletableObjects", objects);
  }
  if (containerName) {
    store.commit("setFolderName", containerName);
  }
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

export function isValidFolderName(str) {
  //minimum length 3 chars
  return str.length > 2;
}
