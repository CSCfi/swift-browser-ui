<template>
  <div class="progress-bar">
    <c-progress-bar
      v-if="isChunking && !isUploading"
      hide-details
    />

    <c-progress-bar
      v-else-if="isUploading && progress != undefined"
      :value="(progress * 100).toFixed(1)"
      single-line
      :label="$t('message.upload.complete')"
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
  },
};
</script>

<style scoped lang="scss">
@import "@/css/prod.scss";

.progress-bar {
  flex: 1
}

</style>
