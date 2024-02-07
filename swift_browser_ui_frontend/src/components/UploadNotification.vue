<template>
  <UploadToast
    v-if="upNotification.visible && upNotification.maximized"
    @view-container="viewContainer"
    @cancel-upload="onCancel"
    @close-upload="onClosed"
  />
  <UploadAlert
    v-if="upNotification.visible && !upNotification.maximized"
    @view-container="viewContainer"
    @close-upload="onClosed"
  />
</template>

<script>
import UploadToast from "@/components/UploadToast.vue";
import UploadAlert from "@/components/UploadAlert.vue";
export default {
  name: "UploadNotification",
  components: {
    UploadToast,
    UploadAlert,
  },
  emits: ["cancel-current-upload"],
  computed: {
    project() {
      return this.$store.state.active.id;
    },
    user() {
      return this.$store.state.uname;
    },
    container() {
      return this.$store.state.uploadFolderName;
    },
    upNotification() {
      return this.$store.state.uploadNotification;
    },
  },
  methods: {
    toggleNotification() {
      this.$store.commit("toggleUploadNotificationSize");
    },
    onCancel() {
      this.$emit("cancel-current-upload", this.container);
      this.onClosed();
    },
    onClosed() {
      //close and reset to maximized
      this.$store.commit("toggleUploadNotification", false);
      if (!this.upNotification.maximized) this.toggleNotification();
    },
    viewContainer() {
      if (this.$route.params.container !== this.container
        || this.$route.query.prefix) {
        this.$router.push({
          name: "ObjectsView",
          params: {
            user: this.user,
            project: this.project,
            container: this.container,
          },
          query: null,
        });
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

::v-deep(.link-underline){
  text-decoration: underline;
  color: $csc-blue;
}

::v-deep(i) {
  font-size: 120%;
}

</style>
