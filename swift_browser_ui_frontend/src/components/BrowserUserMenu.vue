<template>
  <c-menu :items.prop="menuItems">
    {{ uname }}
  </c-menu>
</template>

<script>
export default {
  name: "BrowserUserMenu",
  data: function() {
    return {
      menuItems: [],
    };
  },
  computed: {
    active () {
      return this.$store.state.active;
    },
    uname () {
      return this.$store.state.uname;
    },
    locale () {
      return this.$i18n.locale;
    },
  },
  watch: {
    locale () {
      // Menu needs to be re-created & translated when locale changes
      this.setMenu();
    },
  },
  created: function () {
    this.setMenu();
  },
  methods: {
    setMenu() {
      this.menuItems = [];

      const navigationParams = {
        user: this.uname, 
        project: this.active.id,
      };

      const rawMenuItems = [
        {
          label: this.$t("message.dashboard.dashboard"),
          route: {
            name: "DashboardView", 
            params: navigationParams,
          },
        },
        {
          label: this.$t("message.dashboard.browser"),
          route: {
            name: "ContainersView",
            params: navigationParams,
          },
        },
        {
          label: this.$t("message.share.shared"), 
          route: {
            name: "SharedTo", params: navigationParams},
          rule: this.$store.state.client,
        },
        {
          label: this.$t("message.logOut"), 
          route: "/login/kill",
        }];

      for (let item of rawMenuItems) {
        this.menuItems.push({
          name: item.label,
          action: () => {
            // String typed routes navigate out from app and therefore
            // need to be handled with native browser properties
            typeof item.route === "string" ? 
              window.location.href = item.route :
              this.$router.push(item.route);
          },
        });
      }
    },
  },
};
</script>
