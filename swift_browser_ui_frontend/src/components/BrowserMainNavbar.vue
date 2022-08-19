<template>
  <div
    id="main-navbar"
    class="navbar"
  >
    <div class="container is-fluid">
      <div class="navbar-brand">
        <router-link
          class="navbar-item csclogo"
          :to="`/browse/${uname}/${active.id}`"
        >
          <c-csc-logo />
        </router-link>
      </div>
      <div class="navbar-menu">
        <div class="navbar-start">
          <div class="navbar-item app-name">
            <b>{{ $t("message.program_name") }}</b>
          </div>
        </div>
        <div class="navbar-end">
          <div class="navbar-item">
            <LanguageSelector />
          </div> 
          <div class="navbar-item">
            <BrowserSupportMenu />
          </div>
          <div class="navbar-item">
            <BrowserUserMenu />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import LanguageSelector from "@/components/CLanguageSelector.vue";
import BrowserSupportMenu from "@/components/BrowserSupportMenu.vue";
import BrowserUserMenu from "@/components/BrowserUserMenu.vue";

export default {
  name: "BrowserMainNavbar",
  components: {
    LanguageSelector,
    BrowserSupportMenu,
    BrowserUserMenu,
  },
  props: [
    "langs",
  ],
  computed: {
    active () {
      return this.$store.state.active;
    },
    uname () {
      return this.$store.state.uname;
    },
  },
};
</script>

<style lang="scss" scoped>
@import "@/css/prod.scss";

#main-navbar {
  box-shadow: 2px 4px 8px 0px $csc-light-grey;
  z-index: 31;
}

.app-name {
  color: $csc-grey;
  font-size: 20px;
}

</style>
