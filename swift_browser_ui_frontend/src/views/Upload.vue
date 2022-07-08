<template>
  <c-card class="upload-card">
    <div id="uploadform" class="contents">
      <h3 class="title is-3">
        {{ $t("message.encrypt.uploadFiles") }}
      </h3>
      <c-card-content>
        <h6 class="title is-6">1. {{ $t("message.encrypt.upload_step1") }}</h6>
        <p class="info-text is-size-6">
          {{ $t("message.container_ops.norename") }}
        </p>
        <b-message
          v-if="$te('message.keys') && pubkey.length > 0"
          type="is-info"
        >
          {{ $t("message.encrypt.defaultKeysMessage") }}
        </b-message>
        <b-message v-if="tooLarge && useEncryption" type="is-danger">
          {{ $t("message.encrypt.enTooLarge") }}
        </b-message>
        <c-text-field
          :label="$t('message.container_ops.folderName')"
          name="foldername"
          type="text"
          required
          v-csc-model="folderName"
        />
        <b-field custom-class="has-text-dark" :label="$t('message.tagName')">
          <b-taginput
            v-model="tags"
            ellipsis
            maxlength="20"
            has-counter
            rounded
            type="is-primary"
            :placeholder="$t('message.tagPlaceholder')"
            :confirm-keys="taginputConfirmKeys"
            :on-paste-separators="taginputConfirmKeys"
          />
        </b-field>
        <b-field grouped group-multiline>
          <div id="encryptionOptions" class="control is-flex">
            <b-switch v-model="useEncryption">
              {{ $t("message.encrypt.enFiles") }}
            </b-switch>
          </div>
        </b-field>
        <h6 class="title is-6">2. {{ $t("message.encrypt.upload_step2") }}</h6>

        <div v-if="useEncryption && multipleReceivers" class="columns">
          <div class="column">
            <b-field>
              <b-table
                v-if="useEncryption"
                :data="recvHashedKeys"
                paginated
                focusable
                hoverable
                narrowed
                default-sort="key"
                per-page="5"
                pagination-simple
              >
                <b-table-column
                  v-slot="props"
                  sortable
                  field="key"
                  :label="$t('message.encrypt.pubkeyLabel')"
                >
                  {{ props.row }}
                </b-table-column>
                <b-table-column v-slot="props" field="delete" width="75">
                  <b-button
                    type="is-danger"
                    icon-left="delete"
                    outlined
                    size="is-small"
                    @click.prevent="removePublicKey(props.row)"
                  >
                    {{ $t("message.remove") }}
                  </b-button>
                </b-table-column>
                <template #empty>
                  <div class="has-text-centered">
                    {{ $t("message.encrypt.noRecipients") }}
                  </div>
                </template>
              </b-table>
            </b-field>
          </div>
        </div>
        {{ dropFiles }}
        <b-table
          :data="dropFiles"
          paginated
          focusable
          hoverable
          narrowed
          default-sort="name"
          per-page="20"
          pagination-simple
        >
          <b-table-column
            v-slot="props"
            sortable
            field="name"
            :label="$t('message.encrypt.table.name')"
          >
            {{ props.row.name | truncate(100) }}
          </b-table-column>
          <b-table-column
            v-slot="props"
            sortable
            field="path"
            :label="$t('message.encrypt.table.path')"
          >
            {{
              (!props.row.relativePath
                ? props.row.name
                : props.row.relativePath) | truncate(100)
            }}
          </b-table-column>
          <b-table-column
            v-slot="props"
            sortable
            field="size"
            width="100"
            :label="$t('message.encrypt.table.size')"
          >
            {{ localHumanReadableSize(props.row.size) }}
          </b-table-column>
          <b-table-column
            v-slot="props"
            sortable
            field="type"
            :label="$t('message.encrypt.table.type')"
          >
            {{ props.row.type }}
          </b-table-column>
          <b-table-column v-slot="props" field="remove" width="75">
            <b-button
              type="is-danger"
              icon-left="delete"
              outlined
              size="is-small"
              @click="$store.commit('eraseDropFile', props.row)"
            >
              {{ $t("message.remove") }}
            </b-button>
          </b-table-column>
          <template #empty>
            <div class="has-text-centered">
              {{ $t("message.encrypt.empty") }}
            </div>
          </template>
        </b-table>
        <div class="uploadButtonContainer">
          <b-upload v-model="files" multiple accept class="file is-primary">
            <span class="file-cta">
              <b-icon class="file-icon" icon="upload-multiple" />
              <span class="file-label">
                {{ $t("message.encrypt.dropMsg") }}
              </span>
            </span>
          </b-upload>
        </div>
      </c-card-content>
      <c-card-actions justify="space-between">
        <c-button outlined size="large" @click="cancelUpload">
          {{ $t("message.encrypt.cancel") }}
        </c-button>
        <c-button size="large" :disabled="noUpload" @click="beginUpload">
          {{ $t("message.encrypt.normup") }}
        </c-button>
      </c-card-actions>
    </div>
  </c-card>
</template>

<script>
import { getUploadEndpoint } from "@/common/api";
import { getHumanReadableSize, truncate, computeSHA256 } from "@/common/conv";

