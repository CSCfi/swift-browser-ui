// Project main imports
import Vue from "vue";
import App from "@/pages/BrowserPage.vue";
import Buefy from "buefy";
import router from "@/common/router";
import VueI18n from "vue-i18n";

// Project Vue components
import BrowserNavbar from "@/components/BrowserNavbar.vue";

// Project JS functions
import getLangCookie from "@/common/conv";
import translations from "@/common/lang";
import { getUser } from "@/common/api";
import { getProjects } from "@/common/api";
import getActiveProject from "@/common/api";
import { changeProjectApi } from "@/common/api";

// Import SharingView and Request API
import SwiftXAccountSharing from "@/common/swift_x_account_sharing_bind";
import SwiftSharingRequest from "@/common/swift_sharing_request_bind";

// Import container ACL sync
import { syncContainerACLs } from "@/common/conv";

// Import project state
import store from "@/common/store";

// Import project css
import "@/css/prod.scss";

// Import resumable
import Resumable from "resumablejs";

// Upload progress button
import ProgressBar from "@/components/UploadProgressBar";

// Import delay
import delay from "lodash/delay";

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
    isChunking () {
      return this.$store.state.isChunking;
    },
    isUploading () {
      return this.$store.state.isUploading;
    },
    resumableClient () {
      return this.$store.state.resumableClient;
    },
    altContainer () {
      return this.$store.state.altContainer;
    },
  },
  created() {
    document.title = this.$t("message.program_name");
    this.createUploadInstance();
    getUser().then(( value ) => {
      this.$store.commit("setUname", value);
    });
    getProjects().then((value) => {
      this.$store.commit("setProjects", value);
      
      getActiveProject().then((value) => {
        this.$store.commit("setActive", value);
        if (this.$route.params.user != undefined) {
          if (
            value.name != this.$route.params.project &&
            this.$route.params.project != undefined
          ) {
            this.changeProject(this.$route.params.project);
          }
        }
        if (document.location.pathname == "/browse") {
          this.$router.push(
            "/browse/".concat(
              this.$store.state.uname,
              "/",
              value.name,
            ),
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
              document.location.origin,
            ),
          );
        }
        if (ret.request_endpoint) {
          this.$store.commit(
            "setRequestClient",
            new SwiftSharingRequest(
              ret.request_endpoint,
              document.location.origin,
            ),
          );
        }
      });
    delay(
      this.containerSyncWrapper,
      5000,
    );
  },
  methods: {
    containerSyncWrapper: function () {
      syncContainerACLs(
        this.$store.state.client,
        this.$store.state.active.id,
      );
    },
    // Following are the methods used for resumablejs, as the methods
    // need to have access to the vue instance.
    addFileToast: function () {
      this.$buefy.toast.open({
        message: "File / files scheduled for upload.",
        type: "is-success",
      });
      if(!this.isUploading) {
        this.resumableClient.upload();
      }
    },
    fileSuccessToast: function (file) {
      this.$buefy.toast.open({
        message: this.$t("message.upfinish").concat(file.fileName),
        type: "is-success",
      });
      if (this.$route.params.container != undefined) {
        this.$store.commit({
          type: "updateObjects",
          route: this.$route,
        });
      }
    },
    fileFailureToast: function (file) {
      this.$buefy.toast.open({
        message: this.$t("message.upfail").concat(file.fileName),
        type: "is-danger",
      });
    },
    getUploadUrl: function (params) {
      let retUrl = new URL(
        "/upload/".concat(
          this.$route.params.owner ? this.$route.params.owner : this.active.id,
          "/",
          this.altContainer,
        ),
        document.location.origin,
      );
      for (const param of params) {
        let newParam = param.split("=");
        // check if we should move the file under a pseudofolder
        // using the current prefix defined in route for the url
        if (
          newParam[0].match("resumableRelativePath")
          && this.$route.query.prefix != undefined
        ) {
          retUrl.searchParams.append(
            newParam[0],
            this.$route.query.prefix + newParam[1],
          );
        } else {
          retUrl.searchParams.append(newParam[0], newParam[1]);
        }
      }
      return retUrl.toString();
    },
    startUpload: function () {
      let altContainer = "upload-".concat(Date.now().toString());
      if (this.$route.params.container) {
        altContainer = this.$route.params.container;
      }
      this.$store.commit("setAltContainer", altContainer);
      this.$store.commit("setUploading");
      window.onbeforeunload = function () {return "";};
    },
    endUpload: function () {
      this.$store.commit("eraseAltContainer");
      this.$store.commit("stopUploading");
      this.$store.dispatch("updateContainers");
      window.onbeforeunload = undefined;
    },
    startChunking: function () {
      this.$store.commit("setChunking");
    },
    stopChunking: function () {
      this.$store.commit("stopChunking");
    },
    onComplete: function () {
      this.endUpload();
      this.stopChunking();
      this.$store.commit("eraseProgress");
    },
    onCancel: function () {
      this.onComplete();
    },
    updateProgress () {
      this.$store.commit(
        "updateProgress",
        this.resumableClient.progress(),
      );
    },
    createUploadInstance: function () {
      let res = new Resumable({
        target: this.getUploadUrl,
        testTarget: this.getUploadUrl,
        chunkSize: 5242880,
        forceChunkSize: true,
        simultaneousUploads: 1,
      });

      if (!res.support) {
        this.$buefy.toast.open({
          message: this.$("message.upnotsupported"),
          type: "is-danger",
        });
        return;
      }

      // Set handlers
      res.on("uploadStart", this.startUpload);
      res.on("complete", this.onComplete);
      res.on("cancel", this.onCancel);
      res.on("filesAdded", this.addFileToast);
      res.on("fileSuccess", this.fileSuccessToast);
      res.on("fileError", this.fileFailureToast);
      res.on("chunkingStart", this.startChunking);
      res.on("chunkingComplete", this.stopChunking);
      res.on("progress", this.updateProgress);

      this.$store.commit("setResumable", res);
    },
    getRouteAsList: function () {
      // Create a list representation of the current application route
      // to be used in the initialization of the breadcrumb component
      let retl = [];
      
      retl.push({
        alias: this.$store.state.uname,
        address: {name: "DashboardView"},
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
            address: {name: "ContainersView"},
          });
        }
      }

      if (this.$route.params.container != undefined) {
        retl.push({
          alias: this.$route.params.container,
          address: {name: "ObjectsView"},
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
              this.$store.state.active["name"],
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
