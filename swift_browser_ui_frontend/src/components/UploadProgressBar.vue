<template>
  <div id="up-progress">
    <b-progress
      v-if="isChunking && !isUploading"
      type="is-primary"
      size="is-large"
    >
      Chunking
    </b-progress>
    <b-progress
      v-else-if="isUploading && progress != undefined"
      type="is-primary"
      :value="progress * 100"
      size="is-large"
      show-value
    >
      Uploading {{ (progress * 100).toFixed(1) }}%
    </b-progress>
    <b-progress
      v-else-if="isUploading"
      type="is-primary"
      size="is-large"
    >
      Uploading
    </b-progress>
  </div>
</template>

<style scoped>
#up-progress {
  margin-left: 5%;
  margin-right: 5%;
  margin-top: 1%;
  margin-bottom: 2%;
}
</style>

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
