import { newApp } from "@/entries/index_app_factory";
import AccessibilityPage from "@/pages/AccessibilityPage.vue";

const app = newApp(
  "AccessibilityPage",
  () => {
    return {
      notindex: true,
      badrequest: false,
      unauth: false,
      forbid: false,
      notfound: false,
      uidown: false,
      langs: [{ph: "In English", value: "en"}, {ph: "Suomeksi", value: "fi"}],
      idb: false,
    };
  },
  AccessibilityPage,
);

app.mount("#app");
