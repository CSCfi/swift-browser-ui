// Vuex store for the variables that need to be globally available.
import { createStore } from "vuex";

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
    sharingClient: undefined,
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
    sourceProjectId: "",
    uploadAbortReason: undefined,
    renderedFolders: true,
    addUploadFiles: false,
    isLoaderVisible: false,
    prevActiveEl: null,
    newBucket: "",
    sharingUpdated: false,
    s3endpoint: "",
    s3client: undefined,
    s3upload: undefined,
    s3download: undefined,
    workersInitializing: true,
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
      state.sharingClient = newClient;
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
    setWorkersInitializing(state, payload) {
      state.workersInitializing = payload;
    },
  },
});

export default store;
