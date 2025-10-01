// Vuex store for the variables that need to be globally available.
import { createStore } from "vuex";
import { isEqual, isEqualWith } from "lodash";

import {
  getContainers,
  getObjects,
} from "@/common/api";
import {
  getTagsForContainer,
  getMetadataForSharedContainer,
  getTagsForObjects,
  makeGetObjectsMetaURL,
  tokenize,
  addSegmentContainerSize,
  sortContainer,
} from "@/common/conv";

import { getDB } from "@/common/db";
import {
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
    langs: [
      { ph: "In English", value: "en" },
      { ph: "Suomeksi", value: "fi" },
    ],
    client: undefined,
    requestClient: undefined,
    socket: undefined,
    isUploading: false,
    encryptedFile: "",
    uploadProgress: undefined,
    uploadNotification: {
      visible: false,
      maximized: true,
    },
    downloadCount: 0,
    downloadProgress: undefined,
    downloadNotification: {
      visible: false,
      maximized: true,
    },
    downloadAbortReason: undefined,
    uploadEndpoint: "",
    pubkey: [],
    dropFiles: [],
    openConfirmRouteModal: false,
    routeTo: {},
    openCreateBucketModal: false,
    selectedBucketName: "",
    uploadBucket: {name: "", owner: ""},
    openUploadModal: false,
    openShareModal: false,
    openEditTagsModal: false,
    selectedObjectName: "",
    openCopyBucketModal: false,
    openDeleteModal: false,
    openAPIKeyModal: false,
    deletableObjects: [],
    isBucketCopied: false,
    sourceProjectId: "",
    uploadAbortReason: undefined,
    renderedFolders: true,
    addUploadFiles: false,
    isLoaderVisible: false,
    prevActiveEl: null,
    newBucket: "",
    sharingUpdated: false,
  },
  mutations: {
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
    setUploading(state) {
      state.isUploading = true;
      if (!state.uploadNotification.visible) {
        state.uploadNotification.visible = true;
      }
    },
    stopUploading(state, cancelled = false) {
      state.isUploading = false;
      if (!cancelled) state.isLoaderVisible = true;
    },
    setEncryptedFile(state, file) {
      state.encryptedFile = file;
    },
    toggleUploadNotification(state, payload) {
      state.uploadNotification.visible = payload;
    },
    toggleUploadNotificationSize(state) {
      state.uploadNotification.maximized =
        !state.uploadNotification.maximized;
    },
    toggleDownloadNotification(state, payload) {
      state.downloadNotification.visible = payload;
    },
    toggleDownloadNotificationSize(state) {
      state.downloadNotification.maximized =
        !state.downloadNotification.maximized;
    },
    updateProgress(state, progress) {
      state.uploadProgress = progress;
    },
    eraseProgress(state) {
      state.uploadProgress = undefined;
    },
    setDownloadAbortReason(state, payload) {
      state.downloadAbortReason = payload;
      if (state.downloadNotification.visible) {
        state.downloadNotification.visible = false;
      }
    },
    addDownload(state) {
      state.downloadCount += 1;
      if (!state.downloadNotification.visible) {
        state.downloadNotification.visible = true;
      }
    },
    removeDownload(state, all = false) {
      if (all) state.downloadCount = 0;
      else state.downloadCount -= 1;
    },
    updateDownloadProgress(state, progress) {
      state.downloadProgress = progress;
    },
    eraseDownloadProgress(state) {
      state.downloadProgress = undefined;
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
            relativePath === file.relativePath &&
            name === file.name,
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
    toggleConfirmRouteModal(state, payload) {
      state.openConfirmRouteModal = payload;
    },
    setRouteTo(state, payload) {
      state.routeTo = payload;
    },
    toggleCreateBucketModal(state, payload) {
      state.openCreateBucketModal = payload;
    },
    setBucketName(state, payload) {
      state.selectedBucketName = payload;
    },
    setUploadBucket(state, payload) {
      //separate for upload because it's needed
      //for the duration of upload for "view destination"
      state.uploadBucket.name = payload.name;
      state.uploadBucket.owner = payload.owner;
    },
    toggleUploadModal(state, payload) {
      state.openUploadModal = payload;
    },
    toggleShareModal(state, payload) {
      state.openShareModal = payload;
    },
    setUploadAbortReason(state, payload) {
      state.uploadAbortReason = payload;
    },
    setSocket(state, payload) {
      state.socket = payload;
    },
    toggleEditTagsModal(state, payload) {
      state.openEditTagsModal = payload;
    },
    setObjectName(state, payload) {
      state.selectedObjectName = payload;
    },
    toggleCopyBucketModal(state, payload) {
      state.openCopyBucketModal = payload;
    },
    toggleDeleteModal(state, payload) {
      state.openDeleteModal = payload;
    },
    toggleAPIKeyModal(state, payload) {
      state.openAPIKeyModal = payload;
    },
    setDeletableObjects(state, payload) {
      state.deletableObjects = payload;
    },
    setBucketCopiedStatus(state, payload) {
      state.isBucketCopied = payload;
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
    setNewBucket(state, payload) {
      state.newBucket = payload;
    },
    setSharingUpdated(state, payload) {
      state.sharingUpdated = payload;
    },
  },
  actions: {
    updateContainers: async function (
      { dispatch },
      { projectID, signal, routeContainer = undefined },
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

        if (containers?.length > 0) {
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
      } while (containers?.length > 0);

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

      // sort "_segments" bucket before original bucket
      // so that "_segments" bucket could be updated first
      newContainers = sortContainer(newContainers);

      for (let i = 0; i < newContainers.length; i++) {
        addSegmentContainerSize(newContainers[i], newContainers);
      }

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

          // Check if shared containers should be updated objects
          if (
            container.count === oldContainer.count &&
            container.bytes === oldContainer.bytes &&
            container.owner && dbObjects === 0
          ) {
            updateObjects = false;
          }
          await getDB().containers.update(oldContainer.id, container);
        } else {
          key = await getDB().containers.put(container);
        }

        if (routeContainer && container.owner) {
          if (container.name !== routeContainer &&
            container.name !== `${routeContainer}_segments`) {
          //Update the object cache only for shared container and segments
          //in current route to avoid objects flashing in UI
            updateObjects = false;
          }
        }

        if (updateObjects && !container.name.endsWith("_segments") ) {
          // Have a separate array contained containers that
          // their objects should be updated
          containers_to_update_objects.push({ container, key });
        }
      }

      await dispatch("updateContainerTags", {
        projectID: projectID,
        containers: newContainers,
        signal,
      });
      return containers_to_update_objects;
    },
    updateContainerTags: async function (_, {
      projectID, containers, signal,
    }) {
      const idbContainers = await getDB()
        .containers.where({ projectID })
        .toArray();

      for (let i = 0; i < containers.length; i++) {
        const container = containers[i];
        // Update tags for non-segment containers and for those that
        // have difference between new tags and existing tags from IDB
        if (!container.name.endsWith("_segments")) {
          const tags =
          (await getTagsForContainer(
            projectID, container.name, signal, container.owner)) ||
          null;

          idbContainers.forEach(async (cont) => {
            if (cont.name === container.name && !isEqual(tags, cont.tags)) {
              await getDB().containers
                .where({ projectID, name: container.name })
                .modify({ tags });
            }
          });
        }
      }
    },
    updateObjects: async function (
      { dispatch, state },
      { projectID, owner, container, signal, updateTags },
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
        if (owner) {
          objects = await getObjects(
            projectID,
            container.name,
            marker,
            signal,
            true,
            owner,
          );
        } else {
          objects = await getObjects(
            projectID, container.name, marker, signal);
        }

        if (objects.length > 0) {
          objects.forEach(obj => {
            obj.container = container.name;
            obj.containerID = container.id;
            obj.tokens = isSegmentsContainer ? [] : tokenize(obj.name);
            if (owner) {
              obj.containerOwner = container.owner;
            }
          });
          newObjects = newObjects.concat(objects);
          marker = objects[objects.length - 1].name;
        }
      } while (objects.length > 0);

      let toDelete = [];

      for (let i = 0; i < existingObjects.length; i++) {
        const oldObj = existingObjects[i];
        if (!newObjects.find(obj => obj.name === oldObj.name &&
          obj.containerID === oldObj.containerID)
        ) {
          toDelete.push(oldObj.id);
        }
      }

      if (toDelete.length) {
        await getDB().objects.bulkDelete(toDelete);
      }

      if (!isSegmentsContainer) {
        const segment_objects = await getObjects(
          projectID,
          `${container.name}_segments`,
          "",
          signal,
          !!owner,
          owner ? owner : "",
        );

        if (newObjects.length === segment_objects.length) {
          // Find the segments of an object and
          // update the original objects size accordingly
          for (let i = 0; i < newObjects.length; i++) {
            if (segment_objects[i] && newObjects[i].bytes === 0) {
              newObjects[i].bytes = segment_objects[i].bytes;
            }
            else if (!segment_objects[i] && state.isLoaderVisible) {
            /* When cancelling the upload of large amount of files
              or big files sizes, the original bucket could have
              more objects than segment bucket which results in the
              last updated file has size 0 (segment bucket doesn't have it)
              Therefore it's better to remove that file.
            */
              newObjects.splice(i, 1);
            }
          }
        } else if (segment_objects.length > newObjects.length) {
          /*
            For uploaded objects having size > 5GiB,
            their equivalent segment_objects are split off into
            multiple segments (~5GiB/each) of which combined size
            in total is roughly equal to the original uploaded file.
            The regular objects are not separated into segments, hence
            the number of segment_objects > regular objects.
          */
          for (let i = 0; i < newObjects.length; i++) {
            // Filter equivalent segment objects
            const filteredSegmentObjects = segment_objects.filter(obj =>
              obj.name.includes(newObjects[i].name),
            );
            // Calculate total size of equivalent segment objects
            const totalSegmentSize = filteredSegmentObjects.reduce(
              (totalSize, obj) =>
                obj.name.includes(newObjects[i].name) ?
                  totalSize + obj.bytes : null, 0,
            );
            newObjects[i].bytes = totalSegmentSize;
          }
        }
        updateContainerLastmodified(projectID, container, newObjects);
      }

      for (let i = 0; i < newObjects.length; i++) {
        const newObj = newObjects[i];
        let oldObj = existingObjects.find(obj => obj.name === newObj.name &&
          obj.containerID === newObj.containerID,
        );

        // Check if oldObj and newObj have the same properties
        // except the key "id", because key "id" comes from oldObj in IDB
        const isEqualObject = isEqualWith(oldObj, newObj, (oldObj, newObj) => {
          if (oldObj?.id && !newObj?.id) return true;
        });

        if (oldObj) {
          if (isEqualObject) await getDB().objects.update(oldObj.id, newObj);
        } else {
          await getDB().objects.put(newObj);
        }
      }

      if (!isSegmentsContainer && updateTags) {
        await dispatch("updateObjectTags", {
          projectID,
          container,
          signal,
          owner,
        });
      }
    },
    updateObjectTags: async function (
      _,
      { projectID, container, signal, owner },
    ) {
      let objectList = [];
      const allTags = [];

      const objects = await getDB().objects
        .where({ containerID: container.id })
        .toArray();

      for (let i = 0; i < objects.length; i++) {
        // Object names end up in the URL, which has hard length limits.
        // The aiohttp complains at 8190. The maximum size
        // for object name is 1024. Set it to a safe enough amount.
        // We split the requests to prevent reaching said limits.
        objectList.push(objects[i].name);

        if (
          i === objects.length - 1 ||
          makeGetObjectsMetaURL(projectID, container.name, [
            ...objectList,
            objects[i + 1].name,
          ]).href.length >= 8190
        ) {
          const url = makeGetObjectsMetaURL(
            projectID,
            container.name,
            objectList,
          );

          let tags = await getTagsForObjects(
            projectID,
            container.name,
            objectList,
            url,
            signal,
            owner,
          );

          allTags.push(tags);
          objectList = [];
        }
      }

      if (allTags.flat().length > 0) {
        const newObjects = objects.map((obj, index) => {
          const tags = allTags.flat()[index][1];
          return {...obj, tags};
        });
        await getDB().objects.bulkPut(newObjects);
      }
    },
  },
});

export default store;
