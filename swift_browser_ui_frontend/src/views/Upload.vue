<template>
  <div
    id="uploadform"
    class="contents"
  > 
    <b-message
      v-if="$te('message.keys') && fixedRecvKeys.length > 0"
      type="is-info"
    >
      {{ $t('message.encrypt.defaultKeysMessage') }}
    </b-message>
    <b-message
      v-if="tooLarge"
      type="is-danger"
    >
      {{ $t('message.encrypt.enTooLarge') }}
    </b-message>
    <b-field
      grouped
      group-multiline
    >
      <div
        id="destinationBucket"
        class="control"
      >
        <b-field
          horizontal
          :label="$t('message.encrypt.container')"
          :message="$t('message.encrypt.container_hint')"
        >
          <b-input
            v-model="container"
            :placeholder="$t('message.encrypt.container_msg')"
          />
        </b-field>
      </div>
      <div
        id="encryptionOptions"
        class="control is-flex"
      >
        <b-switch
          v-model="useEncryption"
        >
          {{ $t('message.encrypt.enFiles') }}
        </b-switch>
        <b-switch
          v-model="ownPrivateKey"
        >
          {{ $t('message.encrypt.ephemeral') }}
        </b-switch>
        <b-switch
          v-model="multipleReceivers"
        >
          {{ $t('message.encrypt.multipleReceivers') }}
        </b-switch>
      </div>
    </b-field>
    <hr
      v-if="ownPrivateKey && useEncryption"
      class="is-medium"
    >
    <b-field
      v-if="ownPrivateKey && useEncryption"
      grouped
      group-multiline
    >
      <b-field
        expanded
        :label="$t('message.encrypt.pk')"
      >
        <b-input
          v-model="privkey"
          :placeholder="$t('message.encrypt.pk_msg')"
          type="textarea"
          maxlength="1024"
        />
      </b-field>
      <b-field
        expanded
        :label="$t('message.encrypt.phrase')"
      >
        <b-input
          v-model="passphrase"
          :placeholder="$t('message.encrypt.phrase_msg')"
          type="password"
        />
      </b-field>
    </b-field>
    <hr
      v-if="useEncryption && multipleReceivers"
      class="is-medium"
    >
    <div
      v-if="useEncryption && multipleReceivers"
      class="columns"
    >
      <div class="column">
        <b-field
          :label="$t('message.encrypt.pubkey')"
        >
          <b-input
            v-model="addRecvkey"
            :placeholder="$t('message.encrypt.pubkey_msg')"
            type="textarea"
            maxlength="1024"
          />
        </b-field>
        <b-field v-if="useEncryption">
          <b-button
            type="is-success"
            icon-left="lock-plus"
            @click="appendPublicKey"
          >
            {{ $t("message.encrypt.addkey") }}
          </b-button>
        </b-field>
      </div>
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
            <b-table-column
              v-slot="props"
              field="delete"
              width="75"
            >
              <b-button
                type="is-danger"
                icon-left="delete"
                outlined
                size="is-small"
                @click.prevent="removePublicKey(props.row)"
              >
                {{ $t('message.remove') }}
              </b-button>
            </b-table-column>
            <template #empty>
              <div class="has-text-centered">
                {{ $t('message.encrypt.noRecipients') }}
              </div>
            </template>
          </b-table>
        </b-field>
      </div>
    </div>
    <hr class="is-medium">
    <b-table
      :data="files"
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
        {{ props.row.relativePath | truncate(100) }}
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
      <b-table-column
        v-slot="props"
        field="remove"
        width="75"
      >
        <b-button
          type="is-danger"
          icon-left="delete"
          outlined
          size="is-small"
          @click="files.splice(
            files.findIndex(i => {
              if (i.relativePath) {
                return i.relativePath === props.row.relativePath;
              } else {
                return i.name === props.row.name;
              }
            }), 1
          )"
        >
          {{ $t('message.remove') }}
        </b-button>
      </b-table-column>
      <template #empty>
        <div class="has-text-centered">
          {{ $t('message.encrypt.empty') }}
        </div>
      </template>
    </b-table>
    <div class="uploadButtonContainer">
      <b-upload
        v-model="files"
        multiple
        class="file is-primary"
      >
        <span class="file-cta">
          <b-icon
            class="file-icon"
            icon="upload-multiple"
          />
          <span class="file-label">
            {{ $t('message.encrypt.dropMsg') }}
          </span>
        </span>
      </b-upload>
      <b-button
        v-if="useEncryption"
        id="uploadButton"
        type="is-success"
        :disabled="noUpload"
        icon-left="upload-lock"
        @click="encryptAndUpload"
      >
        {{ $t('message.encrypt.enup') }}
      </b-button>
      <b-button
        v-else
        id="uploadButton"
        type="is-success"
        icon-left="upload-lock"
        @click="beginUpload"
      >
        {{ $t('message.encrypt.normup') }}
      </b-button>
    </div>
  </div>
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
      fixedRecvKeys:[],
      container: "",
      passphrase: "",
      files: [],
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
    active () {
      return this.$store.state.active;
    },
    transfer () {
      return this.$store.state.transfer;
    },
  },
  watch: {
    container: function () {
      // the container is unique so we only need to check that
      if (this.$route.params.container != this.container) {
        this.$router.replace({
          name: "UploadView",
          params: {
            "project": this.$route.params.project,
            "container": this.container,
          },
        });
        this.$route.params.container = this.container;
        this.refreshNoUpload();
      }
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
    files: function () {
      this.refreshNoUpload();
      this.checkUploadSize();
    },
    ephemeral: function () {
      this.refreshNoUpload();
    },
  },
  created () {
    this.setContainer();
  },
  mounted() {
    this.setFiles();
    this.getPubKey();
  },
  methods: {
    getPubKey: function () {
      if (this.$te("message.keys")) {
        for (let item of Object.entries(this.$t("message.keys"))) {
          fetch(
            "/download/"
              + item[1]["project"] + "/"
              + item[1]["container"] + "/"
              + item[1]["object"],
          ).then(resp => {
            return resp.text();
          }).then(resp => {
            this.fixedRecvKeys.push(resp);
          });
        }
      }
    },
    setFile: function (item, path) {
      let entry = undefined;
      if (item.isFile) {
        item.file(file => {
          file.relativePath = path + file.name;
          this.files.push(file);
        });
      } else if (item instanceof File) {
        this.files.push(item);
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
          dirReader.readEntries((entries) => {
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
      }
      else if ("function" === typeof item.getAsFile) {
        item = item.getAsFile();
        if (item instanceof File) {
          this.files.push(item);
        }
      }
    },
    setFiles: function () {
      if (this.transfer) {
        for (let file of this.transfer) {
          let entry = file;
          this.setFile(entry, "");
          this.transfer.splice(file, 1);
        }
      }
    },
    setContainer: function () {
      if(this.$route.params.container) {
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
      let keysArray = this.recvkeys.concat(this.fixedRecvKeys);
      keysArray = [...new Set([...this.recvkeys, ...this.fixedRecvKeys])];
      for (let i = 0; i < keysArray.length; i++) {
        FS.writeFile( // eslint-disable-line
          "/keys/recv_keys/pubkey_" + i.toString(),
          keysArray[i],
        );
      }
      // Add files to the filesystem
      FS.mkdir("/data"); // eslint-disable-line
      for (let f of this.files) {
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
    aBeginUpload: async function (files) {
      // Upload files to the active container
      let uploadInfo = await getUploadEndpoint(
        this.$route.params.owner ? this.$route.params.owner : this.active.id,
        this.$route.params.container,
      );
      this.$store.commit("setUploadInfo", uploadInfo);
      this.res.addFiles(files, undefined);
    },
    beginUpload: function () {
      this.aBeginUpload(this.files).then(() => {
        this.$buefy.toast.open({
          message: this.$t("message.encrypt.upStart"),
          type: "is-success",
        });
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
        for (let f of this.files) {
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
        });
      });
    },
    appendPublicKey: async function () {
      if (!this.recvkeys.includes(this.addRecvkey)){
        this.recvkeys.push(this.addRecvkey);
        this.recvHashedKeys.push(await computeSHA256(this.addRecvkey));
      }
      this.addRecvkey = "";
    },
    removePublicKey: function (value){
      this.recvHashedKeys.splice(this.recvkeys.indexOf(value), 1);
      this.recvkeys.splice(this.recvkeys.indexOf(value), 1);
    },
    refreshNoUpload() {
      if (this.ephemeral) {
        this.noUpload = (
          (!this.fixedRecvKeys.length && !this.recvkeys.length)
          || !this.container
          || !this.files.length
        );
      } 
      if (this.ownPrivateKey) {
        this.noUpload = (
          (!this.fixedRecvKeys.length && !this.recvkeys.length)
          || !this.container
          || !this.files.length
          || (!this.passphrase && !this.privkey)
        );
      }
    },
    checkUploadSize() {
      let size = 0;
      for (let file of this.files) {
        size += file.size;
      }
      this.tooLarge = size > 1073741824;
    },
    // Make human readable translation functions available in instance
    // namespace
    localHumanReadableSize: function ( size ) {
      return getHumanReadableSize( size );
    },
  },
};
</script>

<style scoped>
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

#uploadButton {
  margin-left: auto;
}

#encryptionOptions {
  flex-grow: 1;
  margin-top: -20px;
  justify-content: right;
}

@media screen and ( max-width: 1357px){
  #encryptionOptions {
    margin-top: 0;
  }
  
}

</style>