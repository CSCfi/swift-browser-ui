// Vuex store for the variables that need to be globally available.
import { createStore } from "vuex";

import {
  getContainers,
  getObjects,
} from "@/common/api";
import {
  DEV,
  getTagsForContainer,
  getMetadataForSharedContainer,
  getTagsForObjects,
  makeGetObjectsMetaURL,
  tokenize,
  addSegmentContainerSize,
  getSegmentObjects,
  sortContainer,
} from "@/common/conv";

import { getDB } from "@/common/db";
import {
  getSharingContainers,
  getSharedContainers,
  getContainerLastmodified,
  updateContainerLastmodified,
} from "@/common/globalFunctions";

const store = createStore({
  state: {
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
    uploadNotificationClosable: false,
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
    openDeleteModal: false,
    openTokenModal: false,
    deletableObjects: [],
    isFolderCopied: false,
    sourceProjectId: "",
    uploadAbort: undefined,
    renderedFolders: true,
    addUploadFiles: false,
    isLoaderVisible: false,
    prevActiveEl: null,
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
      state.isLoaderVisible = true;
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
    appendDropFiles(state, file) {
      state.dropFiles.push(file);
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
      state.uploadNotificationClosable = false;
    },
    eraseCurrentUpload(state) {
      delete state.currentUpload;
      state.currentUpload = undefined;
      state.uploadNotificationClosable = true;
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
    toggleDeleteModal(state, payload) {
      state.openDeleteModal = payload;
    },
    toggleTokenModal(state, payload) {
      state.openTokenModal = payload;
    },
    setDeletableObjects(state, payload) {
      state.deletableObjects = payload;
    },
    setFolderCopiedStatus(state, payload) {
      state.isFolderCopied = payload;
    },
    setSourceProjectId(state, payload) {
      state.sourceProjectId = payload;
    },
    toggleRenderedFolders(state, payload) {
      state.renderedFolders = payload;
    },
    setFilesAdded(state, payload) {
      state.addUploadFiles = payload;
    },
    setLoaderVisible(state, payload) {
      state.isLoaderVisible = payload;
    },
    setPreviousActiveEl(state, payload) {
      state.prevActiveEl = payload;
    },
  },
  actions: {
    updateContainers: async function (
      { dispatch },
      { projectID, signal },
    ) {
      const existingContainers = await getDB()
        .containers.where({ projectID })
        .toArray();

      if (!signal) {
        const controller = new AbortController();
        signal = controller.signal;
      }

      let containers;
      let marker = "";
      let newContainers = [];
      do {
        containers = [];
        containers = await getContainers(projectID, marker, signal)
          .catch(() => {});

        if (containers.length > 0) {
          containers.forEach(cont => {
            cont.tokens = cont.name.endsWith("_segments") ?
              [] : tokenize(cont.name);
            cont.projectID = projectID;
            cont.last_modified =  cont.name.endsWith("_segments") ?
              cont.last_modified :
              getContainerLastmodified(existingContainers, cont);
          });
          newContainers = newContainers.concat(containers);
          marker = containers[containers.length - 1].name;
        }
      } while (containers.length > 0);

      const sharedContainers = await getSharedContainers(projectID, signal);
      if (sharedContainers.length > 0) {
        for (let i in sharedContainers) {
          let cont = sharedContainers[i];
          const { bytes, count } = await getMetadataForSharedContainer(
            projectID,
            cont.container,
            signal,
            cont.owner,
          );
          cont.tokens =  cont.container.endsWith("_segments") ?
            [] : tokenize(cont.container);
          cont.projectID = projectID;
          cont.bytes = bytes;
          cont.count = count;
          cont.name = cont.container;

          const idb_last_modified = getContainerLastmodified(
            existingContainers, cont);
          cont.last_modified = !cont.container.endsWith("_segments") &&
            idb_last_modified  && idb_last_modified > cont.sharingdate ?
            idb_last_modified : cont.sharingdate;
        }

        await getDB()
          .containers.bulkPut(sharedContainers)
          .catch(() => {});
        newContainers = newContainers.concat(sharedContainers);
      }

      dispatch("updateContainerTags", {
        projectID: projectID,
        containers: newContainers,
        signal,
      });

      const toDelete = [];
      for (let i = 0; i < existingContainers.length; i++) {
        const oldCont = existingContainers[i];
        if (!newContainers.find(cont => cont.name == oldCont.name)) {
          toDelete.push(oldCont.id);
        }
      }

      if (toDelete.length) {
        await getDB().containers.bulkDelete(toDelete);
        await getDB().objects.where("containerID").anyOf(toDelete).delete();
      }
      const containersFromDB = await getDB()
        .containers.where({ projectID })
        .toArray();

      // sort "_segments" folder before original folder
      // so that "_segments" folder could be updated first
      newContainers = sortContainer(newContainers);

      for (let i = 0; i < newContainers.length; i++) {
        addSegmentContainerSize(newContainers[i], newContainers);
      }

      const sharingContainers = await getSharingContainers(projectID, signal);
      let containers_to_update_objects = [];
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
          dbObjects = await getDB()
            .objects.where({ containerID: oldContainer.id })
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
            await getDB()
              .objects.where({ containerID: oldContainer.id })
              .delete();
          }
          await getDB().containers.update(oldContainer.id, container);
        } else {
          key = await getDB().containers.put(container);
        }

        if (updateObjects ||
          sharingContainers.some(cont => cont === container.name)
        ) {
          // Have a separate array contained containers that
          // their objects should be updated
          containers_to_update_objects.push({ container, key });
        }
      }

      // Updating objects goes sequentially:
      // Update all objects inside a segment_container first
      // before updating objects inside original container
      const dispatchUpdateOjects = async () => {
        for (let i = 0; i < containers_to_update_objects.length; i++) {
          const currentContainer = containers_to_update_objects[i];

          if (!currentContainer.container.owner) {
            await dispatch("updateObjects", {
              projectID: projectID,
              container: {
                id: currentContainer.key,
                ...currentContainer.container,
              },
              signal: signal,
            });
          } else {
            await dispatch("updateSharedObjects", {
              projectID: projectID,
              owner: currentContainer.container.owner,
              container: {
                id: currentContainer.key,
                ...currentContainer.container,
              },
              signal: signal,
            });
          }
        }
      };

      if (containers_to_update_objects.length > 0) dispatchUpdateOjects();
    },
    updateContainerTags: async function (_, { projectID, containers, signal }) {
      for (let i = 0; i < containers.length; i++) {
        const container = containers[i];
        const tags =
          (await getTagsForContainer(
            projectID, container.name, signal, container.owner)) ||
          null;
        await getDB().containers
          .where({ projectID: container.projectID, name: container.name })
          .modify({ tags });
      }
    },

    updateObjects: async function (
      { dispatch, commit, state },
      { projectID, container, signal },
    ) {
      const isSegmentsContainer = container.name.endsWith("_segments");
      const existingObjects = await getDB().objects
        .where({ containerID: container.id })
        .toArray();

      let newObjects = [];
      let objects;
      let marker = "";

      if (!signal) {
        const controller = new AbortController();
        signal = controller.signal;
      }

      do {
        objects = await getObjects(
          projectID, container.name, marker, signal);

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

      for (let i = 0; i < existingObjects.length; i++) {
        const oldObj = existingObjects[i];
        if (!newObjects.find(obj => obj.name === oldObj.name)) {
          toDelete.push(oldObj.id);
        }
      }

      if (toDelete.length) {
        await getDB().objects.bulkDelete(toDelete);
      }

      if (!isSegmentsContainer) {
        const segment_objects = await getSegmentObjects(projectID, container);

        for (let i = 0; i < newObjects.length; i++) {
          if (segment_objects[i]) {
            newObjects[i].bytes = segment_objects[i].bytes;
          }
          else if (!segment_objects[i] && state.isLoaderVisible) {
            /* When cancelling the upload of large amount of files
              or big files sizes, the original folder could have
              more objects than segment folder which results in the
              last updated file has size 0 (segment folder doesn't have it)
              Therefore it's better to remove that file.
            */
            newObjects.splice(i, 1);
          }
        }
        updateContainerLastmodified(projectID, container, newObjects);
      }

      for (let i = 0; i < newObjects.length; i++) {
        const newObj = newObjects[i];

        let oldObj = existingObjects.find(obj => obj.name === newObj.name);

        if (oldObj) {
          await getDB().objects.update(oldObj.id, newObj);
        } else {
          try {
            await getDB().objects.put(newObj);
          } catch (e) {
            if (DEV) console.error("Constraint error: " + e.message);
          }
        }
        if (!isSegmentsContainer && i === newObjects.length - 1) {
          commit("setLoaderVisible", false);
        }
      }

      if (!isSegmentsContainer) {
        dispatch("updateObjectTags", {
          projectID,
          container,
          signal,
        });

      }
    },
    updateObjectTags: async function (
      { commit },
      { projectID, container, signal, sharedObjects = undefined, owner },
    ) {
      let objectList = [];

      let objects = [];
      if (sharedObjects) {
        objects = sharedObjects;
      } else {
        objects = await getDB().objects
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

          tags.forEach(item => {
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
              getDB().objects
                .where({ containerID: container.id, name: objectName })
                .modify({ tags });
            }
          }),
          (objectList = []);
        }
      }
    },
    updateSharedObjects: async function (
      { commit, dispatch, state },
      { projectID, owner, container, signal },
    ) {
      const isSegmentsContainer = container.name.endsWith("_segments");
      let sharedObjects = [];
      let marker = "";
      let objects = [];

      if (!signal) {
        const controller = new AbortController();
        signal = controller.signal;
      }

      do {
        objects = await getObjects(
          projectID,
          container.name,
          marker,
          signal,
          true,
          owner,
        ).catch(() => {
          commit("updateObjects", []);
        });

        if (objects?.length > 0) {
          objects.forEach(obj => {
            obj.container = container.name;
            obj.containerID = container.id;
            obj.tokens = isSegmentsContainer ? [] : tokenize(obj.name);
          });
          sharedObjects = sharedObjects.concat(objects);
          marker = objects[objects.length - 1].name;
        }
      } while (objects?.length > 0);

      if (!isSegmentsContainer) {
        const segment_objects = await getObjects(
          projectID,
          `${container.name}_segments`,
          "",
          signal,
          true,
          owner,
        );
        for (let i = 0; i < sharedObjects.length; i++) {
          if (segment_objects[i]) {
            sharedObjects[i].bytes = segment_objects[i].bytes;
          }
          if (!isSegmentsContainer && i === sharedObjects.length - 1) {
            commit("setLoaderVisible", false);
          }
        }
      }

      commit("updateObjects", [...state.objectCache, sharedObjects]);

      updateContainerLastmodified(projectID, container, sharedObjects);

      dispatch("updateObjectTags", {
        projectID: projectID,
        container,
        signal,
        sharedObjects,
        owner,
      });
    },
  },
});

export default store;
