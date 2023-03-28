import { createApp } from "vue";

import { i18n } from "@/common/i18n";

import { applyPolyfills, defineCustomElements } from "csc-ui/dist/loader";
import { vControl } from "@/common/csc-ui-vue-directive";

import CFooter from "@/components/CFooter.vue";
import LanguageSelector from "@/components/CLanguageSelector.vue";

applyPolyfills().then(() => {
  defineCustomElements();
});

export function newApp(name, data, Component) {
  return createApp({
    name: name,
    components: {
      CFooter,
      LanguageSelector,
    },
    data: data,
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
    ...Component,
  })
    .use(i18n)
    .directive("csc-control", vControl);
}
