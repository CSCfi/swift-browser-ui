<template>
  <form 
    enctype="multipart/form-data"
    method="POST"
    :action.sync="address"
  >
    <input
      type="hidden"
      name="redirect"
      :value.sync="redirect"
    >
    <input
      type="hidden"
      name="max_file_size"
      :value.sync="max_file_size"
    >
    <input
      type="hidden"
      name="max_file_count"
      :value.sync="max_file_count"
    >
    <input
      type="hidden"
      name="expires"
      :value.sync="expires"
    >
    <input
      type="hidden"
      name="signature"
      :value.sync="signature"
    >
    <input
      type="file"
      name="to-upload"
      @change="prepareSignature"
    >
    <input type="submit">
  </form>
</template>

<script>
import {
  getUploadSignature,
} from "@/common/api";

export default {
  name: "FileUploadForm",
  data: function () {
    return {
      address: "",
      redirect: "",
      max_file_size: 0,
      max_file_count: 0,
      expires: 0,
      signature: "",
    };
  },
  methods: {
    prepareSignature: function () {
      // Prepare signature for the file upload.
      getUploadSignature(
        this.$route.params.container,
        1,
        "",
        document.location
      ).then((ret) => {
        this.address = ret.host.concat(ret.path);
        this.max_file_size = ret.max_file_size;
        this.max_file_count= ret.max_file_count;
        this.expires = ret.expires;
        this.signature = ret.signature;
        this.redirect = document.location.toString();
      });
    },
  },
};
</script>
