<template>
  <div
    id="mainContainer"
    @dragenter="itemdrop = true"
    @dragover="itemdrop = true"
    @dragleave="itemdrop = false"
  >
    <div
      v-if="itemdrop"
      class="upload-draggable is-full-page"
      style="width: 100%;height: 100%;margin: auto;"
      @dragenter="dragHandler"
      @dragover="dragHandler"
      @dragleave="dragLeaveHandler"
      @drop="navUpload"
    >
      <p class="has-text-centered">
        {{ $t('message.dropFiles') }}
      </p>
    </div>
    <div
      v-else
      id="subContainer"
    >
      <BrowserNavbar
        :langs="langs"
        :multiple-projects="multipleProjects"
        :projects="projects"
      />
      <ProgressBar v-if="isUploading || isChunking" />
      <b-breadcrumb
        style="margin-left:5%;margin-top:1%;font-size:1rem;"
      >
        <b-breadcrumb-item
          v-for="item in getRouteAsList ()"
          :key="item.alias"
          :to="item.address"
          tag="router-link"
        >
          {{ item.alias | truncate(100) }}
        </b-breadcrumb-item>
      </b-breadcrumb>
      <router-view />
      <b-loading
        :is-full-page="isFullPage"
        :active.sync="isLoading"
        :can-cancel="false"
      />
      <footer
        id="footer"
        class="footer"
      >
        <div class="content has-text-centered">
          <p>
            <span class="has-text-weight-bold">
              {{ $t("message.program_name") }}
            </span> {{ $t("message.devel") }}
            <a 
              href="https://csc.fi"
              :alt="$t('message.cscOrg')"
            >{{ $t("message.cscOrg") }}</a>
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

<style>
html, body {
  height: 100%;
}

#mainContainer {
  height: 100%;
}

#subContainer {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.contents {
  flex: 1 0 auto;
}

.navbar .container .navbar-brand .navbar-item img {
	max-height: 2.5rem;
}

.hero-body #login-center{
    padding: 30px 20px 20px 20px;
}

.hero-body .footer {
    margin:15px 0;
    padding:0;
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

.groupControls {
    margin: 0 5%;
}

.dashboard {
    margin-left: 5%;
    margin-right: 5%;
}

.footer {
  flex-shrink: 0;
}
</style>
