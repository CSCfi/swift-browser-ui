import Vue from "vue";
import App from "@/pages/Login.vue";

// Import project css
import "buefy/dist/buefy.css";

new Vue ({
  data: {
    formname: "Token id:",
  },
  methods: {
    "displayInvalid": function () {
      if (
        document.cookie.split(";")
          .filter((item) => 
            item.trim().startsWith("INVALID_TOKEN=")).length ) {
        this.formname = 
          "Token id: (Invalid characters in previous token.)";
      }
    },
  },
  ...App,
}).$mount("#app");
