// Project main imports
import { createApp } from "vue";
import BrowserPage from "@/pages/BrowserPage.vue";
import router from "@/common/router";

// Project Vue components
import BrowserMainNavbar from "@/components/BrowserMainNavbar.vue";
import BrowserSecondaryNavbar from "@/components/BrowserSecondaryNavbar.vue";
import ConfirmRouteModal from "@/components/ConfirmRouteModal.vue";
import CreateFolderModal from "@/components/CreateFolderModal.vue";
import UploadModal from "@/components/UploadModal.vue";
import EditTagsModal from "@/components/EditTagsModal.vue";
import ShareModal from "@/components/ShareModal.vue";
import CopyFolderModal from "@/components/CopyFolderModal.vue";
import DeleteModal from "@/components/DeleteModal.vue";
import TokenModal from "@/components/TokenModal.vue";

// CSC UI things
import { applyPolyfills, defineCustomElements } from "csc-ui/dist/loader";
import { vControl } from "@/common/csc-ui-vue-directive";

// Project JS functions
import { i18n } from "@/common/i18n";
import { getUser, signedFetch } from "@/common/api";
import { getProjects } from "@/common/api";

// Import SharingView and Request API
import SwiftXAccountSharing from "@/common/swift_x_account_sharing_bind";
import SwiftSharingRequest from "@/common/swift_sharing_request_bind";

// Import container ACL sync
import { syncContainerACLs, DEV } from "@/common/conv";
import checkIDB from "@/common/idb_support";

// Import project state
import store from "@/common/store";

// Import project css
import "@/css/prod.scss";

// Upload and direct download notification handler
import ProgressNotification from "@/components/ProgressNotification.vue";

//Custom footer element
import CFooter from "@/components/CFooter.vue";

import { getDB } from "@/common/db";
import UploadSocket from "@/common/socket";

// Import global functions
import { removeFocusClass } from "@/common/keyboardNavigation";

checkIDB().then(result => {
  if (!result) {
    window.location.pathname = "/";
  }
});

window.onerror = function (error) {
  if (DEV) console.log("Global error", error);
};
window.addEventListener("unhandledrejection", function (event) {
  if (DEV) console.log("unhandledrejection", event);
  event.preventDefault();
  event.stopPropagation();
});
window.addEventListener("rejectionhandled", function (event) {
  if (DEV) console.log("rejectionhandled", event);
  event.preventDefault();
  event.stopPropagation();
});

// Configure csc-ui
applyPolyfills().then(() => {
  defineCustomElements();
});

