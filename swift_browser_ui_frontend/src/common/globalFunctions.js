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

export function validateFolderName(str, t) {
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

export function setPrevActiveElement() {
  const prevActiveEl = document.activeElement;
  store.commit("setPreviousActiveEl", prevActiveEl);
}

export function getFocusableElements(focusableList) {
  const first = focusableList[0];
  let last = focusableList[focusableList.length - 1];
  if (last.disabled) last = focusableList[focusableList.length - 2];
  return { first, last };
}

export function addFocusClass(element) {
  element.classList.add("button-focus");
}

export function removeFocusClass(element) {
  element.removeAttribute("tabIndex");
  element.classList.remove("button-focus");
}

export function disableFocusOutsideModal (modal) {
  const nav = document.querySelector("nav");
  Array.from(nav.children).forEach((child) =>
    child.setAttribute("inert", "true"));

  const mainContent = document.getElementById("mainContent");
  Array.from(mainContent.children).forEach((child) => {
    if (child !== modal) child.setAttribute("inert", "true");
  });

  const footer = document.querySelector("footer");
  Array.from(footer.children).forEach((child) =>
    child.setAttribute("inert", "true"));
}

export function moveFocusOutOfModal(prevActiveEl) {
  const nav = document.querySelector("nav");
  Array.from(nav.children).forEach((child) => {
    child.removeAttribute("inert");
  });

  const mainContent = document.getElementById("mainContent");
  Array.from(mainContent.children).forEach((child) => {
    child.removeAttribute("inert");
  });

  const footer = document.querySelector("footer");
  Array.from(footer.children).forEach((child) =>
    child.removeAttribute("inert"));

  prevActiveEl.tabIndex = "0";
  prevActiveEl.focus();
  if (prevActiveEl === document.activeElement) {
    addFocusClass(prevActiveEl);
  }
}
