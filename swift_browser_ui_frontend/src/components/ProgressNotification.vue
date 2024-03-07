<template>
  <ProgressToast
    v-if="maximized"
    :type="type"
    :finished="finished"
    @toggleSize="toggleSize"
    @close="onClose"
    @cancel-upload="onCancelUpload"
    @view-container="viewUploadContainer"
  />
  <ProgressAlert
    v-else
    :type="type"
    :finished="finished"
    @toggleSize="toggleSize"
    @close="onClose"
    @view-container="viewUploadContainer"
  />
</template>

<script>
import ProgressToast from "@/components/ProgressToast.vue";
import ProgressAlert from "@/components/ProgressAlert.vue";
export default {
  name: "ProgressNotification",
  components: {
    ProgressToast,
    ProgressAlert,
  },
  props: {
    type: {
      type: String,
      default: "upload",
      validator(value) {
        return value === "upload" || value === "download";
      },
    },
  },
  emits: ["cancel-current-upload"],
  computed: {
    finished() {
      return this.type === "upload"
        ? !this.$store.state.isUploading
        : this.$store.state.downloadCount < 1;
    },
    maximized() {
      return this.type === "upload"
        ? this.$store.state.uploadNotification.maximized
        : this.$store.state.downloadNotification.maximized;
    },
    uploadContName() {
      return this.$store.state.uploadFolder.name;
    },
    uploadContOwner() {
      return this.$store.state.uploadFolder.owner;
    },
  },
  methods: {
    toggleSize() {
      this.type === "upload"
        ? this.$store.commit("toggleUploadNotificationSize")
        : this.$store.commit("toggleDownloadNotificationSize");
    },
    onClose() {
      //close and reset to maximized
      this.type === "upload"
        ? this.$store.commit("toggleUploadNotification", false)
        : this.$store.commit("toggleDownloadNotification", false);
      if (!this.maximized) this.toggleSize();
    },
    /* UPLOAD */
    onCancelUpload() {
      this.$emit("cancel-current-upload", this.uploadContName);
      this.onClosed();
    },
    viewUploadContainer() {
      if (this.$route.params.container === this.uploadContName) {
        if (this.$route.query.prefix) {
          //go to container root
          this.$router.push({ query: null });
        }
      } else {
        if (this.uploadContOwner) {
          this.$router.push({
            name: "SharedObjects",
            params: {
              container: this.uploadContName,
              owner: this.uploadContOwner,
            },
          });
        } else {
          this.$router.push({
            name: "ObjectsView",
            params: {
              container: this.uploadContName,
            },
          });
        }
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

::v-deep(.link-underline) {
  text-decoration: underline;
  color: $csc-blue;
}

::v-deep(i) {
  font-size: 120%;
}
</style>
