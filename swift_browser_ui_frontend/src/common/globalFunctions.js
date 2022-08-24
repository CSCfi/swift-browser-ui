import store from "@/common/store";

export function toggleCreateFolderModal(folderName) {
  store.commit("toggleCreateFolderModal", true);
  if (folderName) {
    store.commit("setFolderName", folderName);
  }
} 