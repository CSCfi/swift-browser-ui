import Vue from "vue";
import App from "@/pages/SelectPage.vue";

import getLangCookie from "@/common/conv";
import translations from "@/common/lang";

import { getProjects } from "@/common/api";

// Import project css
import "@/css/prod.scss";

import VueI18n from "vue-i18n";

Vue.use(VueI18n);


const i18n = new VueI18n({
  locale: getLangCookie(),
  messages: translations,
});

new Vue ({
  i18n,
  data: {
    formname: "Token id:",
    loginformname: "Openstack account:",
    idb: true,
    projects: [],
    langs: [{name: "In English", value: "en"}, {name: "Suomeksi", value: "fi"}],
  },
  created() {
    document.title = this.$t("message.program_name");
    this.updateProjects();
  },
  methods: {
    "updateProjects": function () {
      getProjects().then(ret => this.projects = ret);
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
