import { newApp } from "@/entries/index_app_factory";
import IndexPage from "@/pages/IndexPage.vue";

import "@/css/prod.scss";

const app = newApp(
  "ServiceUnavailable",
  () => {
    return {
      notindex: true,
      badrequest: false,
      unauth: false,
      forbid: false,
      notfound: false,
      uidown: true,
      langs: [{ph: "In English", value: "en"}, {ph: "Suomeksi", value: "fi"}],
      idb: true,
    };
  },
  IndexPage,
);

app.mount("#app");
