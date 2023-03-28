import { createApp } from "vue";
import SelectPage from "@/pages/SelectPage.vue";

import { applyPolyfills, defineCustomElements } from "csc-ui/dist/loader";
import { vControl } from "@/common/csc-ui-vue-directive";

import { i18n } from "@/common/i18n";

import { getProjects } from "@/common/api";

// Import project css
import "@/css/prod.scss";

applyPolyfills().then(() => {
  defineCustomElements();
});

const app = createApp({
  data: function() {
    return {
      formname: "Token id:",
      loginformname: "Openstack account:",
      idb: true,
      projects: [],
      langs: [
        {name: "In English", value: "en"},
        {name: "Suomeksi", value: "fi"},
      ],
    };
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
  ...SelectPage,
});

app.use(i18n);
app.directive("csc-control", vControl);

app.mount("#app");
