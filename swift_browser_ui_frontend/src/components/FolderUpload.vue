<template>
  <div>
    <b-button
      v-if="isUploading"
      type="is-primary"
      outlined
      @click="res.cancel()"
    >
      <b-icon
        icon="cancel"
        size="is-small"
      />{{ $t('message.cancelupload') }}
    </b-button>
    <a
      v-else
      :id="id"
      class="button is-outlined is-primary"
    >
      <b-icon
        icon="upload"
        size="is-small"
      />{{ $t('message.upload') }}
    </a>
  </div>
</template>

<script>
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
      containerName: undefined,
      address: "",
      resum: undefined,
    };
  },
  computed: {
    active () {
      return this.$store.state.active;
    },
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
      this.res.assignBrowse(document.getElementById(this.id));
      if(this.dropelement != "") {
        this.res.assignDrop(document.getElementById(this.dropelement));
      }
    },
  },
};
</script>
