<template>
  <c-toasts :id="type + '-toasts'">
    <div class="toast-wrapper">
      <c-row
        justify="space-between"
        align="center"
      >
        <h3>
          {{
            finished
              ? type === "upload"
                ? $t("message.upload.complete")
                : $t("message.download.complete")
              : type === "upload"
                ? $t("message.upload.inProgress")
                : $t("message.download.inProgress")
          }}
        </h3>
        <c-icon-button
          size="small"
          text
          @click="toggleSize"
          @keyup.enter="toggleSize"
        >
          <c-icon :path="mdiArrowCollapse" />
        </c-icon-button>
      </c-row>

      <ProgressBar :type="type" />

      <c-row
        v-if="type === 'upload'"
        gap="5px"
      >
        <span v-if="!finished">
          {{ $t("message.upload.estimate") }}
        </span>
        <a
          href="javascript:void(0)"
          class="link-underline"
          @click="$emit('view-container')"
        >
          {{ $t("message.upload.viewDestinationFolder") }}
        </a>
      </c-row>

      <div
        v-if="type === 'download' && downloadOngoing"
        class="download-warning"
      >
        <p>{{ $t("message.download.warnWait") }}</p>
        <p>{{ $t("message.download.warnTempFiles") }}</p>
      </div>

      <c-button
        v-if="!finished && type === 'upload'"
        outlined
        @click="cancelUpload"
        @keyup.enter="cancelUpload"
      >
        {{ $t("message.share.cancel") }}
      </c-button>
      <c-button
        v-else
        outlined
        @click="close"
        @keyup.enter="close"
      >
        {{ $t("message.share.close") }}
      </c-button>
    </div>
  </c-toasts>
</template>

<script>
import { moveToast } from "@/common/globalFunctions";
import ProgressBar from "@/components/ProgressBar.vue";
import { mdiArrowCollapse } from "@mdi/js";

export default {
  name: "ProgressToast",
  components: {
    ProgressBar,
  },
  props: ["type"],
  emits: ["view-container", "close", "cancel-upload"],
  data() {
    return {
      mdiArrowCollapse,
      toastMoved: false,
    };
  },
  computed: {
    finished() {
      return this.type === "upload"
        ? this.$store.state.uploadNotification.closable
        : this.$store.state.downloadCount < 1;
    },
    otherNotification() {
      return this.type === "upload"
        ? this.$store.state.downloadNotification
        : this.$store.state.uploadNotification;
    },
    otherNotificationType() {
      return this.type === "upload" ? "download" : "upload";
    },
    downloadOngoing() {
      return this.$store.state.downloadCount > 0;
    },
  },
  watch: {
    otherNotification: {
      handler() {
        if (
          (this.toastMoved && !this.otherNotification.visible) ||
          !this.otherNotification.maximized
        ) {
          //restore toast position if no overlap
          this.moveToast(true);
        }
      },
      deep: true,
    },
  },
  mounted() {
    this.openNotification();
  },
  methods: {
    openNotification() {
      setTimeout(() => {
        document.querySelector(`#${this.type}-toasts`).addToast({
          id: `${this.type}-toast`,
          type: "success",
          persistent: true,
          custom: true,
          horizontal: "center",
        });
        if (
          this.otherNotification.visible &&
          this.otherNotification.maximized
        ) {
          this.moveToast();
        } else this.toastMoved = false;
      }, 0);
    },
    close() {
      this.removeToast();
      this.$emit("close");
    },
    cancelUpload() {
      this.removeToast();
      this.$emit("cancel-upload");
    },
    toggleSize() {
      this.type === "upload"
        ? this.$store.commit("toggleUploadNotificationSize")
        : this.$store.commit("toggleDownloadNotificationSize");
      this.removeToast();
    },
    removeToast() {
      document
        .querySelector(`#${this.type}-toasts`)
        .removeToast(`#${this.type}-toast`);
    },
    moveToast(restore = false) {
      const otherToast = document?.querySelector(
        `c-toasts#${this.otherNotificationType}-toasts`,
      );
      const toastToMove = document?.querySelector(
        `c-toasts#${this.type}-toasts`,
      );
      moveToast(toastToMove, otherToast, restore);
      this.toastMoved = !restore;
    },
  },
};
</script>

<style scoped lang="scss">
.toast-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  color: $csc-dark;
}

h3 {
  font-size: 20px;
}

.download-warning {
  display: inherit;
  flex-direction: inherit;
  gap: 0.5rem;
}
</style>
