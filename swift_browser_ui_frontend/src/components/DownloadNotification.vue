<template>
  <c-toasts
    v-if="downNotification.visible && downNotification.maximized"
    id="download-toasts"
  >
    <div class="toast-wrapper">
      <c-row justify="space-between">
        <h3>
          {{ progress === 1 ?
            $t("message.download.complete") :
            $t("message.download.inProgress") }}
        </h3>
        <div>
          <a @click="toggleSize">
            <i
              slot="icon"
              class="mdi mdi-arrow-collapse"
            />
          </a>
        </div>
      </c-row>

      <div class="toast-main">
        <template v-if="progress != 1">
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
          <p>{{ $t("message.download.warnWait") }}</p>
          <p>{{ $t("message.download.warnTempFiles") }}</p>
        </template>
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

  <c-alert
    v-if="downNotification.visible && !downNotification.maximized"
    type="success"
  >
    <c-row
      gap="64"
      align="center"
      justify="space-between"
    >
      <h3>
        {{ progress === 1 ?
          $t("message.download.complete") :
          $t("message.download.inProgress") }}
      </h3>

      <div
        v-if="progress != 1"
        class="progress-bar"
      >
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
      </div>
      <div class="actions">
        <a @click="toggleSize">
          <i
            slot="icon"
            class="mdi mdi-arrow-expand"
          />
        </a>
        <a @click="closeNotification">
          <i
            slot="icon"
            class="mdi mdi-close"
          />
        </a>
      </div>
    </c-row>
  </c-alert>
</template>

<script>
import { getElementHeightPx } from "@/common/globalFunctions";

export default {
  name: "DownloadNotification",
  data() {
    return {
      moved: false,
    };
  },
  computed: {
    progress() {
      return this.$store.state.downloadProgress;
    },
    downNotification() {
      return this.$store.state.downloadNotification;
    },
    upNotification() {
      return this.$store.state.uploadNotification;
    },
  },
  watch: {
    upNotification: {
      handler() {
        if (this.moved && (!this.upNotification.visible ||
          !this.upNotification.maximized)) {
          this.moveToast(true);
        }
      },
      deep: true,
    },
  },
  mounted() {
    this.addToast();
  },
  methods: {
    addToast() {
      setTimeout(() => {
        document.querySelector("#download-toasts").addToast({
          id: "download-toast",
          type: "success",
          persistent: true,
          custom: true,
        });
        if (this.upNotification.visible && this.upNotification.maximized) {
          this.moveToast();
        }
        else this.moved = false;
      },0);
    },
    closeNotification() {
      this.$store.commit("toggleDownloadNotification", false);
      this.removeToast();
      if (!this.downNotification.maximized) {
        this.$store.commit("toggleDownloadNotificationSize");
      }
    },
    toggleSize() {
      this.$store.commit("toggleDownloadNotificationSize");
      if (this.downNotification.maximized) this.addToast();
      else this.removeToast();
    },
    removeToast() {
      document.querySelector("#download-toasts")?.removeToast("download-toast");
      this.moved = false;
    },
    moveToast(restore = false) {
      let toast = document.querySelector("c-toasts#download-toasts");
      if (restore) {
        toast.style.marginBottom = "0";
        this.moved = false;
      }
      else {
        const h = getElementHeightPx(document
          .getElementById("upload-toast"));
        toast.style.marginBottom = h + "px";
        this.moved = true;
      }
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

c-alert {
  margin: 1rem 5%;
}

c-alert h3 {
  font-size: 18px;
}

.actions a {
  margin-left: 2rem;
}

.progress-bar {
  flex: 1;
}

</style>
