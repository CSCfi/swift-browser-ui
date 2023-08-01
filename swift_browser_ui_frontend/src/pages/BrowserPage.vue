<template>
  <div id="mainContainer">
    <nav>
      <BrowserMainNavbar :langs="langs" />
      <BrowserSecondaryNavbar
        :multiple-projects="multipleProjects"
        :projects="projects"
      />
    </nav>
    <div
      id="mainContent"
      role="main"
    >
      <c-modal
        v-model="openCreateFolderModal"
        v-csc-control
        width="64vw"
      >
        <CreateFolderModal />
      </c-modal>
      <c-modal
        v-model="openUploadModal"
        v-csc-control
        width="64vw"
      >
        <UploadModal />
      </c-modal>
      <UploadNotification
        v-if="displayUploadNotification"
        @cancel-upload="currentUpload.cancelUpload()"
      />
      <c-modal
        id="edit-tags-modal"
        v-model="openEditTagsModal"
        v-csc-control
        width="64vw"
      >
        <EditTagsModal />
      </c-modal>
      <c-modal
        id="share-modal"
        v-model="openShareModal"
        v-csc-control
        width="64vw"
      >
        <ShareModal />
      </c-modal>
      <c-modal
        v-model="openCopyFolderModal"
        v-csc-control
        width="64vw"
      >
        <CopyFolderModal />
      </c-modal>
      <c-modal
        v-model="openDeleteModal"
        v-csc-control
      >
        <DeleteModal />
      </c-modal>
      <c-modal
        v-model="openTokenModal"
        v-csc-control
        width="64vw"
      >
        <TokenModal />
      </c-modal>
      <router-view class="content-wrapper" />
      <c-toasts id="toasts" />
      <c-toasts
        id="copyFolder-toasts"
        vertical="top"
      >
        <div class="toasts-wrapper">
          <h5 class="title is-5">
            {{ $t("message.copysuccess") }}
          </h5>
          <p class="has-text-weight-semibold">
            {{ $t("message.copytime") }}
          </p>
        </div>
      </c-toasts>
      <c-toasts
        id="container-error-toasts"
        vertical="top"
        horizontal="center"
      />
    </div>
    <CFooter />
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

html, body {
  height: 100vh;
}

body {
  overflow-y: auto;
}

#mainContainer {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

#mainContent {
  height: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  z-index: 1;
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

#copyFolder-toasts {
  position: sticky;
  bottom: 30vh;
}

.toasts-wrapper {
  padding: 1rem;
}

.taginput-label {
  font-weight: bold;
  margin-bottom: -2rem;
}

#container-error-toasts {
  margin-top: 50vh;
}

.button-focus {
  outline: 2px var(--csc-primary) solid;
  outline-offset: 2px;
  border-radius: 4px;
}
</style>
