import { newApp } from "@/entries/index_app_factory";
import IndexOIDCPage from "@/pages/IndexOIDCPage.vue";
import bannerUrl from "@/assets/banner_login.png";

const app = newApp(
  "IndexOIDCPage",
  () => {
    return {
      loading: false,
      idb: true,
      bannerUrl,
    };
  },
  IndexOIDCPage,
);

app.mount("#app");
