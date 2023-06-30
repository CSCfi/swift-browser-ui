<template>
  <c-card class="upload-card">
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
          aria-required="true"
          required
          :valid="isValidFolderName(inputFolder) || !interacted"
          :validation="$t('message.error.tooShort')"
          validate-on-blur
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
            @add-files="buttonAddingFiles=true"
            @cancel="buttonAddingFiles=false"
          >
            <span>
              {{ $t("message.encrypt.dropMsg") }}
            </span>
          </CUploadButton>
        </div>
        <c-alert
          v-show="duplicateFile"
          type="error"
        >
          <div class="duplicate-notification">
            {{ $t("message.upload.duplicate") }}
            <c-button
              text
              size="small"
              @click="duplicateFile = false"
            >
              <i
                slot="icon"
                class="mdi mdi-close"
              />
              {{ $t("message.close") }}
            </c-button>
          </div>
        </c-alert>
        <!-- Footer options needs to be in CamelCase,
        because csc-ui wont recognise it otherwise. -->
        <!-- eslint-disable-->
        <c-data-table
          v-if="dropFiles.length > 0"
          class="files-table"
          :data.prop="dropFiles"
          :headers.prop="fileHeaders"
          :no-data-text="$t('message.encrypt.empty')"
          :pagination.prop="filesPagination"
          :footerOptions.prop="footer"
        />
        <!-- eslint-enable-->
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
                v-model="multipleReceivers"
                v-csc-control
                :label="$t('message.encrypt.multipleReceivers')"
              />
              <c-flex v-if="multipleReceivers">
                <c-text-field
                  v-model="addRecvkey"
                  v-csc-control
                  :label="$t('message.encrypt.pubkey')"
                  type="text"
                  rows="2"
                  :valid="validatePubkey(addRecvkey) || addRecvkey.length === 0"
                  :validation="$t('message.encrypt.pubkeyError')"
                />
                <c-button
                  :disabled="!validatePubkey(addRecvkey)"
                  @click="appendPublicKey"
                  @keyup.enter="appendPublicKey"
                >
                  {{ $t("message.encrypt.addkey") }}
                </c-button>
                <!-- Footer options needs to be in CamelCase,
                because csc-ui wont recognise it otherwise. -->
                <!-- eslint-disable-->
                <c-data-table
                  class="publickey-table"
                  :data.prop="recvHashedKeys"
                  :headers.prop="publickeyHeaders"
                  :no-data-text="$t('message.encrypt.noRecipients')"
                  :pagination.prop="keyPagination"
                  :footerOptions.prop="footer"
                />
                <!-- eslint-enable-->
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
        :disabled="noUpload
          || addingFiles
          || buttonAddingFiles
          || !isValidFolderName(inputFolder)"
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
  getSharedContainers,
  getAccessDetails,
  isValidFolderName,
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
      multipleReceivers: false,
      addRecvkey: "",
      recvkeys: [],
      recvHashedKeys: [],
      noUpload: true,
      CUploadButton,
      projectInfoLink: "",
      toastVisible: false,
      duplicateFile: false,
      addingFiles: false,
      buttonAddingFiles: false,
      noUploadContainers: [],
      interacted: false,
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
    modalVisible() {
      return this.$store.state.openUploadModal;
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
            this.appendDropFiles(file);
          }
        });
        this.buttonAddingFiles = false;
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
    addFiles() {
      return this.$store.state.addUploadFiles;
    },
    canUpload () {
      //used to disable upload button
      //in case disallowed folder name is typed in
      if (this.noUploadContainers.find(
        item => item.container === this.inputFolder) === undefined) {
        return true;
      }
      return false;
    },
  },
  watch: {
    modalVisible: function() {
      if (this.modalVisible) {
        //inputFolder not cleared when modal toggled,
        //in case there's a delay in upload start
        //reset when modal visible
        this.recvkeys = [];
        if(!this.noUploadContainers.length) {
          this.getNoUploadContainers();
        } else this.setInputFolder();
      }
    },
    inputFolder: function() {
      this.refreshNoUpload();
    },
    dropFiles: function () {
      this.refreshNoUpload();
    },
    recvkeys: function () {
      this.refreshNoUpload();
    },
    currentUpload: function () {
      this.refreshNoUpload();
    },
    active: function () {
      this.projectInfoLink = this.$t("message.dashboard.projectInfoBaseLink")
        + getProjectNumber(this.active);
    },
    addingFiles() {
      //see if drag&drop adding of files is done:
      if (this.addingFiles) {
        let fileCount = this.dropFiles.length;
        let check = setInterval(() => {
          if (this.dropFiles.length === fileCount) {
            //the amount of dropFiles didn't change
            //in the interval
            this.addingFiles = false;
            clearInterval(check);
          } else {
            fileCount = this.dropFiles.length;
          }
        }, 200);
      }
    },
  },
  methods: {
    isValidFolderName,
    appendDropFiles(file) {
      //Checking for identical path only, not name:
      //different folders may have same file names
      if (
        this.$store.state.dropFiles.find(
          ({ relativePath }) => relativePath === String(file.relativePath),
        ) === undefined
      ) {
        this.$store.commit("appendDropFiles", file);
      } else {
        if (!this.duplicateFile) {
          this.duplicateFile = true;
          setTimeout(() => { this.duplicateFile = false; }, 6000);
        }
      }
    },
    getNoUploadContainers: async function () {
      const sharedContainers = await getSharedContainers(this.active.id);
      if (sharedContainers != []) {
        for (const item of sharedContainers) {
          const share = await getAccessDetails(
            this.active.id,
            item.container,
            item.owner,
          );
          if (share.access.length < 2) {
            this.noUploadContainers.push(item);
          }
        }
      }
      this.setInputFolder();
    },
    setInputFolder() {
      if (this.currentFolder) {
        //only show current container as upload destination
        //if user has the right to upload to it
        if (this.noUploadContainers
          .find(item => item.container === this.currentFolder)
          === undefined) {
          this.inputFolder = this.currentFolder;
          return;
        }
      }
      this.inputFolder = "";
    },
    onSelectValue: function (e) {
      if (e.detail) this.inputFolder = e.detail.name;
    },
    onQueryChange: async function (event) {
      this.interacted = true; //user typed
      this.inputFolder = event.detail;
      //filter out containers where user has no upload right
      const result = await this.containers
        .filter(cont => cont.projectID === this.active.id)
        .filter(cont => {
          return !this.noUploadContainers
            .some(c => c.container === cont.container);
        })
        .filter(cont => cont.name.toLowerCase()
          .includes(event.detail.toLowerCase()))
        .filter(cont => !cont.name.endsWith("_segments"))
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
            this.appendDropFiles(file);
          } else return;
        });
      } else if (item instanceof File) {
        this.appendDropFiles(item);
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
          this.appendDropFiles(item);
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
    // Make human readable translation functions available in instance
    // namespace
    localHumanReadableSize: function (size) {
      return getHumanReadableSize(size);
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
      this.addingFiles = true;
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
    validatePubkey(key) {
      const sshed25519 = new RegExp (
        "^ssh-ed25519 AAAAC3NzaC1lZDI1NTE5" +
          "[0-9A-Za-z+/]{46,48}[=]{0,2}\\s[^\\s]+$");
      const crypt4gh = new RegExp (
        "^-----BEGIN CRYPT4GH PUBLIC KEY-----\\s[A-Za-z0-9+/]{42,44}[=]{0,2}" +
          "\\s-----END CRYPT4GH PUBLIC KEY-----$");
      return (key.match(sshed25519) || key.match(crypt4gh));
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
      this.noUpload = (
        (!this.pubkey.length && !this.recvkeys.length)
        || !this.inputFolder
        || !this.dropFiles.length
        || (this.currentUpload != undefined)
        || !this.canUpload
      );
    },
    cancelUpload() {
      this.$store.commit("setFilesAdded", false);
      this.$store.commit("eraseDropFiles");
      this.toggleUploadModal();
    },
    toggleUploadModal() {
      this.$store.commit("toggleUploadModal", false);
      this.addingFiles = false;
      this.tags = [];
      this.files = [];
      this.duplicateFile = false;
      this.interacted = false;
      this.addRecvkey = "";
      this.multipleReceivers = false;
      this.recvHashedKeys = [];
    },
    beginEncryptedUpload() {
      if (this.pubkey.length > 0) {
        this.recvkeys = this.recvkeys.concat(this.pubkey);
      }
      // Clean up old stale upload if exists
      this.$store.commit("abortCurrentUpload");
      this.$store.commit("eraseCurrentUpload");

      this.$store.commit("setFolderName", this.inputFolder);

      // Create a fresh session from scratch
      this.$store.commit("createCurrentUploadAbort");
      let upload = new EncryptedUploadSession(
        this.active,
        this.$route.params.owner ? this.$route.params.owner : this.active.id,
        this.$store.state.dropFiles,
        this.recvkeys,
        null,
        this.inputFolder,
        this.$route.query.prefix,
        null,
        true,
        this.$store,
        this.$el,
      );
      upload.initServiceWorker();
      this.$store.commit("setCurrentUpload", upload);
      upload.cleanUp();
      delay(() => {
        if (this.$store.state.encryptedFile == "" && this.dropFiles.length) {
          if (!this.toastVisible) {
            this.toastVisible = true;
            document.querySelector("#container-error-toasts").addToast(
              {
                type: "success",
                duration: 4000,
                progress: false,
                message: this.$t("message.upload.isStarting"),
              },
            );
            //avoid overlapping toasts
            setTimeout(() => { this.toastVisible = false; }, 4000);
          }
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
  max-height: 75vh;
}

@media screen and (max-width: 766px), (max-height: 580px) {
   .upload-card {
    top: -5rem;
  }
}

@media screen and (max-height: 580px) and (max-width: 766px),
(max-width: 525px) {
  .upload-card {
    top: -9rem;
  }
}

@media screen and (max-height: 580px) and (max-width: 525px) {
  .upload-card {
    top: -13rem;
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

.duplicate-notification {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

c-accordion c-button {
  margin-top: 0.5rem;
}

</style>
