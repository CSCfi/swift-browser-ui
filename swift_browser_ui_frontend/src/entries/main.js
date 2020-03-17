// Project main imports
import Vue from "vue";
import App from "@/pages/Browser.vue";
import Buefy from "buefy";
import router from "@/common/router";
import VueI18n from "vue-i18n";

// Project Vue components
import BrowserNavbar from "@/components/BrowserNavbar.vue";
import BreadcrumbListElement from "@/components/Breadcrumb.vue";

// Project JS functions
import getLangCookie from "@/common/conv";
import translations from "@/common/lang";
import { getUser } from "@/common/api";
import { getProjects } from "@/common/api";
import getActiveProject from "@/common/api";
import { changeProjectApi } from "@/common/api";

// Import Sharing and Request API
import SwiftXAccountSharing from "@/common/swift_x_account_sharing_bind";
import SwiftSharingRequest from "@/common/swift_sharing_request_bind";

// Import project state
import store from "@/common/store";

// Import project css
import "buefy/dist/buefy.css";

// Import resumable
import Resumable from "resumablejs";

// Upload progress button
import ProgressBar from "@/components/UploadProgressBar";

Vue.config.productionTip = false;

Vue.use(Buefy);
Vue.use(VueI18n);

const i18n = new VueI18n({
  locale: getLangCookie(),
  messages: translations,
});

new Vue({
  i18n,
  router,
  store,
  components: {
    BrowserNavbar,
    BreadcrumbListElement,
    ProgressBar,
  },
  computed: {
    projects () {
      return this.$store.state.projects;
    },
    multipleProjects () {
      return this.$store.state.multipleProjects;
    },
    langs () {
      return this.$store.state.langs;
    },
    active () {
      return this.$store.state.active;
    },
    isFullPage () {
      return this.$store.state.isFullPage;
    },
    isLoading () {
      return this.$store.state.isLoading;
    },
    resumableClient () {
      return this.$store.state.resumableClient;
    },
  },
  beforeMount() {
    this.createUploadInsatnce();
    getUser().then(( value ) => {
      this.$store.commit("setUname", value);
    });
    getProjects().then((value) => {
      this.$store.commit("setProjects", value);

      getActiveProject().then((value) => {
        this.$store.commit("setActive", value);
        if (
          value.name != this.$route.params.project &&
          this.$route.params.project != undefined
        ) {
          this.changeProject(this.$route.params.project);
        }
        if (document.location.pathname == "/browse") {
          this.$router.push(
            "/browse/".concat(
              this.$store.state.uname,
              "/",
              value.name
            )
          );
        }
      });
    });
    fetch("/discover")
      .then((resp) => {
        return resp.json();
      }).then((ret) => {
        if (ret.sharing_endpoint) {
          this.$store.commit(
            "setSharingClient",
            new SwiftXAccountSharing(
              ret.sharing_endpoint,
              document.location.origin
            )
          );
        }
        if (ret.request_endpoint) {
          this.$store.commit(
            "setRequestClient",
            new SwiftSharingRequest(
              ret.request_endpoint,
              document.location.origin
            )
          );
        }
      });
  },
  methods: {
    // Following are the methods used for resumablejs, as the methods
    // need to have access to the vue instance.
    addFileToast: function () {
      this.$buefy.toast.open({
        message: "File / files scheduled for upload.",
        type: "is-success",
      });
    },
    fileSuccessToast: function (file) {
      this.$buefy.toast.open({
        message: "Finished uploading ".concat(file.fileName),
        type: "is-success",  
      });
    },
    fileFailureToast: function (file) {
      this.$buefy.toast.open({
        message: "Upload for file ".concat(file.fileName, " failed"),
        type: "is-danger",
      });
    },
    getUploadUrl: function () {
      let alt_container = "uplaod-".concat(Date.now().toString());
      return "/upload/".concat(
        this.$route.params.owner ? this.$route.params.owner : this.active.id,
        "/",
        this.$route.params.container ? this.$route.params.container
          : alt_container
      );
    },
    startUpload: function () {
      this.$store.state.commit("setUploading");
    },
    endUpload: function () {
      this.$store.state.commit("stopUploading");
    },
    startChunking: function () {
      this.$store.state.commit("setChunking");
    },
    stopChunking: function () {
      this.$store.state.commit("stopChunking");
    },
    onComplete: function () {
      this.endUpload();
      this.stopChunking();
      this.$store.state.commit("eraseProgress");
    },
    onCancel: function () {
      this.onComplete();
    },
    updateProgress () {
      this.$store.state.commit(
        "updateProgress",
        this.resumableClient.progress()
      );
    },
    createUploadInsatnce: function () {
      let res = new Resumable({
        target: this.get_upload_url,
        chunkSize: 268435456,
        forceChunkSize: true,
        simultaneousUploads: 1,
      });

      if (!res.support) {
        this.$buefy.toast.open({
          message: "Uploading is not supported on your browser.",
          type: "is-danger",
        });
        return;
      }

      // Set handlers
      res.on("uploadStart", this.startUpload);
      res.on("compete", this.onComplete);
      res.on("cancel", this.onCancel);
      res.on("fileAdded", this.addFileToast);
      res.on("fileSuccess", this.fileSuccessToast);
      res.on("fileError", this.fileFailureToast);

      this.$store.commit("setResumable", res);
    },
    getRouteAsList: function () {
      // Create a list representation of the current application route
      // to be used in the initialization of the breadcrumb component
      let retl = [];
      
      retl.push({
        alias: this.$store.state.uname,
        address: {name: "Dashboard"},
      });

      if (this.$route.params.project != undefined) {
        if (this.$route.path.match("sharing") != null) {
          retl.push({
            alias: this.$t("message.sharing") + this.$store.state.active.name,
            address: {name: "SharedTo"},
          });
        }
        else {
          retl.push({
            alias: this.$t("message.containers")
                   + this.$store.state.active.name,
            address: {name: "Containers"},
          });
        }
      }

      if (this.$route.params.container != undefined) {
        retl.push({
          alias: this.$route.params.container,
          address: {name: "Objects"},
        });
      }

      return retl;
    },
    changeProject: function (newProject) {
      // Re-scope login to project given as a parameter.
      changeProjectApi(newProject).then((ret) => {
        if (ret) {
          getActiveProject().then((value) => {
            this.$store.commit("setActive", value);
            this.$store.commit("updateContainers", undefined);
            this.$store.commit("eraseObjects");
            this.$router.push(
              "/browse/" +
              this.$store.state.uname + "/" +
              this.$store.state.active["name"]
            );
            this.$router.go(0);
          });
        } else{
          this.$router.push("/browse/" + this.$store.state.uname);
        }
      });
    },
  },
  ...App,
}).$mount("#app");
