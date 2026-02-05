import { newApp } from "@/entries/index_app_factory";
import IndexPage from "@/pages/IndexPage.vue";
import bannerUrl from "@/assets/banner_login.png";
import { mdiLogin, mdiOpenInNew } from "@mdi/js";

const app = newApp(
  "IndexPage",
  () => {
    return {
      notindex: false,
      badrequest: false,
      uidown: false,
      unauth: false,
      forbid: false,
      notfound: false,
      langs: [{ph: "In English", value: "en"}, {ph: "Suomeksi", value: "fi"}],
      idb: true,
      bannerUrl,
      mdiLogin,
      mdiOpenInNew,
    };
  },
  IndexPage,
);

app.mount("#app");
