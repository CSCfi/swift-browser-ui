<template>
  <form 
    enctype="multipart/form-data"
    method="post"
    name="contFolders"
    @submit.prevent="folderUpload ()"
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
    folderUpload: function () {
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
      swiftCreateContainer(containerName).then(
        getUploadSignature(
          containerName,
          undefined,
          files.files.length
        ).then((signature) => {
          console.log(signature);
          uploadData.append("redirect", "");
          uploadData.append("max_file_size", signature.max_file_size);
          uploadData.append("max_file_count", signature.max_file_count);
          uploadData.append("expores", signature.expires);
          uploadData.append("signature", signature.signature);

          let address = signature.host.concat(
            signature.path
          );
          return new URL(address);
        }).then((uploadUrl) => {
          fetch(uploadUrl, {
            method: "POST",
            body: uploadData,
          });
        })
      );
      console.log("File upload successful");
    },
  },
};
</script>
