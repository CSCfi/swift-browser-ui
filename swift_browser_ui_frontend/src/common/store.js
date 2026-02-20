// Pinia store for the variables that need to be globally available.
import { defineStore } from "pinia";

const useStore = defineStore("global", {
  state: () => ({
    projects: [],
    active: {},
    uname: "",
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
    headersProcessed: 0,
    headersTotal: 0,
  }),
  getters: {
    multipleProjects: (state) => state.projects.length > 1,
  },
  actions: {
    setProjects(newProjects) {
      // Update the project listing in store
      this.projects = newProjects;
    },
    setActive(newActive) {
      // Update the active project in store
      this.active = newActive;
    },
    setUname(newUname) {
      // Update the username in store
      this.uname = newUname;
    },
    setSharingClient(newClient) {
      this.sharingClient = newClient;
    },
    setRequestClient(newClient) {
      this.requestClient = newClient;
    },
    setUploading() {
      this.isUploading = true;
      if (!this.uploadNotification.visible) {
        this.uploadNotification.visible = true;
      }
    },
    stopUploading(cancelled = false) {
      this.isUploading = false;
      if (!cancelled) this.isLoaderVisible = true;
    },
    setDeleting(payload) {
      this.isDeleting = payload;
    },
    setEncryptedFile(file) {
      this.encryptedFile = file;
    },
    toggleUploadNotification(payload) {
      this.uploadNotification.visible = payload;
    },
    toggleUploadNotificationSize() {
      this.uploadNotification.maximized =
        !this.uploadNotification.maximized;
    },
    toggleDownloadNotification(payload) {
      this.downloadNotification.visible = payload;
    },
    toggleDownloadNotificationSize() {
      this.downloadNotification.maximized =
        !this.downloadNotification.maximized;
    },
    updateProgress(progress) {
      this.uploadProgress = progress;
    },
    eraseProgress() {
      this.uploadProgress = undefined;
    },
    setDownloadAbortReason(payload) {
      this.downloadAbortReason = payload;
      if (this.downloadNotification.visible) {
        this.downloadNotification.visible = false;
      }
    },
    addDownload() {
      this.downloadCount += 1;
      if (!this.downloadNotification.visible) {
        this.downloadNotification.visible = true;
      }
    },
    removeDownload(all = false) {
      if (all) this.downloadCount = 0;
      else this.downloadCount -= 1;
    },
    updateDownloadProgress(progress) {
      this.downloadProgress = progress;
    },
    eraseDownloadProgress() {
      this.downloadProgress = undefined;
    },
    setUploadEndpoint(endpoint) {
      this.uploadEndpoint = endpoint;
    },
    appendDropFiles(file) {
      this.dropFiles.push(file);
    },
    eraseDropFile(file) {
      this.dropFiles.splice(
        this.dropFiles.findIndex(
          ({ name, relativePath }) =>
            relativePath === file.relativePath &&
            name === file.name,
        ),
        1,
      );
    },
    eraseDropFiles() {
      this.dropFiles = [];
    },
    appendPubKey(key) {
      this.pubkey.push(key);
    },
    erasePubKey() {
      this.pubkey = [];
    },
    toggleConfirmRouteModal(payload) {
      this.openConfirmRouteModal = payload;
    },
    setRouteTo(payload) {
      this.routeTo = payload;
    },
    toggleCreateBucketModal(payload) {
      this.openCreateBucketModal = payload;
    },
    setBucketName(payload) {
      this.selectedBucketName = payload;
    },
    setUploadBucket(payload) {
      //separate for upload because it's needed
      //for the duration of upload for "view destination"
      this.uploadBucket.name = payload.name;
      this.uploadBucket.owner = payload.owner;
    },
    toggleUploadModal(payload) {
      this.openUploadModal = payload;
    },
    toggleShareModal(payload) {
      this.openShareModal = payload;
    },
    setUploadAbortReason(payload) {
      this.uploadAbortReason = payload;
    },
    setSocket(payload) {
      this.socket = payload;
    },
    toggleEditTagsModal(payload) {
      this.openEditTagsModal = payload;
    },
    setObjectName(payload) {
      this.selectedObjectName = payload;
    },
    toggleCopyBucketModal(payload) {
      this.openCopyBucketModal = payload;
    },
    toggleDeleteModal(payload) {
      this.openDeleteModal = payload;
    },
    toggleAPIKeyModal(payload) {
      this.openAPIKeyModal = payload;
    },
    setDeletableObjects(payload) {
      this.deletableObjects = payload;
    },
    setSourceProjectId(payload) {
      this.sourceProjectId = payload;
    },
    toggleRenderedFolders(payload) {
      this.renderedFolders = payload;
    },
    setFilesAdded(payload) {
      this.addUploadFiles = payload;
    },
    setLoaderVisible(payload) {
      this.isLoaderVisible = payload;
    },
    setPreviousActiveEl(payload) {
      this.prevActiveEl = payload;
    },
    setNewBucket(payload) {
      this.newBucket = payload;
    },
    setSharingUpdated(payload) {
      this.sharingUpdated = payload;
    },
    setS3Endpoint(payload) {
      this.s3endpoint = payload;
    },
    setS3Client(payload) {
      this.s3client = payload;
    },
    setS3Upload(payload) {
      this.s3upload = payload;
    },
    setS3Download(payload) {
      this.s3download = payload;
    },
    setWorkersInitializing(payload) {
      this.workersInitializing = payload;
    },
    setHeadersTotal(payload) {
      this.headersTotal = payload;
    },
    setHeadersProcessed(payload) {
      this.headersProcessed = payload;
    },
  },
});

export default useStore;
