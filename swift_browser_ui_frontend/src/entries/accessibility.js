import { newApp } from "@/entries/index_app_factory";
import AccessibilityPage from "@/pages/AccessibilityPage.vue";

const app = newApp(
  "AccessibilityPage",
  () => {
    return {
      user: "",
    };
  },
  AccessibilityPage,
);

app.mount("#app");
