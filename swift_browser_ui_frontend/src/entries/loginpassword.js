import { createApp } from "vue";
import LoginPassword from "@/pages/LoginPassword.vue";
import LanguageSelector from "@/components/CLanguageSelector.vue";

import bannerUrl from "@/assets/banner_login.png";

import { i18n } from "@/common/i18n";

import CFooter from "@/components/CFooter.vue";

import { applyPolyfills, defineCustomElements } from "csc-ui/dist/loader";
import { vControl } from "@/common/csc-ui-vue-directive";


// Import project css
import "@/css/prod.scss";

applyPolyfills().then(() => {
  defineCustomElements();
});

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
app.directive("csc-control", vControl);

app.mount("#app");
