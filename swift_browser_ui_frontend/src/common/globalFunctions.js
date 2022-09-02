import store from "@/common/store";

export function toggleCreateFolderModal(folderName) {
  store.commit("toggleCreateFolderModal", true);
  if (folderName) {
    store.commit("setFolderName", folderName);
  }
}

export function modifyBrowserPageStyles() {
  const element = document.getElementById("subContainer");
  element.classList.toggle("subContainer-additionalStyles");
}

export function getProjectNumber(project) {
  if (project.name) {
    const splitProjectName = project.name.split("_");
    return splitProjectName.length > 1 ? splitProjectName[1] : "";
  } else {
    return "";
  }
}
