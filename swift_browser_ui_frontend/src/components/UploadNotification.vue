<template>
  <UploadToast
    v-if="maximized"
    :notification-toggled="notificationToggled"
    @toggle-notification="toggleNotification"
    @view-container="viewContainer"
    @cancel-upload="onCancel"
  />
  <UploadAlert
    v-else
    @toggle-notification="toggleNotification"
    @view-container="viewContainer"
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
  mounted() {
    this.project = this.$store.state.active.id;
    this.user = this.$store.state.uname;
    this.container = this.$route.params.container;
  },
  methods: {
    toggleNotification() {
      this.maximized = !this.maximized;
      this.notificationToggled = true;
    },
    onCancel() {
      this.$emit("cancel-upload");
      this.$store.commit("eraseDropFiles");
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

h3 {
  color: $csc-grey !important;
}

h3, a, .toggle-notification {
  font-weight: 600 !important;
}

.link-underline {
  text-decoration: underline !important;
  color: $csc-blue !important;
}

.toggle-notification {
  font-size: 14px;
  color: $csc-primary !important;
  display: inline-block;

  &:focus {
    border: 2px solid $csc-primary;
    border-radius: 4px;
  }
}

</style>
