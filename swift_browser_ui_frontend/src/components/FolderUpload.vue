<template>
  <div>
    <a
      :id="id"
      class="button is-outlined is-primary"
    >
      {{ $t('message.upload') }}
    </a>
    <b-button
      v-if="isUploading"
      @click="res.cancel()"
    >
      {{ t('cancelupload') }}
    </b-button>
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
