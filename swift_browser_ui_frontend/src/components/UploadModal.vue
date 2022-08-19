<template>
  <c-card class="upload-card">
    <div class="modal-content-wrapper">
      <h3 class="title is-3 has-text-dark">
        {{ $t("message.encrypt.uploadFiles") }}
      </h3>
      <c-card-content>
        <h6 class="title is-6 has-text-dark">
          1. {{ $t("message.encrypt.upload_step1") }}
        </h6>
        <p class="info-text is-size-6">
          {{ $t("message.container_ops.norename") }}
        </p>
        <c-autocomplete
          v-control
          v-csc-model="selectedFolder"
          :items.prop="filteredItems"
          :query="inputFolder"
          :label="$t('message.container_ops.folderName')"
          hide-details
          required
          @changeQuery="onQueryChange"
        />
        <h6 class="title is-6 has-text-dark">
          2. {{ $t("message.encrypt.upload_step2") }}
        </h6>
        <div
          class="dropArea is-flex
                is-align-items-center is-justify-content-center"
          @dragover="dragHandler"
          @dragleave="dragLeaveHandler"
          @drop="navUpload"
        >
          <span>{{ $t("message.dropFiles") }}</span>
          <b-upload
            v-model="files"
            multiple
            accept
            class="file is-primary"
          >
            <span class="file-cta">
              {{ $t("message.encrypt.dropMsg") }}
            </span>
          </b-upload>
        </div>
        <c-data-table
          v-if="dropFiles.length > 0"
          class="files-table"
          :data.prop="dropFiles"
          :headers.prop="fileHeaders"
          :no-data-text="$t('message.encrypt.empty')"
          :pagination.prop="filesPagination"
          :footer-options.prop="footer"
        />
        <p class="info-text is-size-6">
          {{ $t("message.encrypt.uploadedFiles") }}
          <b>{{ active.name }}</b>.
        </p>
        <c-link
          :href="`https://my.csc.fi/myProjects/project/${projectNumber}`"
          underline
          target="_blank"
        >
          {{ $t("message.container_ops.viewProjectMembers") }}
          <i class="mdi mdi-open-in-new" />
        </c-link>
        <c-accordion :value="$t('message.encrypt.advancedOptions')">
          <c-accordion-item
            :heading="$t('message.encrypt.advancedOptions')"
            :value="$t('message.encrypt.advancedOptions')"
          >
            <c-container>
              <c-switch v-csc-model="ownPrivateKey">
                {{ $t("message.encrypt.ephemeral") }}
              </c-switch>
              <c-flex v-if="ownPrivateKey">
                <c-text-field
                  v-csc-model="privkey"
                  :placeholder="$t('message.encrypt.pk_msg')"
                  :label="$t('message.encrypt.pk')"
                  type="text"
                  max="1024"
                />
                <c-text-field
                  v-csc-model="passphrase"
                  :placeholder="$t('message.encrypt.phrase_msg')"
                  :label="$t('message.encrypt.phrase')"
                  type="text"
                  max="1024"
                  rows="5"
                />
              </c-flex>
            </c-container>
            <c-container>
              <c-switch v-csc-model="multipleReceivers">
                {{ $t("message.encrypt.multipleReceivers") }}
              </c-switch>
              <c-flex v-if="multipleReceivers">
                <c-text-field
                  v-csc-model="addRecvkey"
                  :placeholder="$t('message.encrypt.pubkey_msg')"
                  :label="$t('message.encrypt.pubkey')"
                  type="text"
                  max="1024"
                />
                <c-button
                  type="is-success"
                  icon-left="lock-plus"
                  @click="appendPublicKey"
                >
                  {{ $t("message.encrypt.addkey") }}
                </c-button>
                <c-data-table
                  class="publickey-table"
                  :data.prop="recvHashedKeys"
                  :headers.prop="publickeyHeaders"
                  :no-data-text="$t('message.encrypt.noRecipients')"
                  :pagination.prop="keyPagination"
                  :footer-options.prop="footer"
                />
              </c-flex>
            </c-container>
          </c-accordion-item>
        </c-accordion>
      </c-card-content>
    </div>
    <c-card-actions justify="space-between">
      <c-button
        outlined
        size="large"
        @click="cancelUpload"
      >
        {{ $t("message.encrypt.cancel") }}
      </c-button>
      <c-button
        size="large"
        :disabled="noUpload"
        @click="encryptAndUpload"
      >
        {{ $t("message.encrypt.normup") }}
      </c-button>
    </c-card-actions>
  </c-card>
</template>

<script>
import { getUploadEndpoint } from "@/common/api";
import {
  getHumanReadableSize,
  taginputConfirmKeys,
  truncate,
  computeSHA256,
} from "@/common/conv";

