<template>
  <a
    class="button is-primary is-outlined"
    :href="download_link"
  >
    Download
  </a>
</template>

<script>
export default {
  name: "ContainerDownloadLink",
  props: ["container", "project"],
  data: function () {
    return {
      download_link: "",
    };
  },
  methods: {
    createDownloadLink: function () {
      if (this.$route.params.container != undefined) {
        if (this.$route.name == "SharedObjects") {
          this.download_link = "/download/".concat(
            this.$route.params.owner,
            "/",
            this.$route.params.container
          );
        }
        else {
          this.download_link = "/download/".concat(
            this.$store.state.active.id,
            "/",
            this.$route.params.container
          );
        }
      }
      else {
        if (this.$route.name == "SharedTo") {
          this.download_link = "/download/".concat(
            this.project,
            "/",
            this.container
          );
        }
        else {
          this.download_link = "/download/".concat(
            this.$store.state.active.id,
            "/",
            this.container
          );
        }
      }
    },
  },
};
</script>
