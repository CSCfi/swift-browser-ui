<template>
  <c-menu
    :items.prop="menuItems"
    data-testid="support-menu"
  >
    <i
      class="mdi mdi-help-circle-outline pr-3 menu-icon"
    />
    <span class="menu-active">{{ $t("message.support") }}</span>
  </c-menu>
</template>

<script>
import { mdiOpenInNew } from "@mdi/js"; 
export default {
  name: "BrowserSupportMenu",
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
          label: this.$t("message.supportMenu.manual"),
          href: "https://docs.csc.fi/data/sensitive-data/",
        },
        {
          label: this.$t("message.supportMenu.billing"),
          href: "https://research.csc.fi/pricing#buc",
        },
        {
          label: this.$t("message.supportMenu.sharing"), 
          href: "",
        },
        {
          label: this.$t("message.supportMenu.about"), 
          href: "https://research.csc.fi/sensitive-data",
        }];
      // Menu item can be hidden if it's optional rule doesn't apply
      for (let item of rawMenuItems.filter(
        menuItem => menuItem.rule === undefined || menuItem.rule)
      ) {
        this.menuItems.push({
          name: item.label,
          action: () => {
            window.open(item.href, "_blank");
          },
          icon: mdiOpenInNew,
          disabled: item.href === "",
        });
      }
    },
  },
};
</script> 