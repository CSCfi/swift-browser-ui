<template>
  <footer :aria-label="$t('label.footer')">
    <div class="navbar-menu is-active">
      <div class="navbar-start">
        <div class="col-3">
          <div class="row navbar-item ">
            <span class="largetext">
              {{ $t("message.footerMenu.title") }}
            </span>
          </div>
          <div class="row navbar-item smalltext">
            <a
              class="linktext"
              target="_blank"
              :href="$t('message.footerMenu.serviceProviderLink')"
              :alt="$t('message.footerMenu.serviceProvider')"
            >
              {{ $t("message.footerMenu.serviceProvider") }}
            </a>
          </div>
          <div
            v-if="dev"
            class="row navbar-item smalltext"
          >
            <a
              class="linktext"
              target="_blank"
              :href="gitLink"
            >
              {{ gitVersion }}
            </a>
          </div>
        </div>
      </div>

      <div
        id="rightmenu"
        class="navbar-end"
      >
        <div class="navbar-item smalltext">
          <a
            class="linktext"
            target="_blank"
            :href="$t('message.footerMenu.menuItemLink1')"
            :alt="$t('message.footerMenu.menuItem1')"
          >
            {{ $t("message.footerMenu.menuItem1") }}
          </a>
        </div>
        <div class="navbar-item smalltext">
          <a
            class="linktext"
            target="_blank"
            :href="$t('message.footerMenu.menuItemLink2')"
            :alt="$t('message.footerMenu.menuItem2')"
          >
            {{ $t("message.footerMenu.menuItem2") }}
          </a>
        </div>
      </div>
    </div>
  </footer>
</template>

<script>
import { DEV } from "@/common/conv";

export default {
  name:"CFooter",
  data: function() {
    return {
      dev: DEV,
      gitVersion: import.meta.env.VITE_GIT_VERSION || "Version not set",
      gitLink: import.meta.env.VITE_GIT_LINK || "#",
    };
  },
};
</script>

<style lang="scss" scoped>

footer{
  padding: 40px 60px;
}

footer, footer > * div {
  background-color: $csc-lightest-grey !important;
}

.navbar-menu{
  width: 100%;
  height: 100%;
  box-shadow: none;
  padding: 0;
}

#leftmenu{
  padding-left: 10px;
}

.largetext{
  font-style: normal;
  font-weight: 600;
  font-size: 16px;
  line-height: 19px;
  color: $csc-grey;
}

.smalltext{
  font-style: normal;
  font-weight: 400;
  font-size: 14px;
  line-height: 18px;
  color: $csc-grey;
}

.linktext {
  color: $csc-grey;
  font-weight: 400;
}

a:hover {
  background-color: #CCF4F0;
  text-decoration: underline;
}

</style>
