import Vue from "vue";
import App from "@/pages/LoginPage.vue";

import getLangCookie from "@/common/conv";
import translations from "@/common/lang";

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
  },
  created() {
    document.title = this.$t("message.program_name");
  },
  methods: {
    "displayInvalid": function () {
      if (
        document.cookie.split(";")
          .filter((item) => 
            item.trim().startsWith("INVALID_TOKEN=")).length ) {
        this.formname = 
          "Token id: (Invalid characters in previous token.)";
      }
    },
  },
  ...App,
}).$mount("#app");
