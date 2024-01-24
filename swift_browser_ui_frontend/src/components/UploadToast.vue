<template>
  <c-toasts id="upload-toast">
    <div class="toast-wrapper">
      <c-row justify="space-between">
        <div class="col">
          <h3>
            {{ closable ?
              $t("message.upload.complete") :
              $t("message.upload.inProgress") }}
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
import { getElementHeightPx } from "@/common/globalFunctions";
import ProgressBar from "@/components/UploadProgressBar.vue";

export default {
  name: "UploadToast",
  components: {
    ProgressBar,
  },
  emits: ["view-container", "close-upload", "cancel-upload"],
  data() {
    return {
      moved: false,
    };
  },
  computed: {
    currentFile() {
      return this.$store.state.encryptedFile;
    },
    closable() {
      return this.$store.state.uploadNotification.closable;
    },
    downNotification() {
      return this.$store.state.downloadNotification;
    },
  },
  watch: {
    downNotification: {
      handler() {
        if (this.moved && !this.downNotification.visible ||
          !this.downNotification.maximized
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
        document.querySelector("#upload-toast").addToast({
          id: "upload-toast",
          type: "success",
          persistent: true,
          custom: true,
          horizontal: "center",
        });
        if (this.downNotification.visible && this.downNotification.maximized) {
          this.moveToast();
        }
        else this.moved = false;
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
      this.$store.commit("toggleUploadNotificationSize");
      this.removeToast();
    },
    removeToast() {
      document.querySelector("#upload-toast").removeToast("upload-toast");
    },
    moveToast(restore = false) {
      let toast = document.querySelector("c-toasts#upload-toast");
      if (restore) {
        toast.style.marginBottom = "0";
        this.moved = false;
      }
      else {
        const h = getElementHeightPx(document
          .getElementById("download-toasts"));
        toast.style.marginBottom = h + "px";
        this.moved = true;
      }
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
