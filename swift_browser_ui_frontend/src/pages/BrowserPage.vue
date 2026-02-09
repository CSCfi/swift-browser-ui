<template>
  <div id="mainContainer" class="main">
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
        v-model="openConfirmRouteModal"
        v-control
        disable-backdrop-blur
      >
        <ConfirmRouteModal />
      </c-modal>
      <c-modal
        v-model="openCreateBucketModal"
        v-control
        disable-backdrop-blur
        width="64vw"
      >
        <CreateBucketModal />
      </c-modal>
      <c-modal
        v-model="openUploadModal"
        v-control
        disable-backdrop-blur
        width="64vw"
      >
        <UploadModal />
      </c-modal>
      <c-modal
        id="edit-tags-modal"
        v-model="openEditTagsModal"
        v-control
        disable-backdrop-blur
        width="64vw"
      >
        <EditTagsModal />
      </c-modal>
      <c-modal
        id="share-modal"
        v-model="openShareModal"
        v-control
        disable-backdrop-blur
        width="64vw"
      >
        <ShareModal />
      </c-modal>
      <c-modal
        id="copy-bucket-modal"
        v-model="openCopyBucketModal"
        v-control
        disable-backdrop-blur
        width="64vw"
      >
        <CopyBucketModal />
      </c-modal>
      <c-modal
        id="delete-objs-modal"
        v-model="openDeleteModal"
        v-control
        disable-backdrop-blur
      >
        <DeleteModal />
      </c-modal>
      <c-modal
        id="api-key-modal"
        v-model="openAPIKeyModal"
        v-control
        disable-backdrop-blur
        width="64vw"
      >
        <APIKeyModal />
      </c-modal>
      <ProgressNotification
        v-if="displayUploadNotification"
        type="upload"
        @cancel-current-upload="cancelUpload"
      />
      <ProgressNotification
        v-if="displayDownloadNotification"
        type="download"
        @cancel-download="cancelDownload"
      />
      <router-view class="content-wrapper" />
      <c-toasts
        id="copyBucket-toasts"
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
import { truncate } from "@/common/tableFunctions";


export default {
  name: "BrowserPage",
  filters: {
    truncate,
  },

};
</script>

<style scoped>

div.main {
  background-color: var(--c-white);
}

#mainContent {
  height: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  z-index: 1;
}

#copyBucket-toasts {
  position: sticky;
  bottom: 30vh;
}

</style>
