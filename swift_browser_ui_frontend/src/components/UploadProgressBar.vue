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
      v-if="isUploading && fileProgress != undefined"
      type="is-primary"
      :value="fileProgress * 100"
      show-value
    >
      Uploading {{ encryptedFile }}
    </b-progress>
    <b-progress
      v-if="isUploading && encryptedProgress != undefined"
      type="is-primary"
      :value="encryptedProgress * 100"
      show-value
    >
      Uploading encrypted data
    </b-progress>
    <b-progress
      v-else-if="isUploading"
      type="is-primary"
    >
      {{ $t('message.uploading') }}
    </b-progress>
  </div>
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
    encryptedProgress () {
      return this.$store.state.encryptedProgress;
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

<style scoped>
#up-progress {
  margin-left: 5%;
  margin-right: 5%;
  margin-top: 1%;
  margin-bottom: 1%;
}
</style>
