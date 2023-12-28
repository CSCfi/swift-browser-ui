<template>
  <c-toasts
    id="download-toasts"
  >
    <div class="toast-wrapper">
      <c-row justify="space-between">
        <h3>
          {{ progress === 1 ?
            $t("message.download.complete") :
            $t("message.download.inProgress") }}
        </h3>
      </c-row>
      <div class="toast-main">
        <c-progress-bar
          v-if="progress != undefined"
          :value="(progress * 100).toFixed()"
          single-line
          :label="$t('message.upload.progressLabel')"
        />
        <c-progress-bar
          v-else
          hide-details
        />
        <c-button
          outlined
          @click="closeNotification"
          @keyup.enter="closeNotification"
        >
          {{ $t("message.share.close") }}
        </c-button>
      </div>
    </div>
  </c-toasts>
</template>

<script>
export default {
  name: "DownloadNotification",
  computed: {
    progress() {
      return this.$store.state.downloadProgress;
    },
  },
  mounted() {
    this.addToast();
  },
  methods: {
    addToast() {
      document.querySelector("#download-toasts").addToast({
        id: "download-toast",
        type: "success",
        persistent: true,
        custom: true,
        horizontal: "center",
      });
    },
    closeNotification() {
      document.querySelector("#download-toasts").removeToast("download-toast");
      this.$store.commit("toggleDownloadNotification", false);
    },
  },
};
</script>

<style lang="scss" scoped>

::v-deep(h3) {
  color: $csc-dark;
  font-weight: 600;
}

::v-deep(i) {
  font-size: 120%;
}

.toast-wrapper {
  padding: 1rem;
  color: $csc-dark;
}

h3 {
  font-size: 20px;
}

.toast-main {
  padding-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}


</style>
