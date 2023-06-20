import { createApp } from "vue";
import IndexOIDCPage from "@/pages/IndexOIDCPage.vue";

import { i18n } from "@/common/i18n";

import checkIDB from "@/common/idb_support";

import { applyPolyfills, defineCustomElements } from "csc-ui/dist/loader";
import { vControl } from "@/common/csc-ui-vue-directive";

import CFooter from "@/components/CFooter.vue";
import LanguageSelector from "@/components/CLanguageSelector.vue";

import bannerUrl from "@/assets/banner_login.png";

// Import project css
import "@/css/prod.scss";


applyPolyfills().then(() => {
  defineCustomElements();
});

const app = createApp({
  components: {
    CFooter,
    LanguageSelector,
  },
  data: function() {
    return {
      loading: false,
      idb: true,
      bannerUrl,
    };
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
  ...IndexOIDCPage,
});

app.use(i18n);
app.directive("csc-control", vControl);
app.config.compilerOptions.isCustomElement = (tag) => tag.startsWith("c-");

app.mount("#app");
