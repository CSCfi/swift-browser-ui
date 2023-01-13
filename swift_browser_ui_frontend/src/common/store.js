// Vuex store for the variables that need to be globally available.
import Vue from "vue";
import Vuex from "vuex";

import { getContainers } from "@/common/api";
import { getObjects } from "@/common/api";
import {
  getTagsForContainer,
  getMetadataForSharedContainer,
  getTagsForObjects,
  makeGetObjectsMetaURL,
  tokenize,
} from "./conv";

import { initDB } from "@/common/db";
import {getSharedContainers} from "./globalFunctions";
Vue.use(Vuex);

const store = new Vuex.Store({
  state: {
    db: initDB(),
    projects: [],
    active: {},
    uname: "",
    multipleProjects: false,
    objectCache: [], // Only for shared objects
    langs: [
      { ph: "In English", value: "en" },
      { ph: "Suomeksi", value: "fi" },
    ],
    client: undefined,
    requestClient: undefined,
    resumableClient: undefined,
    isUploading: false,
    isChunking: false,
    encryptedFile: "",
    encryptedFileProgress: undefined,
    encryptedProgress: undefined,
    uploadProgress: undefined,
    uploadNotification: false,
    altContainer: undefined,
    uploadInfo: undefined,
    uploadEndpoint: "",
    transfer: [],
    pubkey: [],
    currentPrefix: "",
    dropFiles: [],
    openCreateFolderModal: false,
    selectedFolderName: "",
    openUploadModal: false,
    openShareModal: false,
    currentUpload: undefined,
    openEditTagsModal: false,
    selectedObjectName: "",
    openCopyFolderModal: false,
    isFolderCopied: false,
    sourceProjectId: "",
    uploadAbort: undefined,
  },
  mutations: {
    updateObjects(state, objects) {
      // Update object cache with the new object listing.
      state.objectCache = [...objects];
    },
    eraseObjects(state) {
      state.objectCache = [];
    },
    setProjects(state, newProjects) {
      // Update the project listing in store
      state.projects = newProjects;
      if (newProjects.length > 1) {
        state.multipleProjects = true;
      } else {
        state.multipleProjects = false;
      }
    },
    setActive(state, newActive) {
      // Update the active project in store
      state.active = newActive;
    },
    setUname(state, newUname) {
      // Update the username in store
      state.uname = newUname;
    },
    setSharingClient(state, newClient) {
      state.client = newClient;
    },
    setRequestClient(state, newClient) {
      state.requestClient = newClient;
    },
    setResumable(state, newClient) {
      state.resumableClient = newClient;
    },
    setUploading(state) {
      state.isUploading = true;
      if (!state.uploadNotification) state.uploadNotification = true;
    },
    stopUploading(state) {
      state.isUploading = false;
    },
    setChunking(state) {
      state.isChunking = true;
      if (!state.uploadNotification) state.uploadNotification = true;
    },
    stopChunking(state) {
      state.isChunking = false;
    },
    updateEncryptedProgress(state, progress) {
      state.encryptedProgress = progress;
    },
    eraseEncryptedProgress(state) {
      state.encryptedProgress = undefined;
    },
    setEncryptedFile(state, file) {
      state.encryptedFile = file;
    },
    eraseEncryptedFile(state) {
      state.encryptedFile = "";
    },
    updateEncryptedFileProgress(state, progress) {
      state.encryptedFileProgress = progress;
    },
    eraseEncryptedFileProgress(state) {
      state.encryptedFileProgress = undefined;
    },
    toggleUploadNotification(state, payload) {
      state.uploadNotification = payload;
    },
    updateProgress(state, progress) {
      state.uploadProgress = progress;
    },
    eraseProgress(state) {
      state.uploadProgress = undefined;
    },
    setAltContainer(state, altContainer) {
      state.altContainer = altContainer;
    },
    eraseAltContainer(state) {
      state.altContainer = undefined;
    },
    setUploadInfo(state, uploadInfo) {
      state.uploadInfo = uploadInfo;
    },
    eraseUploadInfo(state) {
      state.uploadInfo = undefined;
    },
    setUploadEndpoint(state, endpoint) {
      state.uploadEndpoint = endpoint;
    },
    appendFileTransfer(state, file) {
      state.transfer.push(file);
    },
    eraseTransfer(state) {
      state.transfer = [];
    },
    appendDropFiles(state, file) {
      if (
        state.dropFiles.find(
          ({ relativePath }) => relativePath === String(file.relativePath),
        ) === undefined &&
        state.dropFiles.find(({ name }) => name === String(file.name)) ===
          undefined
      ) {
        state.dropFiles.push(file);
      } else {
        // we remove and push the file again to get new size
        // and if the file exists to referesh dropFiles var
        state.dropFiles = state.dropFiles.filter(v => {
          return v.relativePath !== file.relativePath && v.name !== file.name;
        });
        state.dropFiles.push(file);
      }
    },
    eraseDropFile(state, file) {
      state.dropFiles.splice(
        state.dropFiles.findIndex(
          ({ name, relativePath }) =>
            relativePath === file.relativePath.value &&
            name === file.name.value,
        ),
        1,
      );
    },
    eraseDropFiles(state) {
      state.dropFiles = [];
    },
    appendPubKey(state, key) {
      state.pubkey.push(key);
    },
    erasePubKey(state) {
      state.pubkey = [];
    },
    setPrefix(state, prefix) {
      state.currentPrefix = prefix;
    },
    erasePrefix(state) {
      state.currentPrefix = "";
    },
    toggleCreateFolderModal(state, payload) {
      state.openCreateFolderModal = payload;
    },
    setFolderName(state, payload) {
      state.selectedFolderName = payload;
    },
    toggleUploadModal(state, payload) {
      state.openUploadModal = payload;
    },
    toggleShareModal(state, payload) {
      state.openShareModal = payload;
    },
    setCurrentUpload(state, cur) {
      state.currentUpload = cur;
    },
    eraseCurrentUpload(state) {
      delete state.currentUpload;
      state.currentUpload = undefined;
      state.uploadNotification = false;
    },
    createCurrentUploadAbort(state) {
      state.uploadAbort = new AbortController();
    },
    abortCurrentUpload(state) {
      if (state.uploadAbort !== undefined) {
        state.uploadAbort.abort();
      }
      delete state.uploadAbort;
      state.uploadAbort = undefined;
    },
    toggleEditTagsModal(state, payload) {
      state.openEditTagsModal = payload;
    },
    setObjectName(state, payload) {
      state.selectedObjectName = payload;
    },
    toggleCopyFolderModal(state, payload) {
      state.openCopyFolderModal = payload;
    },
    setFolderCopiedStatus(state, payload) {
      state.isFolderCopied = payload;
    },
    setSourceProjectId(state, payload) {
      state.sourceProjectId = payload;
    },
  },
  actions: {
    updateContainers: async function (
      { state, dispatch },
      { projectID, signal },
    ) {
      const existingContainers = await state.db.containers
        .where({ projectID })
        .toArray();
      let containers;
      let marker = "";
      let newContainers = [];
      do {
        containers = [];
        containers = await getContainers(projectID, marker).catch(() => {});
        if (containers.length > 0) {
          containers.forEach(cont => {
            cont.tokens = tokenize(cont.name);
            cont.projectID = projectID;
          });
          newContainers = newContainers.concat(containers);
          marker = containers[containers.length - 1].name;
        }
      } while (containers.length > 0);
      const sharedContainers = await getSharedContainers(projectID);

      if (sharedContainers.length > 0) {
        for (let i in sharedContainers) {
          let cont = sharedContainers[i];
          const { bytes, count } = await getMetadataForSharedContainer(
            projectID,
            cont.container,
            signal,
            cont.owner,
          );
          cont.tokens = tokenize(cont.container);
          cont.projectID = projectID;
          cont.bytes = bytes;
          cont.count = count;
          cont.name = cont.container;
        }
        await state.db.containers.bulkPut(sharedContainers).catch(() => {});
        newContainers = newContainers.concat(sharedContainers);
      }

      dispatch("updateContainerTags", {
        projectID: projectID,
        containers: newContainers,
        signal,
      });
      const toDelete = [];
      existingContainers.map(oldCont => {
        if (!newContainers.find(cont => cont.name == oldCont.name)) {
          toDelete.push(oldCont.id);
        }
      });

      if (toDelete.length) {
        await state.db.containers.bulkDelete(toDelete);
        await state.db.objects.where("containerID").anyOf(toDelete).delete();
      }
      const containersFromDB = await state.db.containers
        .where({ projectID })
        .toArray();

      for (let i = 0; i < newContainers.length; i++) {
        const container = newContainers[i];
        const oldContainer = containersFromDB.find(
          cont => cont.name === container.name,
        );
        let key;
        let updateObjects = true;
        let dbObjects = 0;

        if (oldContainer !== undefined) {
          key = oldContainer.id;
          dbObjects = await state.db.objects
            .where({ containerID: oldContainer.id })
            .count();
        }
        if (oldContainer !== undefined) {
          if (
            container.count === oldContainer.count &&
            container.bytes === oldContainer.bytes &&
            !(dbObjects === 0)
          ) {
            updateObjects = false;
          }
          if (container.count === 0) {
            updateObjects = false;
            await state.db.objects
              .where({ containerID: oldContainer.id })
              .delete();
          }
          await state.db.containers.update(oldContainer.id, container);
        } else {
          key = await state.db.containers.put(container);
        }

        if (updateObjects && !container.owner) {
          dispatch("updateObjects", {
            projectID: projectID,
            container: {
              id: key,
              ...container,
            },
            signal: signal,
          });
        }
      }
    },
    updateContainerTags: function (
      { state },
      { projectID, containers, signal },
    ) {
      containers.map(async container => {
        const tags =
          (await getTagsForContainer(
            projectID, container.name, signal, container.owner)) ||
          null;
        await state.db.containers
          .where({ projectID: container.projectID, name: container.name })
          .modify({ tags });
      });
    },

    updateObjects: async function (
      { state, dispatch },
      { projectID, container, signal },
    ) {
      const isSegmentsContainer = container.name.match("_segments");
      const existingObjects = await state.db.objects
        .where({ containerID: container.id })
        .toArray();
      let newObjects = [];
      let objects;
      let marker = "";
      do {
        objects = await getObjects(projectID, container.name, marker, signal);
        if (objects.length > 0) {
          objects.forEach(obj => {
            obj.container = container.name;
            obj.containerID = container.id;
            obj.tokens = isSegmentsContainer ? [] : tokenize(obj.name);
          });
          newObjects = newObjects.concat(objects);
          marker = objects[objects.length - 1].name;
        }
      } while (objects.length > 0);

      let toDelete = [];
      existingObjects.map(oldObj => {
        if (!newObjects.find(obj => obj.name === oldObj.name)) {
          toDelete.push(oldObj.id);
        }
      });
      if (toDelete.length) {
        await state.db.objects.bulkDelete(toDelete);
      }

      newObjects.map(newObj => {
        let oldObj = existingObjects.find(obj => obj.name === newObj.name);

        if (oldObj) {
          state.db.objects.update(oldObj.id, newObj);
        } else {
          state.db.objects.put(newObj);
        }
      });
      if (!isSegmentsContainer) {
        dispatch("updateObjectTags", {
          projectID,
          container,
          signal,
        });
      }
    },
    updateObjectTags: async function (
      { state, commit },
      { projectID, container, signal, sharedObjects = undefined, owner },
    ) {
      let objectList = [];

      let objects = [];
      if (sharedObjects) {
        objects = sharedObjects;
      } else {
        objects = await state.db.objects
          .where({ containerID: container.id })
          .toArray();
      }

      for (let i = 0; i < objects.length; i++) {
        // Object names end up in the URL, which has hard length limits.
        // The aiohttp complains at 8190. The maximum size
        // for object name is 1024. Set it to a safe enough amount.
        // We split the requests to prevent reaching said limits.
        objectList.push(objects[i].name);
        const url = makeGetObjectsMetaURL(
          projectID,
          container.name,
          objectList,
        );

        if (
          i === objects.length - 1 ||
          makeGetObjectsMetaURL(projectID, container.name, [
            ...objectList,
            objects[i + 1].name,
          ]).href.length >= 8190
        ) {
          let tags = await getTagsForObjects(
            projectID,
            container.name,
            objectList,
            url,
            signal,
            owner,
          );
          tags.map(item => {
            const objectName = item[0];
            const tags = item[1];
            if (sharedObjects) {
              objects.forEach(obj => {
                if (obj.name === objectName) {
                  obj.tags = tags;
                }
              });
              commit("updateObjects", objects);
            } else {
              state.db.objects
                .where({ containerID: container.id, name: objectName })
                .modify({ tags });
            }
          }),
          (objectList = []);
        }
      }
    },
    updateSharedObjects: async function (
      { commit, dispatch },
      { project, owner, container, signal },
    ) {
      let sharedObjects = [];
      let marker = "";
      let objects = [];
      do {
        objects = await getObjects(
          project,
          container.name,
          marker,
          signal,
          true,
          owner,
        ).catch(() => {
          commit("updateObjects", []);
        });

        if (objects.length > 0) {
          sharedObjects = sharedObjects.concat(objects);
          marker = objects[objects.length - 1].name;
        }
      } while (objects.length > 0);
      commit("updateObjects", sharedObjects);
      dispatch("updateObjectTags", {
        projectID: project,
        container,
        signal,
        sharedObjects,
        owner,
      });
    },
  },
});

export default store;
