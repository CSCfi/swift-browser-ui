// Vuex store for the variables that need to be globally available.
import { createStore } from "vuex";

import {
  awsListBuckets,
  awsBulkAddBucketListCors,
} from "@/common/api";
import {
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
import { DEV } from "@/common/conv";

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
    isDeleting: false,
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
    submitConfig: {
      sd_submit_user: "",
      sd_submit_id: "",
      sd_submit_endpoint: "",
    },
    s3endpoint: "",
    s3client: undefined,
    s3upload: undefined,
    s3download: undefined,
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
    setDeleting(state, payload) {
      state.isDeleting = payload;
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
    setSubmitConfig(state, payload) {
      state.submitConfig = payload;
    },
    setS3Endpoint(state, payload) {
      state.s3endpoint = payload;
    },
    setS3Client(state, payload) {
      state.s3client = payload;
    },
    setS3Upload(state, payload) {
      state.s3upload = payload;
    },
    setS3Download(state, payload) {
      state.s3download = payload;
    },
  },
  actions: {
    updateContainers: async function (
      {},
      { projectID, signal },
    ) {
      const existingContainers = await getDB()
        .containers.where({ projectID })
        .toArray();

      if (!signal) {
        const controller = new AbortController();
        signal = controller.signal;
      }

      let buckets;
      let continuationToken = undefined;
      let newBuckets = [];
      let newBucketsPage = [];

      do {
        buckets = [];

        // Get a list of buckets and check bucket CORS
        buckets = await awsListBuckets(projectID, continuationToken, 100);
        if (buckets?.Buckets?.length > 0) {
          await awsBulkAddBucketListCors(projectID, buckets.Buckets.map(
            bucket => bucket.Name,
          ));
        }

        if (buckets?.Buckets?.length > 0) {
          for (const bucket of buckets.Buckets) {

            let newBucket = {
              name: bucket.Name,
              tokens: tokenize(bucket.Name),
              projectID: projectID,
              tags: [],
              last_modified: bucket.CreationDate.toISOString(),
              bytes: 0,
              count: 0,
            };
            newBucketsPage.push(newBucket);

            if (newBucketsPage.length >= 100) {
              try {
                await getDB().containers.bulkPut(newBucketsPage);
              } catch (err) {
                if (DEV) console.log(err);
              }

              newBucketsPage = [];
            }

            newBuckets.push(newBucket);
          }
        }

        if (buckets?.ContinuationToken) {
          continuationToken = buckets.ContinuationToken;
        } else {
          break;
        }
        // May be unnecessary, S3 should omit the continuation token on
        // final page
        if (buckets?.Buckets?.length < 10) {
          break;
        }
      } while (buckets?.Buckets?.length > 0 && continuationToken);

      const sharedContainers = await getSharedContainers(projectID, signal);

      if (sharedContainers.length > 0) {
        for (let i in sharedContainers) {
          let cont = sharedContainers[i];
          cont.tokens =  cont.container.endsWith("_segments") ?
            [] : tokenize(cont.container);
          cont.projectID = projectID;
          cont.bytes = 0;
          cont.count = 0;
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
        newBuckets = newBuckets.concat(sharedContainers);
      }

      const toDelete = [];
      for (let i = 0; i < existingContainers.length; i++) {
        const oldCont = existingContainers[i];
        if (!newBuckets.find(cont => cont.name == oldCont.name)) {
          toDelete.push(oldCont.id);
        }
      }

      if (toDelete.length) {
        await getDB().containers.bulkDelete(toDelete);
      }
      const containersFromDB = await getDB()
        .containers.where({ projectID })
        .toArray();

      // sort "_segments" bucket before original bucket
      // so that "_segments" bucket could be updated first
      newBuckets = sortContainer(newBuckets);

      for (let i = 0; i < newBuckets.length; i++) {
        addSegmentContainerSize(newBuckets[i], newBuckets);
      }

      for (let i = 0; i < newBuckets.length; i++) {
        const container = newBuckets[i];
        const oldContainer = containersFromDB.find(
          cont => cont.name === container.name,
        );

        if (oldContainer !== undefined) {
          await getDB().containers.update(oldContainer.id, container);
        } else {
          await getDB().containers.put(container);
        }
      }
    },
  },
});

export default store;
