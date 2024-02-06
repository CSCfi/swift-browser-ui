import { newApp } from "@/entries/index_app_factory";
import IndexPage from "@/pages/IndexPage.vue";

const app = newApp(
  "NotfoundPage",
  () => {
    return {
      notindex: true,
      badrequest: false,
      unauth: false,
      forbid: false,
      notfound: true,
      uidown: false,
      langs: [{ph: "In English", value: "en"}, {ph: "Suomeksi", value: "fi"}],
      idb: true,
    };
  },
  IndexPage,
);

app.mount("#app");
