import { newApp } from "@/entries/index_app_factory";
import IndexPage from "@/pages/IndexPage.vue";

const app = newApp(
  "BadRequest",
  () => {
    return {
      notindex: true,
      badrequest: true,
      unauth: false,
      forbid: false,
      notfound: false,
      uidown: false,
      langs: [{ph: "In English", value: "en"}, {ph: "Suomeksi", value: "fi"}],
      idb: true,
    };
  },
  IndexPage,
);

app.mount("#app");
