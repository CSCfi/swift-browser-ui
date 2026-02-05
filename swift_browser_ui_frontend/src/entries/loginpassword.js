import { createApp } from "vue";
import { mdiLogin } from "@mdi/js";
import LoginPassword from "@/pages/LoginPassword.vue";
import LanguageSelector from "@/components/CLanguageSelector.vue";

import bannerUrl from "@/assets/banner_login.png";

import { i18n } from "@/common/i18n";

import CFooter from "@/components/CFooter.vue";

import { defineCustomElements } from "@cscfi/csc-ui/loader";
import { vControl } from "@cscfi/csc-ui-vue";


// Import project css
import "@/assets/main.css";

defineCustomElements();


const app = createApp({
  name: "LoginPassword",
  components: {
    CFooter,
    LanguageSelector,
  },
  data: function() {
    return {
      langs: [{ph: "In English", value: "en"}, {ph: "Suomeksi", value: "fi"}],
      idb: true,
      bannerUrl,
      mdiLogin,
    };
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
  ...LoginPassword,
});

app.use(i18n);
app.directive("control", vControl);

app.mount("#app");
