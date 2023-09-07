<template>
  <c-card
    ref="uploadContainer"
    class="upload-card"
    @keydown="handleKeyDown"
  >
    <div
      id="upload-modal-content"
      class="modal-content-wrapper"
    >
      <c-toasts
        id="uploadModal-toasts"
        data-testid="uploadModal-toasts"
        vertical="bottom"
        absolute
      />
      <h2 class="title is-4">
        {{ $t("message.encrypt.uploadFiles") }}
      </h2>
      <c-card-content>
        <div
          v-if="!currentFolder"
          id="upload-to-root"
        >
          <h3 class="title is-6">
            1. {{ $t("message.encrypt.upload_step1") }}
          </h3>
          <p class="info-text is-size-6">
            {{ $t("message.container_ops.norename") }}
          </p>
          <c-text-field
            id="upload-folder-input"
            v-model="inputFolder"
            v-csc-control
            :label="$t('message.container_ops.folderName')"
            aria-required="true"
            required
            :valid="errorMsg.length === 0"
            :validation="errorMsg"
            @changeValue="interacted = true"
          />
          <h3 class="title is-6">
            2. {{ $t("message.encrypt.upload_step2") }}
          </h3>
        </div>
        <div v-else>
          <p>
            <b>{{ $t("message.encrypt.uploadDestination") }}</b>
            {{ currentFolder }}
          </p>
        </div>
        <div
          class="dropArea"
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
          v-show="duplicateDropFile"
          type="error"
        >
          <div class="duplicate-notification">
            {{ $t("message.upload.duplicate") }}
            <c-button
              text
              size="small"
              @click="duplicateDropFile = false"
            >
              <i
                slot="icon"
                class="mdi mdi-close"
              />
              {{ $t("message.close") }}
            </c-button>
          </div>
        </c-alert>
        <c-alert
          v-show="existingFiles.length"
          type="warning"
        >
          <span
            v-if="existingFiles.length === 1"
          >
            {{ $t("message.objects.file") }}
            <b>
              {{ existingFiles[0].name }}
            </b>
            {{ $t("message.objects.overwriteConfirm") }}
          </span>
          <span
            v-else
          >
            {{ $t("message.objects.files") }}
            <b>
              {{ existingFileNames }}
            </b>
            {{ $t("message.objects.overwriteConfirmMany") }}
          </span>
          <c-card-actions justify="end">
            <c-button
              outlined
              @click="overwriteFiles"
              @keyup.enter="overwriteFiles"
            >
              {{ $t("message.objects.overwrite") }}
            </c-button>
            <c-button
              @click="clearExistingFiles"
              @keyup.enter="clearExistingFiles"
            >
              {{ $t("message.cancel") }}
            </c-button>
          </c-card-actions>
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
          @click="checkPage($event,false)"
        />
        <!-- eslint-enable-->
        <p
          class="info-text is-size-6"
        >
          {{ $t("message.encrypt.uploadedFiles") }}
          <b>{{ active.name }}</b>{{ !owner ? "." : " (" }}
          <c-link
            :href="projectInfoLink"
            underline
            target="_blank"
          >
            {{ $t("message.container_ops.viewProjectMembers") }}
            <i class="mdi mdi-open-in-new" />
          </c-link>
          {{ !owner ? "" :
            ") " + $t("message.encrypt.uploadedToShared") }}
        </p>
        <c-accordion
          id="accordion"
          value="advancedOptions"
        >
          <c-accordion-item
            :heading="$t('message.encrypt.advancedOptions')"
            :value="$t('message.encrypt.advancedOptions')"
          >
            <c-container>
              <c-flex>
                <h3 class="title is-6">
                  {{ $t('message.encrypt.multipleReceivers') }}
                </h3>
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
                  @click="checkPage($event,true)"
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
        :loading="addingFiles || buttonAddingFiles"
        @click="onUploadClick"
        @keyup.enter="onUploadClick"
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
  validateFolderName,
  checkIfItemIsLastOnPage,
} from "@/common/globalFunctions";
import {
  getFocusableElements,
  moveFocusOutOfModal,
  keyboardNavigationInsideModal,
} from "@/common/keyboardNavigation";
import CUploadButton from "@/components/CUploadButton.vue";
import { swiftDeleteObjects, getObjects } from "@/common/api";

