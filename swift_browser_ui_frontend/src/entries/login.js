import Vue from "vue";
import App from "@/pages/Login.vue";

// Import project css
import "@/css/prod.scss";

new Vue ({
  data: {
    formname: "Token id:",
  },
  created() {
    document.title = this.$t("message.program_name");
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
