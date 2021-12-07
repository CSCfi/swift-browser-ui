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
    <UploadButton
      v-else
      :id="id"
    />
  </div>
</template>

<script>
import UploadButton from "@/components/UploadButton";

export default {
  name: "FolderUploadForm",
  components: {
    UploadButton,
  },
  props: {
    dropelement: {
      default: "",
      type: String,
    },
  },
  data: function () {
    return {
      id: "upload-".concat(Date.now().toString()),
    };
  },
  computed: {
    res () {
      return this.$store.state.resumableClient;
    },
    isUploading () {
      return this.$store.state.isUploading;
    },
  },
  mounted () {
    this.registerToResumable();
  },
  methods: {
    registerToResumable: function () {
      // Add elements to listen
      if(this.dropelement != "") {
        this.res.assignDrop(document.getElementById(this.dropelement));
      }
    },
  },
};
</script>
