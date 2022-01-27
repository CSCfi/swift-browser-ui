<template>
  <div
    id="uploadform"
    class="contents"
  >
    <b-message
      v-if="tooLarge"
      type="is-danger"
      has-icon
    >
      {{ $t('message.encrypt.enTooLarge') }}
    </b-message>
    <b-field :label="$t('message.encrypt.enFiles')">
      <b-switch
        v-model="useEncryption"
        size="is-large"
      />
    </b-field>
    <b-field
      v-if="useEncryption"
      :label="$t('message.encrypt.ephemeral')"
    > 
      <b-switch
        v-model="ephemeral"
        size="is-large"
      />
    </b-field>
    <b-field
      v-if="!ephemeral && useEncryption"
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
      v-if="!ephemeral && useEncryption"
      :label="$t('message.encrypt.phrase')"
    >
      <b-input
        v-model="passphrase"
        :placeholder="$t('message.encrypt.phrase_msg')"
        type="password"
      />
    </b-field>
    <b-field
      v-if="useEncryption"
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
        icon-left="plus"
        @click="appendPublicKey"
      >
        {{ $t("message.encrypt.addkey") }}
      </b-button>
    </b-field>
    <b-field>
      <b-table
        v-if="useEncryption"
        :data="recvkeys"
        paginated
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
        >
          <b-button
            type="is-danger"
            icon-left="delete"
            @click.prevent="recvkeys.splice(
              recvkeys.indexOf(props.row), 1)"
          >
            {{ $t('message.remove') }}
          </b-button>
        </b-table-column>
      </b-table>
    </b-field>
    <b-field :label="$t('message.encrypt.container')">
      <b-input
        v-model="container"
        :placeholder="$t('message.encrypt.container_msg')"
      />
    </b-field>
    <b-field
      :label="$t('message.encrypt.addFiles')"
    >
      <b-upload
        v-model="files"
        multiple
        expanded
      >
        <a class="button is-primary is-fullwidth">
          {{ $t('message.encrypt.dropMsg') }}
        </a>
      </b-upload>
    </b-field>
    <b-field :label="$t('message.encrypt.files')">
      <b-table
        :data="files"
        paginated
        per-page="20"
        pagination-simple
      >
        <b-table-column
          v-slot="props"
          sortable
          field="name"
          :label="$t('message.encrypt.table.name')"
        >
          {{ props.row.name }}
        </b-table-column>
        <b-table-column
          v-slot="props"
          sortable
          field="path"
          :label="$t('message.encrypt.table.path')"
        >
          {{ props.row.relativePath }}
        </b-table-column>
        <b-table-column
          v-slot="props"
          sortable
          field="size"
          :label="$t('message.encrypt.table.size')"
        >
          {{ props.row.size }}
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
          :label="$t('message.remove')"
        >
          <b-button
            type="is-danger"
            icon-left="delete"
            @click.prevent="
              files.splice(
                files.findIndex(i => {
                  if (i.relativePath) {
                    return i.relativePath === props.row.relativePath;
                  } else {
                    return i.name === props.row.name;
                  }
                }), 1
              )
            "
          >
            {{ $t('message.remove') }}
          </b-button>
        </b-table-column>
      </b-table>
    </b-field>
    <b-button
      v-if="useEncryption"
      type="is-success"
      :disabled="noUpload"
      icon-left="upload"
      @click="encryptAndUpload"
    >
      {{ $t('message.encrypt.enup') }}
    </b-button>
    <b-button
      v-else
      type="is-success"
      icon-left="upload"
      @click="beginUpload"
    >
      {{ $t('message.encrypt.normup') }}
    </b-button>
  </div>
</template>

<script>
import { getUploadEndpoint } from "@/common/api";

export default {
  name: "UploadView",
  data() {
    return {
      ephemeral: true,
      useEncryption: true,
      privkey: "",
      recvkeys: [],
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
      if (this.$t("message.keys")) {
        for (let item of Object.entries(this.$t("message.keys"))) {
          fetch(
            "/download/"
              + item[1]["project"] + "/"
              + item[1]["container"] + "/"
              + item[1]["object"],
          ).then(resp => {
            return resp.text();
          }).then(resp => {
            this.recvkeys.push(resp);
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
          item.relativePath = path + item.name;
          this.files.push(item);
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
      for (let i = 0; i < this.recvkeys.length; i++) {
        FS.writeFile( // eslint-disable-line
          "/keys/recv_keys/pubkey_" + i.toString(),
          this.recvkeys[i],
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
    appendPublicKey: function () {
      this.recvkeys.push(this.addRecvkey);
      this.addRecvkey = "";
    },
    refreshNoUpload() {
      if (this.ephemeral) {
        this.noUpload = (
          !this.recvkeys.length
          || !this.container
          || !this.files.length
        );
      } else {
        this.noUpload (
          !this.recvkeys.length
            || !this.container
            || !this.files.length
            || !this.passphrase
            || !this.privkey,
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
  },
};
</script>

<style scoped>
#uploadform {
  width: 90%;
  margin: auto;
}

</style>