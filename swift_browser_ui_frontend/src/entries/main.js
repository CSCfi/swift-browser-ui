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
  },
  beforeMount() {
    getUser().then(( value ) => {
      this.$store.commit("setUname", value);
    });
    getProjects().then((value) => {
      this.$store.commit("setProjects", value);
      if (document.location.pathname == "/browse") {
        getActiveProject().then((value) => {
          this.$store.commit("setActive", value);
          this.$router.push(
            "/browse/" +
            this.$store.state.uname +
            "/" +
            this.$store.state.active["name"]
          );
        });
      }
      if (this.$store.state.active["name"] != this.$route.params.project) {
        getActiveProject().then((value) => {
          this.$store.commit("setActive", value);
          if (value["name"] != this.$route.params.project) {
            this.changeProject(this.$route.params.project);
          }
        });
      }
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
    getRouteAsList: function () {
      // Create a list representation of the current application route
      // to help in the initialization of the breadcrumb component
      let retl = [];
      if (this.$route.params.user != undefined) {
        retl.push({
          alias: this.$route.params.user,
          address: ("/browse/" + this.$route.params.user),
        });
      }
      if (this.$route.params.project != undefined) {
        retl.push({
          alias: this.$route.params.project,
          address: (
            "/browse/" + this.$route.params.user +
            "/" + this.$route.params.project
          ),
        });
      }
      if (this.$route.params.container != undefined) {
        retl.push({
          alias: this.$route.params.container,
          address: (
            "/browse/" + this.$route.params.user +
            "/" + this.$route.params.project +
            "/" + this.$route.params.container
          ),
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