import { delay, debounce } from "lodash";
import { mdiDelete } from "@mdi/js";


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
      addRecvkey: "",
      recvkeys: [],
      recvHashedKeys: [],
      CUploadButton,
      projectInfoLink: "",
      toastVisible: false,
      duplicateDropFile: false,
      addingFiles: false,
      buttonAddingFiles: false,
      interacted: false,
      currentPage: 1,
      currentKeyPage:1,
      errorMsg: "",
      toastMsg : "",
      containers: [],
      objects: [],
      existingFiles: [],
      filesToOverwrite: [],
    };
  },
  computed: {
    res() {
      return this.$store.state.resumableClient;
    },
    active() {
      return this.$store.state.active;
    },
    pubkey() {
      return this.$store.state.pubkey;
    },
    currentFolder() {
      return this.$route.params.container;
    },
    modalVisible() {
      return this.$store.state.openUploadModal;
    },
    owner() {
      return this.$route.params.owner;
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
          key: "delete",
          value: null,
          sortable: false,
          children: [
            {
              value: this.$t("message.delete"),
              component: {
                tag: "c-button",
                params: {
                  text: true,
                  size: "small",
                  title: this.$t("message.delete"),
                  path: mdiDelete,
                  onClick: ({ data }) =>
                    this.$store.commit("eraseDropFile", data),
                  onKeyUp: (e) => {
                    if(e.keyCode === 13) {
                      // Get the row element of item that is to be removed
                      const row = e.target.closest("tr");
                      if (row !== undefined) {
                        const data = {
                          name: row.children[0]?.innerText,
                          relativePath: row.children[3]?.innerText,
                        };
                        this.$store.commit("eraseDropFile", data);
                      }
                    }
                  },
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
          key: "delete",
          value: null,
          sortable: false,
          children: [
            {
              value: this.$t("message.delete"),
              component: {
                tag: "c-button",
                params: {
                  text: true,
                  size: "small",
                  title: this.$t("message.delete"),
                  path: mdiDelete,
                  onClick: ({ index }) =>{
                    this.recvHashedKeys.splice(index, 1);
                    this.recvkeys.splice(index, 1);
                  },
                  onKeyUp: (e) => {
                    if(e.keyCode === 13) {
                      // Get the text value of item that is to be removed
                      const keyText = e.target.closest("tr")?.innerText;
                      // Find its index in key list
                      const index = this.recvHashedKeys.indexOf(keyText);
                      if (index !== undefined) {
                        this.recvHashedKeys.splice(index - 2, 1);
                        this.recvkeys.splice(index - 2, 1);
                      }
                    }
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
        currentPage: this.currentPage,
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
        currentPage: this.currentKeyPage,
      };
    },
    addFiles() {
      return this.$store.state.addUploadFiles;
    },
    prevActiveEl() {
      return this.$store.state.prevActiveEl;
    },
    existingFileNames() {
      return this.existingFiles.reduce((array, item) => {
        array.push(item.name);
        return array;
      }, []).join(", ");
    },
  },
  watch: {
    modalVisible: async function() {
      if (this.modalVisible) {
        //inputFolder not cleared when modal toggled,
        //in case there's a delay in upload start
        //reset when modal visible
        this.clearExistingFiles();
        this.filesToOverwrite = [];
        this.recvkeys = [];
        this.inputFolder = "";
        this.containers = await getDB().containers
          .where({ projectID: this.active.id })
          .toArray();
        if (this.currentFolder) {
          const cont = this.containers.find(c =>
            c.name === this.currentFolder);
          this.objects = await getDB().objects
            .where({containerID: cont.id})
            .toArray();
        }
      }
    },
    inputFolder: function() {
      if (this.inputFolder && this.interacted) {
        this.checkFolderName();
      }
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
    checkPage(event, isKey) {
      const page = checkIfItemIsLastOnPage(
        {
          currentPage: event.target.pagination.currentPage ,
          itemsPerPage: event.target.pagination.itemsPerPage,
          itemCount: event.target.pagination.itemCount,
        });
      if (isKey) {
        this.currentKeyPage = page;
      } else {
        this.currentPage = page;
      }
    },
    appendDropFiles(file, overwrite = false) {
      //Check if file path already exists in dropFiles
      if (
        this.$store.state.dropFiles.find(
          ({ relativePath }) => relativePath === String(file.relativePath),
        ) === undefined
      ) {
        if (this.objects && !overwrite) {
          //Check if file already exists in container objects
          const existingFile = this.objects.find(obj => obj.name === `${file.relativePath}.c4gh`);
          if (existingFile) {
            this.existingFiles.push(file);
            return;
          }
        }
        this.$store.commit("appendDropFiles", file);
      } else {
        if (!this.duplicateDropFile) {
          this.duplicateDropFile = true;
          setTimeout(() => { this.duplicateDropFile = false; }, 6000);
        }
      }
    },
    overwriteFiles() {
      //if new duplicate files appear after confirmation
      // alert will show again
      for (let i = 0; i < this.existingFiles.length; i++) {
        this.appendDropFiles(this.existingFiles[i], true);
        this.filesToOverwrite.push(this.existingFiles[i]);
      }
      this.clearExistingFiles();
    },
    async deleteSegments() {
      //old file segments need to be deleted because
      //they are not overwritten
      if (!this.filesToOverwrite.length) return;

      let oldSegments = [];
      const segmentCont= await getDB().containers.get({
        projectID: this.active.id,
        name: `${this.currentFolder}_segments`,
      });
      const segmentObjs =  await getObjects(
        this.owner ? this.owner : this.active.id,
        segmentCont.name,
      );

      if (segmentCont) {
        for (let i = 0; i < this.filesToOverwrite.length; i++) {
          const segment = segmentObjs.filter(obj =>
            obj.name.includes(`${this.filesToOverwrite[i].name}.c4gh/`))[0];
          if (segment) oldSegments.push(segment.name);
        }
      }

      if (oldSegments.length) {
        await swiftDeleteObjects(
          this.owner || this.active.id,
          segmentCont.name,
          oldSegments,
        );
      }
    },
    clearExistingFiles() {
      this.existingFiles = [];
      this.objects = [];
    },
    checkFolderName: debounce(function () {
      const error = validateFolderName(this.inputFolder, this.$t);
      if (error.length === 0) {
        if (this.containers) {
          let found = this.containers.find(
            cont => cont.name === this.inputFolder);
          if (found) {
            this.errorMsg = this.$t("message.error.inUse");
            return;
          }
        }
        this.errorMsg = "";
      }
      else this.errorMsg = error;
    }, 300),
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
    cancelUpload() {
      this.$store.commit("setFilesAdded", false);
      this.$store.commit("eraseDropFiles");
      this.toggleUploadModal();
    },
    resetAccordionVal() {
      let accordion = document.getElementById("accordion");
      accordion.value = "advancedOptions";
    },
    toggleUploadModal() {
      this.resetAccordionVal();
      document.querySelector("#uploadModal-toasts").removeToast("upload-toast");
      this.$store.commit("toggleUploadModal", false);
      this.addingFiles = false;
      this.tags = [];
      this.files = [];
      this.duplicateDropFile = false;
      this.interacted = false;
      this.addRecvkey = "";
      this.recvHashedKeys = [];
      this.errorMsg = "";
      this.toastMsg = "";

      moveFocusOutOfModal(this.prevActiveEl);
    },
    checkIfCanUpload() {
      if (this.dropFiles.length === 0) {
        return this.$t("message.upload.addFiles");
      }
      else if (!this.pubkey.length && !this.recvkeys.length) {
        return this.$t("message.upload.error");
      }
      else return "";
    },
    onUploadClick() {
      this.toastMsg = this.checkIfCanUpload();
      if (!this.currentFolder && !this.inputFolder) {
        //In case user does not interact with input field before click
        this.errorMsg = validateFolderName(this.inputFolder, this.$t);
      }
      if (this.errorMsg) {
        return;
      }
      else if (this.toastMsg) {
        document.querySelector("#uploadModal-toasts").addToast(
          {
            id: "upload-toast",
            type: "error",
            duration: 4000,
            progress: false,
            message: this.toastMsg,
          },
        );
        return;
      }
      else {
        if (this.filesToOverwrite.length > 0) this.deleteSegments();
        this.beginEncryptedUpload();
      }
    },
    beginEncryptedUpload() {
      if (this.pubkey.length > 0) {
        this.recvkeys = this.recvkeys.concat(this.pubkey);
      }
      // Clean up old stale upload if exists
      this.$store.commit("abortCurrentUpload");
      this.$store.commit("eraseCurrentUpload");

      this.currentFolder ?
        this.$store.commit("setFolderName", this.currentFolder) :
        this.$store.commit("setFolderName", this.inputFolder);

      // Create a fresh session from scratch
      this.$store.commit("createCurrentUploadAbort");
      let upload = new EncryptedUploadSession(
        this.active,
        this.owner ? this.owner : this.active.id,
        this.$store.state.dropFiles,
        this.recvkeys,
        null,
        this.currentFolder ? this.currentFolder : this.inputFolder,
        "",
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
    handleKeyDown: function (e) {
      const focusableList = this.$refs.uploadContainer.querySelectorAll(
        "c-link, c-button, textarea, c-text-field, c-data-table",
      );
      const { first, last } = getFocusableElements(focusableList);
      keyboardNavigationInsideModal(e, first, last, true);
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
  padding: 1rem 0 0 0;
  color: var(--csc-dark);
}

c-card-actions {
  padding: 0;
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
  display: flex;
  align-items: center;
  justify-content: center;
}

.over-dropArea {
  border: 2px dashed var(--csc-primary);
}

c-data-table.files-table {
  margin-top: -24px;
}

#upload-to-root p {
  padding: 1rem 0 1rem 0;
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
c-accordion h3 {
  padding: 1rem 0;
}

</style>
