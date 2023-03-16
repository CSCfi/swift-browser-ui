import { createApp } from "vue";
import LoginPage from "@/pages/LoginPage.vue";

import { i18n } from "@/common/i18n";

// Import project css
import "@/css/prod.scss";

const app = createApp({
  data: function() {
    return {
      formname: "Token id:",
      loginformname: "Openstack account:",
      idb: true,
    };
  },
  created() {
    document.title = i18n.$t("message.program_name");
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
  ...LoginPage,
});
  
app.mount("#app");
