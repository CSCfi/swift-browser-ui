import { newApp } from "@/entries/index_app_factory";
import IndexPage from "@/pages/IndexPage.vue";

const app = newApp(
  "ForbiddenPage",
  () => {
    return {
      notindex: true,
      badrequest: false,
      unauth: false,
      forbid: true,
      notfound: false,
      uidown: false,
      langs: [{ph: "In English", value: "en"}, {ph: "Suomeksi", value: "fi"}],
      idb: true,
    };
  },
  IndexPage,
);

app.mount("#app");
