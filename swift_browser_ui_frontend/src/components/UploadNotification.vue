<template>
  <UploadToast
    v-if="maximized"
    :notification-toggled="notificationToggled"
    @toggle-notification="toggleNotification"
    @view-container="viewContainer"
    @cancel-upload="onCancel"
    @close-upload="onClosed"
  />
  <UploadAlert
    v-else
    @toggle-notification="toggleNotification"
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
  data() {
    return {
      notificationToggled: false,
    };
  },
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
    maximized() {
      //minimize if download notification shown
      return !this.$store.state.downloadNotification;
    },
  },
  methods: {
    toggleNotification() {
      this.maximized = !this.maximized;
      this.notificationToggled = true;
    },
    onCancel() {
      this.$emit("cancel-current-upload", this.container);
      this.$store.commit("toggleUploadNotification", false);
    },
    onClosed() {
      this.$store.commit("toggleUploadNotification", false);
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
