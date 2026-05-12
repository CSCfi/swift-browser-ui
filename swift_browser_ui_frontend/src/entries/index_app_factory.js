import { createApp } from "vue";

import { i18n } from "@/common/i18n";

import { checkIDB } from "@/common/idb";

import { defineCustomElements } from "@cscfi/csc-ui/loader";
import { vControl } from "@cscfi/csc-ui-vue";

import CFooter from "@/components/CFooter.vue";
import MainToolbar from "@/components/MainToolbar.vue";

import "@/assets/main.css";

defineCustomElements();

export function newApp(name, data, Component) {
  return createApp({
    name: name,
    components: {
      CFooter,
      MainToolbar,
    },
    data: data,
    created() {
      document.title = this.$t("message.program_name");
    },
    mounted: function() {
      // Login card content doesn't fill the card due to an invisible svg
      const targetNode = document.querySelector("form");
      if (!targetNode) return;
      const observer = new MutationObserver(() => {
        // Remove the svg once it appears in DOM
        const svg = targetNode.querySelector("c-login-card > article > svg");
        if (svg) {
          svg.remove();
          observer.disconnect();
        }
      });
      observer.observe(targetNode, { childList: true, subtree: true });

      checkIDB().then(result => this.idb = result);
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
    .directive("control", vControl);
}