const app = createApp({
  components: {
    CFooter,
    BrowserMainNavbar,
    BrowserSecondaryNavbar,
    ConfirmRouteModal,
    CreateFolderModal,
    UploadModal,
    ProgressNotification,
    EditTagsModal,
    ShareModal,
    CopyFolderModal,
    DeleteModal,
    TokenModal,
  },
  data: function () {
    return {
      files: [],
    };
  },
  computed: {
    projects() {
      return this.$store.state.projects;
    },
    multipleProjects() {
      return this.$store.state.multipleProjects;
    },
    langs() {
      return this.$store.state.langs;
    },
    active() {
      return this.$store.state.active;
    },
    user() {
      return this.$store.state.uname;
    },
    isUploading() {
      return this.$store.state.isUploading;
    },
    displayUploadNotification() {
      return this.$store.state.uploadNotification.visible;
    },
    displayDownloadNotification() {
      return this.$store.state.downloadNotification.visible;
    },
    openConfirmRouteModal: {
      get() {
        return this.$store.state.openConfirmRouteModal;
      },
      set(newState) {
        return newState;
      },
    },
    openCreateFolderModal: {
      get() {
        return this.$store.state.openCreateFolderModal;
      },
      set(newState) {
        return newState;
      },
    },
    openUploadModal: {
      get() {
        return this.$store.state.openUploadModal;
      },
      set(newState) {
        return newState;
      },
    },
    openEditTagsModal: {
      get() {
        return this.$store.state.openEditTagsModal;
      },
      set(newState) {
        return newState;
      },
    },
    openCopyFolderModal: {
      get() {
        return this.$store.state.openCopyFolderModal;
      },
      set(newState) {
        return newState;
      },
    },
    openDeleteModal: {
      get() {
        return this.$store.state.openDeleteModal;
      },
      set(newState) {
        return newState;
      },
    },
    openShareModal: {
      get() {
        return this.$store.state.openShareModal;
      },
      set() { },
    },
    openTokenModal: {
      get() {
        return this.$store.state.openTokenModal;
      },
      set() { },
    },
    prevActiveEl() {
      return this.$store.state.prevActiveEl;
    },
    socket() {
      return this.$store.state.socket;
    },
  },
  watch: {
    openCreateFolderModal: function () {
      if (this.openCreateFolderModal) {
        // Set the modal to scroll to top whenever it's opened
        const el = document.getElementById("createFolder-modal-content");
        el.scrollTo(0, 0);
      }
    },
    openUploadModal: function () {
      if (this.openUploadModal) {
        // Set the modal to scroll to top whenever it's opened
        const el = document.getElementById("upload-modal-content");
        el.scrollTo(0, 0);
      }
    },
  },
  created() {
    document.title = this.$t("message.program_name");

    let initialize = async () => {
      let active;
      let user = await getUser();
      let projects = await getProjects();
      this.$store.commit("setUname", user);
      this.$store.commit("setProjects", projects);

      const existingProjects = await getDB().projects
        .toCollection()
        .primaryKeys();
      await getDB().projects.bulkPut(projects);


      const toDelete = [];
      existingProjects.map(async oldProj => {
        if (!projects.find(proj => proj.id === oldProj)) {
          toDelete.push(oldProj);
        }
      });
      if (toDelete.length) {
        await getDB().projects.bulkDelete(toDelete);
        const containersCollection = await getDB().containers
          .where("projectID")
          .anyOf(toDelete);
        const containers = await containersCollection.primaryKeys();
        await containersCollection.delete();
        await getDB().objects
          .where("containerID")
          .anyOf(containers)
          .delete();
      }

      if (
        this.$route.params.user === undefined
        || this.$route.params.project === undefined
      ) {
        active = projects[0];
      } else {
        active =
          projects[
            projects.indexOf(
              projects.find(e => e.id == this.$route.params.project),
            )
          ];
      }
      this.$store.commit("setActive", active);

      if (document.location.pathname == "/browse") {
        this.$router.replace({
          name: "AllFolders",
          params: {
            project: active.id,
            user: user,
          },
        });
      }
      let discovery = await fetch("/discover");
      discovery = await discovery.json();
      if (discovery.sharing_endpoint) {
        this.$store.commit(
          "setSharingClient",
          new SwiftXAccountSharing(
            discovery.sharing_endpoint,
            document.location.origin,
          ),
        );

        // Cache id information
        await this.$store.state.client.projectCacheIDs(
          this.$store.state.active.id,
          this.$store.state.active.name,
        );
      }
      if (discovery.request_endpoint) {
        this.$store.commit(
          "setRequestClient",
          new SwiftSharingRequest(
            discovery.request_endpoint,
            document.location.origin,
          ),
        );
      }
      if (discovery.upload_endpoint) {
        this.$store.commit(
          "setUploadEndpoint",
          discovery.upload_endpoint,
        );

        let key = await signedFetch(
          "GET",
          discovery.upload_endpoint,
          `/cryptic/${this.active.name}/keys`,
        );
        key = await key.text();
        key = `-----BEGIN CRYPT4GH PUBLIC KEY-----\n${key}\n-----END CRYPT4GH PUBLIC KEY-----\n`;
        this.$store.commit("appendPubKey", key);
      }

      this.initSocket().then(
        () => {if (DEV) console.log("Initialized the websocket.");},
      );
    };
    initialize().then(() => {
      if(DEV) console.log("Initialized successfully.");
    });
    setTimeout(this.containerSyncWrapper, 10000);
  },
  mounted() {
    document
      .getElementById("mainContainer")
      .addEventListener("keydown", this.onKeydown);
  },
  methods: {
    initSocket: async function () {
      // Open the upload and download webworkers
      let available = await navigator.storage.estimate();
      // If there's less than 50GiB of storage available, try getting more.
      // We're probably on Firefox, persisting should grant us more.
      if (available.quota < 53687091200) {
        await navigator.storage.persist();
        if (await navigator.storage.persisted()) {
          if (DEV) console.log("Storage persisted.");
          // Update the quotas
          available = await navigator.storage.estimate();
        } else {
          if (DEV) console.log(
            "Couldn't persist storage, "
            + "possible limited save space for downloads.",
          );
        }
      }

      if (DEV) console.log(
        `${available.usage}/${available.quota} of available storage used.`,
      );
      if (DEV) console.log(
        "Any downloads need to fit under this size when downloading.",
      );

      let workers = new UploadSocket(
        this.$store.state.active,
        this.$store.state.active.id,
        this.$store,
        this.$t,
      );
      workers.openSocket();
      this.$store.commit("setSocket", workers);
    },
    containerSyncWrapper: function () {
      syncContainerACLs(this.$store);
    },
    cancelUpload: function(container) {
      this.socket.cancelUpload(container);
    },
    onKeydown: function (e) {
      if (e.key === "Tab" && this.prevActiveEl &&
        e.target === this.prevActiveEl) {
        if(this.prevActiveEl.classList.contains("button-focus")) {
          removeFocusClass(this.prevActiveEl);
          this.$store.commit("setPreviousActiveEl", null);
        }
      }
    },
  },
  ...BrowserPage,
});

app.use(i18n);
app.use(router);
app.use(store);
app.directive("csc-control", vControl);

app.config.errorHandler = function (err, vm, info) {
  if (DEV) console.log("Vue error: ", err, vm, info);
};
app.config.warnHandler = function (msg, vm, info) {
  if (DEV) console.log("Vue warning: ", msg, vm, info);
};

router.afterEach((to) => {
  if (!to.name) {
    window.location.pathname = "/notfound";
  }
});
router.isReady().then(() => app.mount("#app"));
