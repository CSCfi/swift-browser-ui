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
    containerName() {
      return this.$store.state.uploadFolder.name;
    },
    containerOwner() {
      return this.$store.state.uploadFolder.owner;
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
      this.$emit("cancel-current-upload", this.containerName);
      this.onClosed();
    },
    onClosed() {
      //close and reset to maximized
      this.$store.commit("toggleUploadNotification", false);
      if (!this.upNotification.maximized) this.toggleNotification();
    },
    viewContainer() {
      if (this.$route.params.container === this.containerName) {
        if (this.$route.query.prefix) {
          //go to container root
          this.$router.push({ query: null });
        }
      }
      else {
        if (this.containerOwner) {
          this.$router.push({
            name: "SharedObjects",
            params: {
              container: this.containerName,
              owner: this.containerOwner,
            },
          });
        }
        else {
          this.$router.push({
            name: "ObjectsView",
            params: {
              container: this.containerName,
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

::v-deep(.link-underline){
  text-decoration: underline;
  color: $csc-blue;
}

::v-deep(i) {
  font-size: 120%;
}

</style>
