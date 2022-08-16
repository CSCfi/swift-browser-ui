<template>
  <div id="mainContainer">
    <div id="subContainer">
      <BrowserMainNavbar :langs="langs" />
      <BrowserSecondaryNavbar
        :multiple-projects="multipleProjects"
        :projects="projects"
      />
      <ProgressBar v-if="isUploading || isChunking" />
      <b-breadcrumb style="margin-left: 5%; margin-top: 1%; font-size: 1rem">
        <b-breadcrumb-item
          v-for="item in getRouteAsList()"
          :key="item.alias"
          :to="item.address"
          tag="router-link"
          data-testid="breadcrumb-item"
        >
          {{ item.alias | truncate(100) }}
        </b-breadcrumb-item>
      </b-breadcrumb>
      <router-view class="content-wrapper" />
      <b-loading
        :is-full-page="isFullPage"
        :active.sync="isLoading"
        :can-cancel="false"
      />
      <footer id="footer" class="footer">
        <div class="content has-text-centered">
          <p>
            <span class="has-text-weight-bold">
              {{ $t("message.program_name") }}
            </span>
            {{ $t("message.devel") }}
            <a href="https://csc.fi" :alt="$t('message.cscOrg')">{{
              $t("message.cscOrg")
            }}</a>
          </p>
        </div>
      </footer>
    </div>
  </div>
</template>

<script>
import { truncate } from "@/common/conv";

export default {
  name: "BrowserPage",
  filters: {
    truncate,
  },
};
</script>

<style lang="scss">
@import "@/css/prod.scss";

$footer-height: 10rem;

html, body {
  height: 100%;
}

#mainContainer {
  min-height: 100vh;
  position: relative;
}

#subContainer {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.content-wrapper {
  margin: 0;
  padding: 0;
  padding-bottom: calc(#{$footer-height} + 3rem);
  display: flex;
  flex-direction: column;
}

.contents {
  flex: 1 0 auto;
}

.navbar .container .navbar-brand .navbar-item img {
  max-height: 2.5rem;
}

.menu-active {
  font-weight: 600 !important;
  font-size: 14px;
}

.menu-icon {
  font-size: 1.5rem;
}

.menu-active,
.menu-icon {
  color: $csc-primary;
}

.menu-icon {
  font-size: 1.5rem;
}

.menu-active, .menu-icon {
  color: $csc-primary;
}

.hero-body #login-center{
    padding: 30px 20px 20px 20px;
}

.hero-body .footer {
  margin: 15px 0;
  padding: 0;
}

.searchBox {
  max-width: 30%;
  width: auto;
  margin-right: auto;
  margin-left: auto;
}

.uploadGroup {
  margin-left: auto;
}

.dashboard {
  margin-left: 5%;
  margin-right: 5%;
}

.footer {
  flex-shrink: 0;
  position: absolute;
  height: $footer-height;
  width: 100%;
  bottom: 0;
}

#footer {
  margin-top: 15px;
}
</style>
