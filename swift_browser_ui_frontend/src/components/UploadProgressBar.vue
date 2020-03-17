<template>
  <b-progress
    v-if="isChunking && !isUploading"
    type="is-primary"
    size="is-large"
  >
    Chunking
  </b-progress>
  <b-progress
    v-else-if="isUploading"
    type="is-primary"
    :value="progress"
    size="is-large"
    show-value
  >
    Uploading {{ (progress * 100).toFixed(1) }}%
  </b-progress>
</template>

<script>
export default {
  name: "ProgressBar",
  computed: {
    isChunking () {
      return this.$store.state.isChunking;
    },
    isUploading () {
      return this.$store.state.isUploading;
    },
    progress () {
      return this.$store.state.uploadProgress;
    },
  },
};
</script>
