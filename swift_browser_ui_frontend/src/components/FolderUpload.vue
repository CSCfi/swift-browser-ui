<template>
  <div>
    <b-button
      v-if="isUploading"
      type="is-primary"
      outlined
      icon-left="cancel"
      @click="res.cancel()"
    >
      {{ $t('message.cancelupload') }}
    </b-button>
    <b-field 
      v-else
      class="file is-primary"
    >
      <b-upload
        v-model="files"
        class="file-label"
        multiple
        @input="beginUpload"
      >
        <span class="file-cta">
          <b-icon
            class="file-icon"
            icon="upload"
          />
          <span class="file-label">{{ $t('message.upload') }}</span>
        </span>
      </b-upload>
    </b-field>
  </div>
</template>

<script>
import { getUploadEndpoint } from "@/common/api";

export default {
  name: "FolderUploadForm",
  props: {
    dropelement: {
      default: "",
      type: String,
    },
  },
  data: function () {
    return {
      id: "upload-".concat(Date.now().toString()),
      files: [],
    };
  },
  computed: {
    res () {
      return this.$store.state.resumableClient;
    },
    isUploading () {
      return this.$store.state.isUploading;
    },
    active () {
      return this.$store.state.active;
    },
  },
  methods: {
    aBeginUpload: async function () {
      let altContainer = "upload-".concat(Date.now().toString());
      if (this.$route.params.container) {
        altContainer = this.$route.params.container;
      }

      let uploadInfo = await getUploadEndpoint(
        this.$route.params.owner ? this.$route.params.owner : this.active.id,
        altContainer,
      );
      this.$store.commit("setAltContainer", altContainer);
      this.$store.commit("setUploadInfo", uploadInfo);
      
      this.res.addFiles(this.files, undefined);
    },
    beginUpload: function() {
      this.aBeginUpload();
    },
  },
};
</script>
