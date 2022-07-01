<template>
  <c-menu
    :items.prop="menuItems"
    data-testid="user-menu"
  >
    <i
      class="mdi mdi-account pr-3 menu-icon"
    />
    <span class="menu-active">{{ uname }}</span>
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

      const rawMenuItems = [
        {
          label: this.$t("message.dashboard.dashboard"),
          route: { name: "DashboardView" },
        },
        {
          label: this.$t("message.dashboard.browser"),
          route: { name: "AllFolders" },
        },
        {
          label: this.$t("message.share.shared"), 
          route: { name: "SharingTo" },
          rule: this.$store.state.client,
        },
        {
          label: this.$t("message.logOut"), 
          route: "/login/kill",
        }];


      // Menu item can be hidden if it's optional rule doesn't apply
      for (let item of rawMenuItems.filter(
        menuItem => menuItem.rule === undefined || menuItem.rule)
      ) {
        this.menuItems.push({
          name: item.label,
          action: () => {
            // String typed routes navigate out from app and therefore
            // need to be handled with native browser properties.
            // Navigating to active route is not allowed.
            const activeRoute = this.$route;

            if (typeof item.route === "string") {
              window.location.href = item.route;
            } else if (item.route.name !== activeRoute.name) {
              this.$router.push({...item.route, params: {        
                user: this.uname, 
                project: this.active.id}});
            }
          },
        });
      }
    },
  },
};
</script>