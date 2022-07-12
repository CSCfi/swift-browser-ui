<template>
  <c-card class="upload-card">
    <div class="upload-form">
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
          v-csc-model="folderName"
          :placeholder="$t('message.container_ops.folderName')"
          name="foldername"
          type="text"
          required
        />
        <b-field
          custom-class="has-text-dark"
          :label="$t('message.tagName')"
          type="is-dark"
        >
          <b-taginput
            v-model="tags"
            class="taginput"
            ellipsis
            maxlength="20"
            has-counter
            rounded
            :placeholder="$t('message.tagPlaceholder')"
            :confirm-keys="taginputConfirmKeys"
            :on-paste-separators="taginputConfirmKeys"
          />
        </b-field>
        <h6 class="title is-6 has-text-dark">
          2. {{ $t("message.encrypt.upload_step2") }}
        </h6>
        <b-upload
          v-model="files"
          multiple
          accept
          drag-drop
          expanded
          class="file is-primary"
        >
          <div class="is-flex is-align-items-center is-justify-content-center">
            <span>{{ $t("message.dropFiles") }}</span>
            <span class="file-cta">
              {{ $t("message.encrypt.dropMsg") }}
            </span>
          </div>
        </b-upload>

        <c-data-table
          :data.prop="dropFiles"
          :headers.prop="headers"
          :no-data-text="$t('message.encrypt.empty')"
          :pagination.prop="paginationOptions"
          :footerOptions.prop="footerOptions"
        />
        <p class="info-text is-size-6">
          {{ $t("message.container_ops.createdFolder") }}
          <b>{{ $t("message.container_ops.myResearchProject") }}</b>
        </p>
        <c-link
          :href="`https://my.csc.fi/myProjects/project/${currentProjectID}`"
          underline
          target="_blank"
        >
          {{ $t("message.container_ops.viewProjectMembers") }}
          <i class="mdi mdi-open-in-new" />
        </c-link>
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
    headers() {
      return [
        {
          key: "name",
          value: this.$t("message.encrypt.table.name"),
          width: "30%",
        },
        {
          key: "type",
          value: this.$t("message.encrypt.table.type"),
          width: "15%",
        },
        {
          key: "size",
          value: this.$t("message.encrypt.table.size"),
          width: "10%",
        },
        {
          key: "path",
          value: this.$t("message.encrypt.table.path"),
          width: "30%",
        },
        {
          key: "remove",
          value: null,
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
                    this.$store.commit("eraseDropFile", data["id"]),
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
          path: {
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
    paginationOptions() {
      return {
        itemCount: this.dropFiles.length,
        itemsPerPage: 20,
        currentPage: 1,
      };
    },
    footerOptions() {
      return {
        hideDetails: true,
        sortable: false,
      };
    },
    currentProjectID() {
      return this.$route.params.project;
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
  margin-top: 50%;
  transform: translate(-50%, -50%);
  height: 85vh;
}

.upload-form {
  overflow-y: scroll;
}

c-card-content {
  padding: 1.5rem 0;
  color: var(--csc-dark-grey);
}

c-text-field {
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

.is-flex {
  padding: 2rem 0;
  & > span:first-of-type {
    margin-right: 1rem;
  }
}

span.file-cta {
  background-color: transparent !important;
  border: 2px solid var(--csc-primary) !important;
  color: var(--csc-primary) !important;
  font-weight: bold;
}

c-data-table {
  margin-top: -24px;
}

c-card-actions {
  padding: 0;
  margin-top: 1rem;
}
</style>
