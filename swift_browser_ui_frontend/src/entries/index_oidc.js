

import Vue from "vue";
import App from "@/pages/IndexOIDCPage.vue";

import getLangCookie from "@/common/conv";
import translations from "@/common/lang";
import checkIDB from "@/common/idb_support";
import cModel from "@/common/csc-ui.js";

import { applyPolyfills, defineCustomElements } from "csc-ui/dist/loader";
import VueI18n from "vue-i18n";

// Import project css
import "@/css/prod.scss";


Vue.config.ignoredElements = [/c-\w*/];

applyPolyfills().then(() => {
  defineCustomElements();
});

Vue.use(VueI18n);


const i18n = new VueI18n({
  locale: getLangCookie(),
  messages: translations,
});

new Vue ({
  i18n,
  data: {
    loading: false,
    idb: true,
  },
  created() {
    document.title = this.$t("message.program_name");
  },
  mounted: function() {
    checkIDB().then(result => this.idb = result);
  },
  methods: {
    loginButtonClick: function() {
      this.loading = true;
      window.location.pathname = this.$t("message.indexOIDC.href");
    },
    setCookieLang: function() {
      const expiryDate = new Date();
      expiryDate.setMonth(expiryDate.getMonth() + 1);
      document.cookie = "OBJ_UI_LANG=" +
                        i18n.locale +
                        "; path=/; expires="
                        + expiryDate.toUTCString();
    },
  },
  ...App,
}).$mount("#app");


Vue.directive("csc-model", cModel);