import {
  modifyBrowserPageStyles,
  getProjectNumber,
} from "@/common/globalFunctions";

export default {
  name: "UploadModal",
  filters: {
    truncate,
  },
  data() {
    return {
      inputFolder: "",
      selectedFolder: null,
      taginputConfirmKeys,
      filteredItems: [],
      tooLarge: false,
      ownPrivateKey: false,
      ephemeral: true,
      privkey: "",
      passphrase: "",
      multipleReceivers: false,
      addRecvkey: "",
      recvkeys: [],
      recvHashedKeys: [],
      noUpload: true,
      projectNumber: "",
    };
  },
  computed: {
    containers() {
      return this.$store.state.db.containers;
    },
    res() {
      return this.$store.state.resumableClient;
    },
    active() {
      return this.$store.state.active;
    },
    transfer() {
      return this.$store.state.transfer;
    },
    pubkey() {
      return this.$store.state.pubkey;
    },
    fileHeaders() {
      return [
        {
          key: "name",
          value: this.$t("message.encrypt.table.name"),
          width: "30%",
          sortable: this.dropFiles.length > 1,
        },
        {
          key: "type",
          value: this.$t("message.encrypt.table.type"),
          width: "15%",
          sortable: this.dropFiles.length > 1,
        },
        {
          key: "size",
          value: this.$t("message.encrypt.table.size"),
          width: "10%",
          sortable: this.dropFiles.length > 1,
        },
        {
          key: "relativePath",
          value: this.$t("message.encrypt.table.path"),
          width: "30%",
          sortable: this.dropFiles.length > 1,
        },
        {
          key: "remove",
          value: null,
          sortable: false,
          children: [
            {
              value: this.$t("message.remove"),
              component: {
                tag: "c-button",
                params: {
                  text: true,
                  size: "small",
                  title: this.$t("message.remove"),
                  onClick: ({ data }) =>
                    this.$store.commit("eraseDropFile", data),
                },
              },
            },
          ],
        },
      ];
    },
    publickeyHeaders() {
      return [
        {
          key: "key",
          value: this.$t("message.encrypt.pubkeyLabel"),
          width: "70%",
          sortable: this.recvHashedKeys.length > 1,
        },
        {
          key: "remove",
          value: null,
          sortable: false,
          children: [
            {
              value: this.$t("message.remove"),
              component: {
                tag: "c-button",
                params: {
                  text: true,
                  size: "small",
                  title: this.$t("message.remove"),
                  onClick: ({ index }) =>{
                    this.recvHashedKeys.splice(index, 1);
                    this.recvkeys.splice(index, 1);
                  },
                },
              },
            },
          ],
        },
      ];
    },
    dropFiles() {
      return this.$store.state.dropFiles.map(file => {
        return {
          name: { value: file.name || truncate(100) },
          type: { value: file.type },
          size: { value: this.localHumanReadableSize(file.size) },
          relativePath: {
            value:
              (!file.relativePath ? file.name : file.relativePath) ||
              truncate(100),
          },
        };
      });
    },
    files: {
      get() {
        return this.$store.state.dropFiles.message;
      },
      set(value) {
        const files = Array.from(value);
        files.forEach(element => {
          this.$store.commit("appendDropFiles", element);
        });
      },
    },
    filesPagination() {
      return {
        itemCount: this.dropFiles.length,
        itemsPerPage: 20,
        currentPage: 1,
      };
    },
    footer() {
      return {
        hideDetails: true,
      };
    },
    keyPagination() {
      return {
        itemCount: this.recvHashedKeys.length,
        itemsPerPage: 5,
        currentPage: 1,
      };
    },
    currentProjectID() {
      return this.$route.params.project;
    },
  },
  watch: {
    selectedFolder: function() {
      if(this.selectedFolder !== null) {
        this.inputFolder = this.selectedFolder.name;
      }
    },
    inputFolder: function() {
      this.refreshNoUpload();
    },
    dropFiles: function () {
      this.checkUploadSize();
    },
    transfer: function () {
      this.setFiles();
    },
    ownPrivateKey: function() {
      this.ephemeral = !this.ephemeral;
      this.refreshNoUpload();
    },
    privkey: function () {
      this.refreshNoUpload();
    },
    recvkeys: function () {
      this.refreshNoUpload();
    },
    passphrase: function () {
      this.refreshNoUpload();
    },
    ephemeral: function () {
      this.refreshNoUpload();
    },
    active: function () {
      this.projectNumber = getProjectNumber(this.active);
    },
  },
  methods: {
    onQueryChange: function (e) {
      this.inputFolder = e.detail;
      this.getFilteredContainers();
    },
    getFilteredContainers: async function() {
      const result = await this.containers
        .filter(cont => cont.projectID === this.active.id)
        .filter(cont => cont.name.toLowerCase()
          .includes(this.inputFolder.toLowerCase()))
        .limit(1000)
        .toArray();
      this.filteredItems = result;
    },
    setFile: function (item, path) {
      let entry = undefined;
      if (item.isFile) {
        item.file(file => {
          file.relativePath = path + file.name;
          this.$store.commit("appendDropFiles", file);
        });
      } else if (item instanceof File) {
        this.$store.commit("appendDropFiles", item);
      } else if (item.isDirectory) {
        entry = item;
      }
      if ("function" === typeof item.webkitGetAsEntry) {
        entry = item.webkitGetAsEntry();
      }
      // Recursively process items inside a directory
      if (entry && entry.isDirectory) {
        let newPath = path + entry.name + "/";
        let dirReader = entry.createReader();
        let allEntries = [];

        let readEntries = () => {
          dirReader.readEntries(entries => {
            if (entries.length) {
              allEntries = allEntries.concat(entries);
              return readEntries();
            }
            for (let item of allEntries) {
              this.setFile(item, newPath);
            }
          });
        };

        readEntries();
      } else if ("function" === typeof item.getAsFile) {
        item = item.getAsFile();
        if (item instanceof File) {
          item.relativePath = path + item.name;
          this.$store.commit("appendDropFiles", item);
        }
      }
    },
    setFiles: function () {
      if (this.transfer) {
        for (let file of this.transfer) {
          let entry = file;
          this.setFile(entry, "");
        }
      }
    },
    aBeginUpload: async function (files) {
      // Upload files to the active folder
      let uploadInfo = await getUploadEndpoint(
        this.active.id,
        this.$route.params.owner ? this.$route.params.owner : this.active.id,
        this.inputFolder,
      );
      this.$store.commit("setUploadInfo", uploadInfo);
      this.res.addFiles(files, undefined);
    },
    checkUploadSize() {
      let size = 0;
      for (let file of this.dropFiles) {
        size += file.size;
      }
      this.tooLarge = size > 1073741824;
    },
    // Make human readable translation functions available in instance
    // namespace
    localHumanReadableSize: function (size) {
      return getHumanReadableSize(size);
    },
    clearFiles() {
      this.$store.commit("eraseDropFiles");
    },
    cancelUpload() {
      this.$store.commit("eraseDropFiles");
      this.$store.commit("toggleUploadModal", false);
      this.inputFolder = "";
      modifyBrowserPageStyles();
    },
    dragHandler: function (e) {
      e.preventDefault();
      let dt = e.dataTransfer;
      if (dt.types.indexOf("Files") >= 0) {
        const el = document.querySelector(".dropArea");
        el.classList.add("over-dropArea");
        e.stopPropagation();
        dt.dropEffect = "copy";
        dt.effectAllowed = "copy";
      } else {
        dt.dropEffect = "none";
        dt.effectAllowed = "none";
      }
    },
    dragLeaveHandler: function () {
      const el = document.querySelector(".dropArea");
      el.classList.remove("over-dropArea");
    },
    navUpload: function (e) {
      e.stopPropagation();
      e.preventDefault();
      if (e.dataTransfer && e.dataTransfer.items) {
        for (let item of e.dataTransfer.items) {
          this.$store.commit("appendFileTransfer", item);
        }
      } else if (e.dataTransfer && e.dataTransfer.files) {
        for (let file of e.dataTransfer.files) {
          this.$store.commit("appendFileTransfer", file);
        }
      }
      const el = document.querySelector(".dropArea");
      el.classList.remove("over-dropArea");
    },
    appendPublicKey: async function () {
      if (!this.recvkeys.includes(this.addRecvkey)){
        this.recvkeys.push(this.addRecvkey);
        this.recvHashedKeys
          .push({key: {value: await computeSHA256(this.addRecvkey)}});
      }
      this.addRecvkey = "";
    },
    refreshNoUpload() {
      if (this.ephemeral) {
        this.noUpload = (
          (!this.pubkey.length && !this.recvkeys.length)
          || !this.inputFolder
          || !this.dropFiles.length
        );
      }
      if (this.ownPrivateKey) {
        this.noUpload = (
          (!this.pubkey.length && !this.recvkeys.length)
          || !this.inputFolder
          || !this.dropFiles.length
          || (!this.passphrase && !this.privkey)
        );
      }
    },
    encryptFiles: async function () {
      let res = 0;
      // Add keys to the filesystem
      FS.mkdir("/keys"); // eslint-disable-line
      FS.mkdir("/keys/recv_keys"); // eslint-disable-line
      // Only add private key if we're not using ephemeral key upload
      if (!this.ephemeral) {
        FS.writeFile("/keys/pk.key", this.privkey); // eslint-disable-line
      }
      // we add the fixed set of keys to the ones the user added
      let keysArray = this.recvkeys.concat(this.pubkey);
      keysArray = [...new Set([...this.recvkeys, ...this.pubkey])];
      for (let i = 0; i < keysArray.length; i++) {
        FS.writeFile( // eslint-disable-line
          "/keys/recv_keys/pubkey_" + i.toString(),
          keysArray[i],
        );
      }
      // Add files to the filesystem
      FS.mkdir("/data"); // eslint-disable-line
      for (let f of this.dropFiles) {
        let buf = new Uint8Array(await f.arrayBuffer());
        handleDirectories: {
          if (f.relativePath) {
            if (f.relativePath.split("/").length <= 1) {
              break handleDirectories;
            }
            // Ensure the directories are available for the path
            let dirs = f.relativePath.split("/");
            dirs.pop(); // ditch the file name
            let createDirs = (dirs, path) => {
              let npath = path + "/" + dirs[0];
              try {
                FS.mkdir(npath); // eslint-disable-line
              } catch(err) {} // eslint-disable-line
              if (dirs.slice(1).length > 0) {
                createDirs(dirs.slice(1), npath);
              }
            };
            createDirs(dirs, "/data");
          }
        }
        let outname = "/data/" + (f.relativePath ? f.relativePath : f.name);
        try {
          FS.writeFile(outname, buf); // eslint-disable-line
        } catch (err) {
          res = 255; // Indicate FS space exhaustion with error 255
        }
      }

      if (res != 0 ) {
        this.$buefy.toast.open({
          message: this.$t("message.encrypt.fsWriteFail"),
          duration: 15000,
          type: "is-danger",
        });
        throw "Failed to write files into FS.";
      }

      res = 0;
      if(!this.ephemeral) {
        res = Module.ccall( // eslint-disable-line
          "encrypt_folder",
          "number",
          ["string"],
          [this.passphrase],
        );
      } else {
        res = Module.ccall( // eslint-disable-line
          "encrypt_folder_ephemeral",
          "number",
          [],
          [],
        );
      }
      if (res != 0) {

        this.$buefy.toast.open({
          message: this.$t("message.encrypt.enFail"),
          duration: 15000,
          type: "is-danger",
        });
        throw "Failed to encrypt files.";
      }
    },
    encryptAndUpload: function () {
      this.$buefy.toast.open({
        message: this.$t("message.encrypt.enStart"),
        duration: 10000,
        type: "is-success",
      });
      this.$store.commit("toggleUploadModal", false);
      modifyBrowserPageStyles();
      this.encryptFiles().then(() => {
        this.$buefy.toast.open({
          message: this.$t("message.encrypt.enSuccess"),
          duration: 10000,
          type: "is-success",
        });
        this.$store.commit("setAltContainer", this.inputFolder);
        let files = [];
        for (let f of this.dropFiles) {
          let path = f.relativePath ? f.relativePath : f.name;
          let outname = (
            "/data/"
            + path
            + ".c4gh");
          let newFile = new Blob(
            [FS.readFile(outname).buffer], // eslint-disable-line
            {
              type: "binary/octet-stream",
            },
          );
          newFile.relativePath = path + ".c4gh";
          newFile.name = f.name + ".c4gh";
          files.push(newFile);
        }
        this.aBeginUpload(files).then(() => {
          this.$buefy.toast.open({
            message: this.$t("message.encrypt.upStart"),
            type: "is-success",
          });
          this.clearFiles();
        });
      });
    },
  },
};
</script>

<style lang="scss" scoped>
@import "@/css/prod.scss";

.upload-card {
  padding: 3rem;
  position: absolute;
  top: -5rem;
  left: 0;
  right: 0;
  max-height: 80vh;
}

@media screen and (max-width: 992px) {
  .upload-card {
    max-height: 50vh;
  }
}

c-card-content {
  padding: 1.5rem 0 0 0;
  color: var(--csc-dark-grey);
}

c-autocomplete {
  width: 70%;
}

.taginput {
  width: 60%;
}

.title.is-6 {
  margin: 0 !important;
}

p.info-text.is-size-6 {
  margin-bottom: -1rem;
}

.dropArea {
  border: 1px dashed $csc-light-grey;
  padding: 2rem 0;
  & > span:first-of-type {
    margin-right: 1rem;
  }
}

.over-dropArea {
  border: 2px dashed var(--csc-primary);
}

c-data-table.files-table {
  margin-top: -24px;
}

c-card-actions {
  padding: 1rem 0 0 0;
  border-top: 1px solid var(--csc-primary);
}

c-container {
  margin-top: 1rem;
}

c-flex {
  margin-top: 1rem;
}

c-data-table.publickey-table {
  margin-top: 1rem;
}


</style>