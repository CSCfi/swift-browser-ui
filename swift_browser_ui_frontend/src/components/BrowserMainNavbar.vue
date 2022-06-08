<template>
  <div
    id="main-navbar"
    class="navbar"
  >
    <div class="container is-fluid">
      <div class="navbar-brand">
        <a
          class="navbar-item csclogo"
          :href="'/browse/'.concat(uname)"
        >
          <img
            src="@/assets/logo.svg"
            :alt="$t('message.cscOrg')"
          >
        </a>
      </div>
      <div class="navbar-menu">
        <div class="navbar-start">
          <div class="navbar-item">
            <b>{{ $t("message.program_name") }}</b>
          </div>
        </div>
        <div class="navbar-end">
          <div class="navbar-item">
            <LanguageSelector />
          </div> 
          <div
            v-if="$te('message.helplink')"
            class="navbar-item"
          >
            <a
              :href="$t('message.helplink')"
              target="_blank"
            >
              <c-button
                text
                tabindex="-1"
              >
                <i
                  slot="icon"
                  class="mdi mdi-help-circle-outline menu-icon"
                />
                <span class="menu-active">{{ $t("message.support") }}</span>
              </c-button>
            </a>
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
import BrowserUserMenu from "@/components/BrowserUserMenu.vue";

export default {
  name: "BrowserMainNavbar",
  components: {
    LanguageSelector,
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
</style>
