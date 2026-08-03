// Project main imports
import { createApp } from "vue";
import { createPinia } from "pinia";
import BrowserPage from "@/pages/BrowserPage.vue";
import router from "@/common/router";

// Project Vue components
import BrowserMainNavbar from "@/components/BrowserMainNavbar.vue";
import BrowserSecondaryNavbar from "@/components/BrowserSecondaryNavbar.vue";
import ConfirmRouteModal from "@/components/ConfirmRouteModal.vue";
import CreateBucketModal from "@/components/CreateBucketModal.vue";
import UploadModal from "@/components/UploadModal.vue";
import EditTagsModal from "@/components/EditTagsModal.vue";
import ShareModal from "@/components/ShareModal.vue";
import CopyBucketModal from "@/components/CopyBucketModal.vue";
import DeleteModal from "@/components/DeleteModal.vue";
import APIKeyModal from "@/components/APIKeyModal.vue";

// CSC UI things
import { defineCustomElements } from "@cscfi/csc-ui/loader";
import { vControl } from "@cscfi/csc-ui-vue";

// Project JS functions
import { i18n } from "@/common/i18n";
import {
  getUser,
  signedFetch,
  getProjects,
} from "@/common/api";

// Import SharingView and Request API
import SwiftXAccountSharing from "@/common/swift_x_account_sharing_bind";
import SwiftSharingRequest from "@/common/swift_sharing_request_bind";

// Import container ACL sync
import { syncBucketPolicies } from "@/common/share";

// Import project state
import useStore from "@/common/store";

// Import project css
import "@/assets/main.css";

// Upload and direct download notification handler
import ProgressNotification from "@/components/ProgressNotification.vue";

//Custom footer element
import CFooter from "@/components/CFooter.vue";

import { getDB, checkIDB } from "@/common/idb";
import { updateProjectSharingSyncTime } from "@/common/idbFunctions";

// Import global functions
import { initS3 } from "@/common/s3init";

checkIDB().then(result => {
  if (!result) {
    window.location.pathname = "/";
  }
});

window.onerror = function (error) {
  console.error("Global error", error);
};
window.addEventListener("unhandledrejection", function (event) {
  console.error("unhandledrejection", event);
  event.preventDefault();
  event.stopPropagation();
});
window.addEventListener("rejectionhandled", function (event) {
  console.log("rejectionhandled", event);
  event.preventDefault();
  event.stopPropagation();
});

// Configure csc-ui
defineCustomElements();

