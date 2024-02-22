<template>
  <div class="progress-bar">
    <c-progress-bar
      v-if="isUploading && progress != undefined"
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
    isUploading() {
      return this.$store.state.isUploading;
    },
    progress() {
      return this.$store.state.uploadProgress;
    },
  },
};
</script>

<style scoped lang="scss">

.progress-bar {
  flex: 1
}

</style>
