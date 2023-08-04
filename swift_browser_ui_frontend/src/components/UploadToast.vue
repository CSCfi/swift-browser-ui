<template>
  <c-toasts id="upload-toast">
    <div class="toast-wrapper">
      <c-row justify="space-between">
        <div class="col">
          <h3 v-if="closable">
            {{ $t("message.upload.complete") }}
          </h3>
          <h3 v-else-if="!notificationToggled">
            {{ $t("message.upload.hasStarted") }}
          </h3>
          <h3 v-else>
            {{ $t("message.upload.longProgress") }}
          </h3>
        </div>
        <div class="col">
          <a
            ref="minimize"
            href="javascript:void(0)"
            class="toggle-notification"
            @click="minimizeToast"
          >
            <i
              slot="icon"
              class="mdi mdi-arrow-collapse"
            />
          </a>
        </div>
      </c-row>

      <div class="toast-main">
        <c-row gap="5px">
          <span v-if="!closable">
            {{ $t("message.upload.estimate") }}
          </span>
          <a
            class="link-underline"
            href="javascript:void(0)"
            @click="$emit('view-container')"
          >
            {{ $t("message.upload.viewDestinationFolder") }}
          </a>
        </c-row>

        <ProgressBar class="progress-bar" />

        <c-button
          v-if="!closable"
          outlined
          @click="cancelUpload"
          @keyup.enter="cancelUpload"
        >
          {{ $t("message.share.cancel") }}
        </c-button>
        <c-button
          v-else
          outlined
          @click="closeUpload"
          @keyup.enter="closeUpload"
        >
          {{ $t("message.share.close") }}
        </c-button>
      </div>
    </div>
  </c-toasts>
</template>

<script>
import ProgressBar from "@/components/UploadProgressBar.vue";

export default {
  name: "UploadToast",
  components: {
    ProgressBar,
  },
  props: ["notificationToggled"],
  computed: {
    currentFile() {
      return this.$store.state.encryptedFile;
    },
    closable() {
      return this.$store.state.uploadNotificationClosable;
    },
  },
  mounted() {
    this.openNotification();
  },
  methods: {
    openNotification() {
      setTimeout(() => {
        document.querySelector("#upload-toast").addToast({
          id: "upload-toast",
          type: "success",
          persistent: true,
          custom: true,
          horizontal: "center",
        });
      },0);

      setTimeout(() => {
        this.$refs.minimize?.focus();
      }, 100);
    },
    closeUpload() {
      this.removeToast();
      this.$emit("close-upload");
    },
    cancelUpload() {
      this.removeToast();
      this.$emit("cancel-upload");
    },
    minimizeToast() {
      this.removeToast();
      this.$emit("toggle-notification");
    },
    removeToast() {
      document.querySelector("#upload-toast").removeToast("upload-toast");
    },
  },
};
</script>

<style scoped lang="scss">

.toast-wrapper {
  padding: 1rem;
  color: $csc-dark;
}

.progress-bar {
  padding: 1rem 0;
}

h3 {
  font-size: 20px;
}

.toast-main {
  padding-top: 1rem;
}

</style>