const pinia = createPinia();
const app = createApp({
  components: {
    CFooter,
    BrowserMainNavbar,
    BrowserSecondaryNavbar,
    ConfirmRouteModal,
    CreateBucketModal,
    UploadModal,
    ProgressNotification,
    EditTagsModal,
    ShareModal,
    CopyBucketModal,
    DeleteModal,
    APIKeyModal,
  },
  data: function () {
    return {
      files: [],
    };
  },
  computed: {
    projects() {
      return this.$store.projects;
    },
    multipleProjects() {
      return this.$store.multipleProjects;
    },
    langs() {
      return this.$store.langs;
    },
    active() {
      return this.$store.active;
    },
    user() {
      return this.$store.uname;
    },
    isUploading() {
      return this.$store.isUploading;
    },
    displayUploadNotification() {
      return this.$store.uploadNotification.visible;
    },
    displayDownloadNotification() {
      return this.$store.downloadNotification.visible;
    },
    openConfirmRouteModal: {
      get() {
        return this.$store.openConfirmRouteModal;
      },
      set(newState) {
        this.$store.toggleConfirmRouteModal(newState);
      },
    },
    openCreateBucketModal: {
      get() {
        return this.$store.openCreateBucketModal;
      },
      set(newState) {
        this.$store.toggleCreateBucketModal(newState);
      },
    },
    openUploadModal: {
      get() {
        return this.$store.openUploadModal;
      },
      set(newState) {
        this.$store.toggleUploadModal(newState);
      },
    },
    openEditTagsModal: {
      get() {
        return this.$store.openEditTagsModal;
      },
      set(newState) {
        this.$store.toggleEditTagsModal(newState);
      },
    },
    openCopyBucketModal: {
      get() {
        return this.$store.openCopyBucketModal;
      },
      set(newState) {
        this.$store.toggleCopyBucketModal(newState);
      },
    },
    openDeleteModal: {
      get() {
        return this.$store.openDeleteModal;
      },
      set(newState) {
        this.$store.toggleDeleteModal(newState);
      },
    },
    openShareModal: {
      get() {
        return this.$store.openShareModal;
      },
      set(newState) {
        this.$store.toggleShareModal(newState);
      },
    },
    openAPIKeyModal: {
      get() {
        return this.$store.openAPIKeyModal;
      },
      set(newState) {
        this.$store.toggleAPIKeyModal(newState);
      },
    },
    s3download() {
      return this.$store.s3download;
    },
    s3upload() {
      return this.$store.s3upload;
    },
  },
  watch: {
    openCreateBucketModal: function () {
      if (this.openCreateBucketModal) {
        // Set the modal to scroll to top whenever it's opened
        const el = document.getElementById("createBucket-modal-content");
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
  async created() {
    document.title = this.$t("message.program_name");

    let initialize = async () => {
      let active;
      let user = await getUser();
      let projects = await getProjects();
      this.$store.setUname(user);
      this.$store.setProjects(projects);

      // Sync projects instead of bulkPut to preserve last share sync data
      const existingProjectIDs = await getDB().projects
        .toCollection()
        .primaryKeys();

      const toPut = projects.filter(proj => !existingProjectIDs.includes(proj.id));
      const toDelete = existingProjectIDs.filter(id => !projects.some(proj => proj.id === id));

      if (toPut.length) {
        await getDB().projects.bulkPut(toPut);
      }

      if (toDelete.length) {
        await getDB().projects.bulkDelete(toDelete);
        await getDB().containers
          .where("projectID")
          .anyOf(toDelete)
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
      this.$store.setActive(active);

      if (document.location.pathname == "/browse") {
        this.$router.replace({
          name: "AllBuckets",
          params: {
            project: active.id,
            user: user,
          },
        });
      }
      let discovery = await fetch("/discover");
      discovery = await discovery.json();
      if (discovery.sharing_endpoint) {
        this.$store.setSharingClient(
          new SwiftXAccountSharing(
            discovery.sharing_endpoint,
            document.location.origin,
          ),
        );

        // Cache id information
        await this.$store.sharingClient.projectCacheIDs(
          this.$store.active.id,
          this.$store.active.name,
        );
      }
      if (discovery.request_endpoint) {
        this.$store.setRequestClient(
          new SwiftSharingRequest(
            discovery.request_endpoint,
            document.location.origin,
          ),
        );
      }
      if (discovery.upload_endpoint) {
        this.$store.setUploadEndpoint(discovery.upload_endpoint);

        let key = await signedFetch(
          "GET",
          discovery.upload_endpoint,
          `/cryptic/${this.active.name}/keys`,
        );
        key = await key.text();
        key = `-----BEGIN CRYPT4GH PUBLIC KEY-----\n${key}\n-----END CRYPT4GH PUBLIC KEY-----\n`;
        this.$store.appendPubKey(key);
      }
      await initS3(this.active.id, this.active.name, this.$store, this.$t);
    };

    await initialize();
    console.log("Initialized successfully.");

    await this.syncSharingIfStale();
  },
  methods: {
    /**
     * Run project share sync and update last_share_sync time in IDB after a delay
     * if project data in IDB shows that it hasn't been done in the past hour
     */
    syncSharingIfStale: async function () {
      const staleAfterMs = 60 * 60 * 1000; // 1 hour
      const delayMs = 10000;

      const project = await getDB().projects.get(this.active.id);
      const needsSync = !project.last_share_sync ||
        Date.now() - project.last_share_sync.getTime() > staleAfterMs;
      if (needsSync) {
        setTimeout(async () => {
          const synced = await syncBucketPolicies(project.id);
          if (synced) {
            await updateProjectSharingSyncTime(project.id);
            this.$store.setSharingUpdated(true);
          }
        }, delayMs);
      }
    },
    cancelUpload: function(bucket) {
      this.s3upload.cancelUpload(bucket);
    },
    cancelDownload: function() {
      this.s3download.cancelDownload();
    },
  },
  ...BrowserPage,
});

app.use(i18n);
app.use(router);
app.use(pinia);
app.directive("control", vControl);

// Pinia is geared toward multiple stores: ease migration and enforce single global store like Vuex
app.config.globalProperties.$store = useStore();

app.config.errorHandler = function (err, vm, info) {
  console.error("Vue error: ", err, vm, info);
};
app.config.warnHandler = function (msg, vm, info) {
  console.warn("Vue warning: ", msg, vm, info);
};

router.afterEach((to) => {
  if (!to.name) {
    window.location.pathname = "/notfound";
  }
});
router.isReady().then(() => app.mount("#app"));
