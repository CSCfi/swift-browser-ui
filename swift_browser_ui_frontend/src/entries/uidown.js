import Vue from "vue";
import App from "@/pages/IndexPage.vue";
import VueI18n from "vue-i18n";

import getLangCookie from "@/common/conv";
import translations from "@/common/lang";

import cModel from "@/common/csc-ui.js";

import { applyPolyfills, defineCustomElements } from "csc-ui/dist/loader";
import { vControlV2 } from "csc-ui-vue-directive";

import CFooter from "@/components/CFooter.vue";
import LanguageSelector from "@/components/CLanguageSelector.vue";

// Import project css
import "@/css/prod.scss";

Vue.config.productiontip = true;

Vue.config.ignoredElements = [/c-\w*/];

applyPolyfills().then(() => {
  defineCustomElements();
});

Vue.use(VueI18n);
Vue.directive("control", vControlV2);
Vue.directive("csc-model", cModel);

const i18n = new VueI18n({
  locale: getLangCookie(),
  messages: translations,
});

new Vue({
  name: "ServiceUnavailable",
  i18n,
  components: {
    CFooter,
    LanguageSelector,
  },
  data: {
    notindex: true,
    badrequest: false,
    unauth: false,
    forbid: false,
    notfound: false,
    uidown: true,
    langs: [{ph: "In English", value: "en"}, {ph: "Suomeksi", value: "fi"}],
    idb: true,
  },
  created() {
    document.title = this.$t("message.program_name");
  },
  methods: {
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
