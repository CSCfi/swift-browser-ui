<template>
  <div id="mainContainer">
    <div id="subContainer">
      <BrowserMainNavbar :langs="langs" />
      <BrowserSecondaryNavbar
        :multiple-projects="multipleProjects"
        :projects="projects"
      />
      <ProgressBar v-if="isUploading || isChunking" />
      <c-modal
        v-control
        v-csc-model="openCreateFolderModal"
      >
        <CreateFolderModal />
      </c-modal>
      <c-modal
        v-control
        v-csc-model="openUploadModal"
        width="64vw"
      >
        <UploadModal />
      </c-modal>
      <UploadNotification
        v-if="displayUploadNotification"
        @cancel-upload="currentUpload.cancelUpload()"
      />
      <c-modal
        v-control
        v-csc-model="openEditTagsModal"
        width="64vw"
      >
        <EditTagsModal />
      </c-modal>
      <c-modal
        v-control
        v-csc-model="openShareModal"
        width="50vw"
      >
        <ShareModal />
      </c-modal>
       <c-modal
        v-control
        v-csc-model="openCopyFolderModal"
        width="64vw"
      >
        <CopyFolderModal />
      </c-modal>
      <router-view class="content-wrapper" />
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
            </span>
            {{ $t("message.devel") }}
            <a
              href="https://csc.fi"
              :alt="$t('message.cscOrg')"
            >{{
              $t("message.cscOrg")
            }}</a>
          </p>
        </div>
      </footer>
      <c-toasts id="toasts" />
      <!-- TODO: Move folder toast to programmatical modal -->
      <c-toasts
        id="copyFolder-toasts"
        vertical="top"
      >
        <div class="toasts-wrapper">
          <h5 class="title is-5 has-text-dark">
            {{ this.$t("message.copysuccess") }}
          </h5>
          <p class="has-text-weight-semibold has-text-dark">
            {{ this.$t("message.copytime") }}
          </p>
        </div>
      </c-toasts>
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

.subContainer-additionalStyles {
  position: fixed;
  width: 100%;
}

c-modal {
  position: relative;
  margin: 0 auto;
  display: inline-flex;
}

.modal-content-wrapper {
  overflow-y: scroll;
  scrollbar-width: 0.5rem;
  padding-right: 0.5rem;

  &::-webkit-scrollbar {
    width: 0.5rem;
  }
  &::-webkit-scrollbar-thumb {
    background: var(--csc-mid-grey);
    border-radius: 10px;
    &:hover {
      background: var(--csc-dark-grey);
    }
  }
}

.content-wrapper {
  margin: 0;
  padding: 0;
  padding-bottom: 3rem;
  display: flex;
  flex-direction: column;
}

.contents {
  flex: 1 0 auto;
}

.container-box {
  width: 90%;
  margin-left: 5%;
  margin-right: 5%;
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

#optionsbar {
  display: block;
  padding: 1.5rem 0;
}

.search {
  flex: 0.4;

  input, input::placeholder, .icon {
    color: $csc-grey !important;
  }

  input::placeholder {
    opacity: 0.8;
  }

  input, input:focus {
    box-shadow:rgba(0, 0, 0, 0.15) 0px 5px 15px 0px;
  }

  input {
    border: none;
    &:focus {
      outline: 2px solid $csc-primary;

     & + .icon {
        color: $csc-primary !important;
      }
    }
  }
}

.display-options-menu {
  display: flex;
  align-items: center;
  & .mdi {
    padding-right: .5rem;
    font-size: 18px;
  }
}

#dropArea:before{
  content:"";
  width: 98%;
  height:98%;
  position:absolute;
  border:2px dashed #b5b5b5;
  margin: 0 1%;
  padding: 0;
  border-radius: 6px;
}

.footer {
  flex-shrink: 0;
  height: 10rem;
  width: 100%;
}

#footer {
  margin-top: 15px;
}

#copyFolder-toasts {
  position: sticky;
  bottom: 30vh;
}

.toasts-wrapper {
  padding: 1rem;
}
</style>
