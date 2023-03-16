import { newApp } from "@/entries/index_app_factory";
import IndexPage from "@/pages/IndexPage.vue";

import "@/css/prod.scss";

const app = newApp(
  "UnauthorizedPage",
  () => {
    return {
      notindex: true,
      badrequest: false,
      unauth: true,
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
