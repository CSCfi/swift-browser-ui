<template>
  <c-card class="upload-card">
    <c-toasts
      id="uploadModal-toasts"
      data-testid="uploadModal-toasts"
      absolute
    />
    <div
      id="upload-modal-content"
      class="modal-content-wrapper"
    >
      <h2 class="title is-4 has-text-dark">
        {{ $t("message.encrypt.uploadFiles") }}
      </h2>
      <c-card-content>
        <h3 class="title is-6 has-text-dark">
          1. {{ $t("message.encrypt.upload_step1") }}
        </h3>
        <p class="info-text is-size-6">
          {{ $t("message.container_ops.norename") }}
        </p>
        <c-autocomplete
          v-csc-control
          :items.prop="filteredItems"
          :label="$t('message.container_ops.folderName')"
          :query="inputFolder"
          hide-details
          required
          @changeQuery="onQueryChange"
          @changeValue="onSelectValue"
        />
        <h3 class="title is-6 has-text-dark">
          2. {{ $t("message.encrypt.upload_step2") }}
        </h3>
        <div
          class="dropArea is-flex
                is-align-items-center is-justify-content-center"
          @dragover="dragHandler"
          @dragleave="dragLeaveHandler"
          @drop="navUpload"
        >
          <span>{{ $t("message.dropFiles") }}</span>
          <CUploadButton
            v-model="files"
            v-csc-control
          >
            <span>
              {{ $t("message.encrypt.dropMsg") }}
            </span>
          </CUploadButton>
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
          <c-link
            :href="projectInfoLink"
            underline
            target="_blank"
          >
            {{ $t("message.container_ops.viewProjectMembers") }}
            <i class="mdi mdi-open-in-new" />
          </c-link>
        </p>
        <c-accordion value="advancedOptions">
          <c-accordion-item
            :heading="$t('message.encrypt.advancedOptions')"
            :value="$t('message.encrypt.advancedOptions')"
          >
            <c-container>
              <c-checkbox
                v-model="ownPrivateKey"
                v-csc-control
                :label="$t('message.encrypt.ephemeral')"
              />
              <c-flex v-if="ownPrivateKey">
                <c-text-field
                  v-model="privkey"
                  v-csc-control
                  :placeholder="$t('message.encrypt.pk_msg')"
                  :label="$t('message.encrypt.pk')"
                  type="text"
                  max="1024"
                />
                <c-text-field
                  v-model="passphrase"
                  v-csc-control
                  :placeholder="$t('message.encrypt.phrase_msg')"
                  :label="$t('message.encrypt.phrase')"
                  type="text"
                  max="1024"
                  rows="5"
                />
              </c-flex>
            </c-container>
            <c-container>
              <c-checkbox
                v-model="multipleReceivers"
                v-csc-control
                :label="$t('message.encrypt.multipleReceivers')"
              />
              <c-flex v-if="multipleReceivers">
                <c-text-field
                  v-model="addRecvkey"
                  v-csc-control
                  :placeholder="$t('message.encrypt.pubkey_msg')"
                  :label="$t('message.encrypt.pubkey')"
                  type="text"
                  max="1024"
                  rows="3"
                />
                <c-button
                  @click="appendPublicKey"
                  @keyup.enter="appendPublicKey"
                >
                  <i
                    slot="icon"
                    class="mdi mdi-lock-plus"
                  />
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
        @keyup.enter="cancelUpload"
      >
        {{ $t("message.encrypt.cancel") }}
      </c-button>
      <c-button
        size="large"
        :disabled="noUpload"
        @click="beginEncryptedUpload"
        @keyup.enter="beginEncryptedUpload"
      >
        {{ $t("message.encrypt.normup") }}
      </c-button>
    </c-card-actions>
  </c-card>
</template>

<script>
import EncryptedUploadSession from "@/common/upload";
import {
  getHumanReadableSize,
  truncate,
  computeSHA256,
} from "@/common/conv";
import { getDB } from "@/common/db";

import {
  getProjectNumber,
} from "@/common/globalFunctions";
import CUploadButton from "@/components/CUploadButton.vue";

import delay from "lodash/delay";

