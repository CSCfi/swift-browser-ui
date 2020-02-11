<template>
  <form 
    enctype="multipart/form-data"
    method="post"
    name="contFolders"
    @submit.prevent="callUpload ()"
  >
    <input
      id="directoryFileList"
      type="file"
      name="fileList"
      webkitdirectory
      multiple
    >
    <input
      type="submit"
      value="Upload a folder"
    >
  </form>
</template>

<script>
import {
  getUploadSignature,
  swiftCreateContainer,
} from "@/common/api";

export default {
  name: "FolderUploadForm",
  methods: {
    callUpload: function () {
      // Wrapper for the asynchronous upload function
      this.folderUpload().then(() => {
        console.log("Called folder upload");
      });
    },
    folderUpload: async function () {
      // Upload a folder using Openstack Swift FormPost API

      let containerName = "swift-browser-ui-upload-".concat(
        Date.now().toString()
      );
      console.log(containerName);
      let form = document.forms.namedItem("contFolders");
      let files = form.elements["fileList"];
      console.log(files);
      let uploadData = new FormData(form);

      console.log("Creating container");
      await swiftCreateContainer(containerName);
      console.log("Container creation successful");

      let signature = await getUploadSignature(
        containerName,
        files.files.length,
        undefined
      );
      console.log(signature);

      uploadData.append("redirect", "");
      uploadData.append("max_file_size", signature.max_file_size);
      uploadData.append("max_file_count", signature.max_file_count);
      uploadData.append("expires", signature.expires);
      uploadData.append("signature", signature.signature);

      let address = new URL(signature.host.concat(signature.path));

      console.log(uploadData);

      await fetch(address, {
        method: "POST",
        body: uploadData,
      });
      console.log("File upload successful");
    },
  },
};
</script>
