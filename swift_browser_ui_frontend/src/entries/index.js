import Vue from "vue";
import App from "@/pages/Index.vue";
import Buefy from "buefy";
import VueI18n from "vue-i18n";

import getLangCookie from "@/common/conv";
import translations from "@/common/lang";

// Import project css
import "buefy/dist/buefy.css";

Vue.config.productiontip = true;

Vue.use(Buefy);
Vue.use(VueI18n);

const i18n = new VueI18n({
  locale: getLangCookie(),
  messages: translations,
});

new Vue({
  name: "Index",
  i18n,
  data: {
    notindex: false,
    uidown: false,
    unauth: false,
    forbid: false,
    notfound: false,
    langs: [{ph: "In English", value: "en"}, {ph: "Suomeksi", value: "fi"}],
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
  ...App,
}).$mount("#app");
