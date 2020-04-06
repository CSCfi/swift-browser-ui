<template>
  <div id="up-progress">
    <b-progress
      v-if="isChunking && !isUploading"
      type="is-primary"
    >
      {{ $t('message.chunking') }}
    </b-progress>
    <b-progress
      v-else-if="isUploading && progress != undefined"
      type="is-primary"
      :value="progress * 100"
      show-value
    >
      {{ $t('message.uploading') }} {{ (progress * 100).toFixed(1) }}%
    </b-progress>
    <b-progress
      v-else-if="isUploading"
      type="is-primary"
    >
      {{ $t('message.uploading') }}
    </b-progress>
  </div>
</template>

<style scoped>
#up-progress {
  margin-left: 5%;
  margin-right: 5%;
  margin-top: 2%;
  margin-bottom: 3%;
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
