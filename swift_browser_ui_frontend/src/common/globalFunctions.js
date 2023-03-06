import store from "@/common/store";
import { taginputConfirmKeyCodes } from "@/common/conv";

export function toggleCreateFolderModal(folderName) {
  store.commit("toggleCreateFolderModal", true);
  if (folderName) {
    store.commit("setFolderName", folderName);
  }
  modifyBrowserPageStyles();
}

export function toggleEditTagsModal(objectName, containerName) {
  store.commit("toggleEditTagsModal", true);
  if (objectName) {
    store.commit("setObjectName", objectName);
  }
  if (containerName) {
    store.commit("setFolderName", containerName);
  }
  modifyBrowserPageStyles();
}

export function toggleCopyFolderModal(folderName, sourceProjectId) {
  store.commit("toggleCopyFolderModal", true);
  if (folderName) {
    store.commit("setFolderName", folderName);
  }
  if(sourceProjectId) {
    store.commit("setSourceProjectId", sourceProjectId);
  }
  modifyBrowserPageStyles();
}

export function modifyBrowserPageStyles() {
  const element = document.getElementById("mainContainer");
  element.classList.toggle("mainContainer-additionalStyles");
}

export function getProjectNumber(project) {
  if (project.name) {
    const splitProjectName = project.name.split("_");
    return splitProjectName.length > 1 ? splitProjectName[1] : "";
  } else {
    return "";
  }
}

export async function getSharingContainers (projectId) {
  return store.state.client && projectId
    ? await store.state.client.getShare(projectId)
    : [];
}

export async function getSharedContainers (projectId) {
  return store.state.client
    ? await store.state.client.getAccess(projectId)
    : [];
}

export async function getAccessDetails (
  projectId,
  folderName,
  sourceProjectId)
{
  return store.state.client
    ? await store.state.client.getAccessDetails(
      projectId,
      folderName,
      sourceProjectId)
    : [];
}

export function addNewTag (event, currentTags, onBlur) {
  if (taginputConfirmKeyCodes.includes(event.keyCode) || onBlur) {
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



