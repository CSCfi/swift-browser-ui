<template>
  <div class="progress-bar">
    <c-progress-bar
      v-if="isChunking && !isUploading"
      hide-details
    />

    <c-progress-bar
      v-else-if="isUploading && progress != undefined"
      :value="(progress * 100).toFixed()"
      single-line
      :label="$t('message.upload.progressLabel')"
    />

    <c-progress-bar
      v-else-if="isUploading"
      hide-details
    />
  </div>
</template>

<script>
export default {
  name: "ProgressBar",
  computed: {
    isChunking() {
      return this.$store.state.isChunking;
    },
    isUploading() {
      return this.$store.state.isUploading;
    },
    progress() {
      return this.$store.state.uploadProgress;
    },
    encryptedFile () {
      return this.$store.state.encryptedFile;
    },
    fileProgress () {
      return this.$store.state.encryptedFileProgress;
    },
  },
};
</script>

<style scoped lang="scss">

.progress-bar {
  flex: 1
}

</style>
