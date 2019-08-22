// Project main imports
import Vue from "vue";
import App from "./Browser.vue";
import Buefy from "buefy";
import router from "./router";
import VueI18n from "vue-i18n";

// Project Vue components
import BrowserNavbar from "@/components/BrowserNavbar.vue";
import BreadcrumbListElement from "@/components/Breadcrumb.vue";

// Project JS functions
import getLangCookie from "@/conv";
import translations from "@/lang";

// Import project state
import store from "@/store";

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
  },
  ...App,
}).$mount("#app");
