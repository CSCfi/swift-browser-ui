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
      maximized: true,
      project: "",
      user: "",
      container: "",
      notificationToggled: false,
    };
  },
  computed: {
    closable() {
      return this.$store.state.uploadNotificationClosable;
    },
  },
  watch: {
    closable: function() {
      if (!this.closable) {
        this.container = this.$store.state.selectedFolderName;
      }
    },
  },
  mounted() {
    this.project = this.$store.state.active.id;
    this.user = this.$store.state.uname;
    this.container = this.$store.state.selectedFolderName;
  },
  methods: {
    toggleNotification() {
      this.maximized = !this.maximized;
      this.notificationToggled = true;
    },
    onCancel() {
      this.$emit("cancel-upload");
      this.$store.commit("toggleUploadNotification", false);
    },
    onClosed() {
      this.$store.commit("toggleUploadNotification", false);
    },
    viewContainer() {
      if (this.$route.params.container !== this.container) {
        this.$router.push({
          name: "ObjectsView",
          params: {
            user: this.user,
            project: this.project,
            container: this.container,
          }},
        );
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
