<template>
  <b-button
    v-if="disabled"
    tag="a"
    type="is-primary"
    outlined
    target="_blank"
    :inverted="inverted"
    disabled
  >
    <b-icon
      icon="download"
      size="is-small"
    /> {{ $t('message.downloadContainer') }}
  </b-button>
  <b-button
    v-else
    tag="a"
    type="is-primary"
    outlined
    target="_blank"
    :inverted="inverted"
    :href="download_link"
  >
    <b-icon
      icon="download"
      size="is-small"
    /> {{ $t('message.downloadContainer') }}
  </b-button>
</template>

<script>
export default {
  name: "ContainerDownloadLink",
  props: [
    "container",
    "project",
    "inverted",
    "disabled",
  ],
  data: function () {
    return {
      download_link: "",
    };
  },
  computed: {
    active () {
      return this.$store.state.active;
    },
  },
  beforeMount () {
    this.createDownloadLink();
  },
  methods: {
    createDownloadLink: function () {
      if (this.$route.params.container != undefined) {
        if (this.$route.name == "SharedObjects") {
          this.download_link = "/download/".concat(
            this.$route.params.owner,
            "/",
            this.$route.params.container,
          );
        }
        else {
          this.download_link = "/download/".concat(
            this.active.id,
            "/",
            this.$route.params.container,
          );
        }
      }
      else {
        if (this.$route.name == "SharedTo") {
          this.download_link = "/download/".concat(
            this.$props.project,
            "/",
            this.$props.container,
          );
        }
        else {
          this.download_link = "/download/".concat(
            this.active.id,
            "/",
            this.$props.container,
          );
        }
      }
    },
  },
};
</script>