export default {
  name: "UploadModal",
  components: {
    CUploadButton,
  },
  filters: {
    truncate,
  },
  data() {
    return {
      inputFolder: "",
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
      CUploadButton,
      projectInfoLink: "",
    };
  },
  computed: {
    containers() {
      return getDB().containers;
    },
    res() {
      return this.$store.state.resumableClient;
    },
    active() {
      return this.$store.state.active;
    },
    pubkey() {
      return this.$store.state.pubkey;
    },
    currentUpload() {
      return this.$store.state.uploadState;
    },
    currentFolder() {
      return this.$route.params.container;
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
            value: file.relativePath || truncate(100),
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
        files.forEach(file => {
          if (this.addFiles) {
            file.relativePath = file.name;
            this.$store.commit("appendDropFiles", file);
          }
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
    addFiles() {
      return this.$store.state.addUploadFiles;
    },
  },
  watch: {
    currentFolder: function() {
      this.inputFolder = this.currentFolder;
    },
    inputFolder: function() {
      this.refreshNoUpload();
    },
    dropFiles: function () {
      this.checkUploadSize();
      this.refreshNoUpload();
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
    currentUpload: function () {
      this.refreshNoUpload();
    },
    active: function () {
      this.projectInfoLink = this.$t("message.dashboard.projectInfoBaseLink")
        + getProjectNumber(this.active);
    },
  },
  mounted() {
    if (this.currentFolder) this.inputFolder = this.currentFolder;
  },
  methods: {
    onSelectValue: function (e) {
      if (e.detail) this.inputFolder = e.detail.name;
    },
    onQueryChange: async function (event) {
      this.inputFolder = event.detail;
      const result = await this.containers
        .filter(cont => cont.projectID === this.active.id)
        .filter(cont => cont.name.toLowerCase()
          .includes(event.detail.toLowerCase()))
        .limit(1000)
        .toArray();
      this.filteredItems = result;
    },
    setFile: function (item, path) {
      let entry = undefined;
      if (item.isFile) {
        item.file(file => {
          if (this.addFiles) {
            file.relativePath = path + file.name;
            this.$store.commit("appendDropFiles", file);
          } else return;
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
            if (this.addFiles) {
              if (entries.length) {
                allEntries = allEntries.concat(entries);
                return readEntries();
              }
              for (let item of allEntries) {
                if (this.addFiles) {
                  this.setFile(item, newPath);
                }
              }
            } else return; //modal was closed
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
    setFiles: function (files) {
      if (files.length > 0) {
        for (let file of files) {
          let entry = file;
          this.setFile(entry, "");
        }
      }
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
        this.setFiles(e.dataTransfer.items);
      } else if (e.dataTransfer && e.dataTransfer.files) {
        this.setFiles(e.dataTransfer.files);
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
          || (this.currentUpload != undefined)
        );
      }
      if (this.ownPrivateKey) {
        this.noUpload = (
          (!this.pubkey.length && !this.recvkeys.length)
          || !this.inputFolder
          || !this.dropFiles.length
          || (!this.passphrase && !this.privkey)
          || (this.currentUpload != undefined)
        );
      }
    },
    cancelUpload() {
      this.$store.commit("setFilesAdded", false);
      this.toggleUploadModal();
    },
    toggleUploadModal() {
      this.clearFiles();
      this.tags = [];
      this.ephemeral = true;
      this.files = [];
      this.$store.commit("toggleUploadModal", false);
    },
    beginEncryptedUpload() {
      if (this.pubkey.length > 0) {
        this.recvkeys = this.recvkeys.concat(this.pubkey);
      }
      // Clean up old stale upload if exists
      this.$store.commit("abortCurrentUpload");
      this.$store.commit("eraseCurrentUpload");

      // Create a fresh session from scratch
      this.$store.commit("createCurrentUploadAbort");
      let upload = new EncryptedUploadSession(
        this.active,
        this.$route.params.owner ? this.$route.params.owner : this.active.id,
        this.$store.state.dropFiles,
        this.recvkeys,
        this.privkey,
        this.inputFolder,
        this.$route.query.prefix,
        this.passphrase,
        this.ephemeral,
        this.$store,
        this.$el,
      );
      document.querySelector("#uploadModal-toasts").addToast(
        {
          type: "success",
          progress: false,
          message: this.$t("message.upload.isStarting"),
        },
      );
      upload.initServiceWorker();
      this.$store.commit("setCurrentUpload", upload);
      upload.cleanUp();
      delay(() => {
        if (this.$store.state.encryptedFile == "" && this.dropFiles.length) {
          this.beginEncryptedUpload();
        }
      }, 1000);
      this.toggleUploadModal();
    },
  },
};
</script>

<style lang="scss" scoped>

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
  margin-top: -0.5rem;
  width: 70%;
}

.taginput {
  width: 60%;
}

.title.is-6 {
  margin: 0 !important;
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

c-data-table.publickey-table {
  margin-top: 1rem;
}

</style>
