<template>
  <c-toasts id="upload-toast">
    <div class="toast-wrapper">
      <c-row justify="space-between">
        <div class="col">
          <h3 v-if="!notificationToggled">
            {{ $t("message.upload.hasStarted") }}
          </h3>
          <h3 v-else>
            {{ $t("message.upload.longProgress") }}{{ currentFile }}
          </h3>
        </div>
        <div class="col">
          <a
            ref="minimize"
            href="javascript:void(0)"
            class="toggle-notification"
            @click="minimizeToast"
          >
            {{ $t("message.upload.minimize") }}
            <i
              slot="icon"
              class="mdi mdi-arrow-collapse"
            />
          </a>
        </div>
      </c-row>

      <div class="toast-main">
        <p>
          {{ $t("message.upload.estimate") }}
          <a
            class="link-underline"
            href="javascript:void(0)"
            @click="$emit('view-container')"
          >
            {{ $t("message.upload.viewDestinationFolder") }}
          </a>
        </p>

        <ProgressBar class="progress-bar" />

        <c-button
          outlined
          @click="cancelUpload"
          @keyup.enter="cancelUpload"
        >
          {{ $t("message.share.cancel") }}
        </c-button>
      </div>
    </div>
  </c-toasts>
</template>

<script>
import ProgressBar from "./UploadProgressBar.vue";

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
        this.$refs.minimize.focus();
      }, 100);
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
@import "@/css/prod.scss";

.toast-wrapper {
  padding: 1rem;
  color: $csc-grey;
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
