<template>
  <div
    v-if="!finished"
    class="progress-bar"
  >
    <c-progress-bar
      v-if="progress != undefined"
      :value="(progress * 100).toFixed()"
      single-line
      :label="$t('message.upload.progressLabel')"
    />
    <c-progress-bar
      v-else
      hide-details
    />
  </div>
</template>

<script>
export default {
  name: "ProgressBar",
  props: ["type", "finished"],
  computed: {
    progress() {
      return this.type === "upload"
        ? this.$store.state.uploadProgress
        : this.$store.state.downloadProgress;
    },
  },
};
</script>

<style scoped lang="scss">
.progress-bar {
  flex: 1;
}
</style>