export default {
  name: "UploadView",
  filters: {
    truncate,
  },
  data() {
    return {
      ownPrivateKey: false,
      ephemeral: true,
      multipleReceivers: false,
      useEncryption: true,
      privkey: "",
      recvkeys: [],
      recvHashedKeys: [],
      container: "",
      passphrase: "",
      tooLarge: false,
      noUpload: true,
      addRecvkey: "",
    };
  },
  computed: {
    res() {
      return this.$store.state.resumableClient;
    },
    isUploading() {
      return this.$store.state.isUploading;
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
    dropFiles() {
      return this.$store.state.dropFiles;
    },
    files: {
      get() {
        return this.$store.state.dropFiles.message;
      },
      set(value) {
        console.log("value :>> ", value);
        const files = Array.from(value);
        files.forEach(element => {
          this.$store.commit("appendDropFiles", element);
        });
      },
    },
  },
  watch: {
    container: function () {
      // the container is unique so we only need to check that
      if (this.$route.params.container != this.container) {
        this.$router.replace({
          name: "UploadView",
          params: {
            project: this.$route.params.project,
            container: this.container,
          },
        });
        this.$route.params.container = this.container;
        this.refreshNoUpload();
      }
    },
    ownPrivateKey: function () {
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
    dropFiles: function () {
      this.refreshNoUpload();
      this.checkUploadSize();
    },
    ephemeral: function () {
      this.refreshNoUpload();
    },
    useEncryption: function () {
      this.refreshNoUpload();
    },
  },
  created() {
    this.setContainer();
  },
  mounted() {
    this.setFiles();
  },
  methods: {
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
        this.$store.commit("eraseTransfer");
      }
    },
    setContainer: function () {
      if (this.$route.params.container) {
        this.container = this.$route.params.container;
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
        // eslint-disable-next-line
        FS.writeFile("/keys/recv_keys/pubkey_" + i.toString(), keysArray[i]);
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
              } catch (err) {} // eslint-disable-line
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

      if (res != 0) {
        this.$buefy.toast.open({
          message: this.$t("message.encrypt.fsWriteFail"),
          duration: 15000,
          type: "is-danger",
        });
        throw "Failed to write files into FS.";
      }

      res = 0;
      if (!this.ephemeral) {
        // eslint-disable-next-line
        res = Module.ccall(
          "encrypt_folder",
          "number",
          ["string"],
          [this.passphrase],
        );
      } else {
        // eslint-disable-next-line
        res = Module.ccall("encrypt_folder_ephemeral", "number", [], []);
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
    aBeginUpload: async function (files) {
      // Upload files to the active container
      let uploadInfo = await getUploadEndpoint(
        this.active.id,
        this.$route.params.owner ? this.$route.params.owner : this.active.id,
        this.$route.params.container,
      );
      this.$store.commit("setUploadInfo", uploadInfo);
      this.res.addFiles(files, undefined);
    },
    beginUpload: function () {
      this.aBeginUpload(this.dropFiles).then(() => {
        this.$buefy.toast.open({
          message: this.$t("message.encrypt.upStart"),
          type: "is-success",
        });
        this.$store.commit("eraseDropFiles");
        this.$store.commit("toggleUploadModal", false);
      });
    },
    encryptAndUpload: function () {
      this.$buefy.toast.open({
        message: this.$t("message.encrypt.enStart"),
        duration: 10000,
        type: "is-success",
      });
      this.encryptFiles().then(() => {
        this.$buefy.toast.open({
          message: this.$t("message.encrypt.enSuccess"),
          duration: 10000,
          type: "is-success",
        });
        this.$store.commit("setAltContainer", this.$route.params.container);
        let files = [];
        for (let f of this.dropFiles) {
          let path = f.relativePath ? f.relativePath : f.name;
          let outname = "/data/" + path + ".c4gh";
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
    appendPublicKey: async function () {
      if (!this.recvkeys.includes(this.addRecvkey)) {
        this.recvkeys.push(this.addRecvkey);
        this.recvHashedKeys.push(await computeSHA256(this.addRecvkey));
      }
      this.addRecvkey = "";
    },
    removePublicKey: function (value) {
      this.recvHashedKeys.splice(this.recvkeys.indexOf(value), 1);
      this.recvkeys.splice(this.recvkeys.indexOf(value), 1);
    },
    refreshNoUpload() {
      if (this.ephemeral) {
        this.noUpload =
          (!this.pubkey.length && !this.recvkeys.length) ||
          !this.container ||
          !this.dropFiles.length;
      }
      if (this.ownPrivateKey) {
        this.noUpload =
          (!this.pubkey.length && !this.recvkeys.length) ||
          !this.container ||
          !this.dropFiles.length ||
          (!this.passphrase && !this.privkey);
      }
      if (!this.useEncryption) {
        this.noUpload = this.dropFiles.length === 0;
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
    cancelUpload() {
      this.$store.commit("eraseDropFiles");
      this.$store.commit("toggleUploadModal", false);
    },
  },
};
</script>

<style lang="scss" scoped>
@import "@/css/prod.scss";

.upload-card {
  width: 64vw;
  padding: 3rem;
  left: 50%;
  transform: translate(-50%, -50%);
}

c-card-content {
  padding: 1.5rem;
  color: var(--csc-dark-grey);
}

#uploadform {
  width: 90%;
  margin: auto;
}

#destinationBucket {
  flex-grow: 1;
}

.uploadButtonContainer {
  margin-top: 2%;
  display: flex;
  flex-wrap: wrap;
}

.uploadButtonContainer .upload + button,
.uploadButtonContainer #uploadButton + button {
  margin-left: 1%;
}

#uploadButton {
  margin-left: auto;
}

#encryptionOptions {
  flex-grow: 1;
  margin-top: -20px;
  justify-content: right;
}

@media screen and (max-width: 1357px) {
  #encryptionOptions {
    margin-top: 0;
  }
}
</style>
