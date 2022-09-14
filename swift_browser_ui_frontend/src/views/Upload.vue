<template>
  <div
    id="uploadform"
    class="contents"
  > 
    <b-message
      v-if="$te('message.keys') && pubkey.length > 0"
      type="is-info"
    >
      {{ $t('message.encrypt.defaultKeysMessage') }}
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
      :data="dropFiles"
      paginated
      focusable
      hoverable
      narrowed
      default-sort="name"
      per-page="10"
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
        {{ (!props.row.relativePath ? props.row.name : props.row.relativePath)
          | truncate(100) }}
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
          @click="$store.commit('eraseDropFile', props.row)"
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
        accept
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
        type="is-info is-light"
        icon-left="cached"
        @click="clearFiles"
      >
        {{ $t('message.encrypt.clearDrop') }}
      </b-button>
      <b-button
        v-if="useEncryption"
        id="uploadButton"
        type="is-success"
        :disabled="noUpload"
        icon-left="upload-lock"
        @click="beginEncryptedUpload"
      >
        {{ $t('message.encrypt.enup') }}
      </b-button>
      <b-button
        v-else
        id="uploadButton"
        type="is-success"
        :disabled="noUpload"
        icon-left="upload-lock"
        @click="beginUpload"
      >
        {{ $t('message.encrypt.normup') }}
      </b-button>
      <b-button
        type="is-light"
        icon-left="cancel"
        @click="cancelUpload"
      >
        {{ $t('message.encrypt.cancel') }}
      </b-button>
    </div>
  </div>
</template>

<script>
import { getUploadEndpoint } from "@/common/api";
import { getHumanReadableSize, truncate, computeSHA256 } from "@/common/conv";
import EncryptedUploadSession from "@/common/upload";

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
    pubkey () {
      return this.$store.state.pubkey;
    },
    dropFiles () {
      return this.$store.state.dropFiles;
    },
    currentUpload () {
      return this.$store.state.uploadState;
    },
    files: {
      get () {
        return this.$store.state.dropFiles.message;
      },
      set (value) {
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
    dropFiles: function () {
      this.refreshNoUpload();
    },
    ephemeral: function () {
      this.refreshNoUpload();
    },
    useEncryption: function () {
      this.refreshNoUpload();
    },
  },
  created () {
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
      if(this.$route.params.container) {
        this.container = this.$route.params.container;
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
        this.$router.go(-1);
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
          (!this.pubkey.length && !this.recvkeys.length)
          || !this.container
          || !this.dropFiles.length
          || (this.currentUpload != undefined)
        );
      } 
      if (this.ownPrivateKey) {
        this.noUpload = (
          (!this.pubkey.length && !this.recvkeys.length)
          || !this.container
          || !this.dropFiles.length
          || (!this.passphrase && !this.privkey)
          || (this.currentUpload != undefined)
        );
      }
      if (!this.useEncryption) {
        this.noUpload = this.dropFiles.length === 0;
      }
    },
    // Make human readable translation functions available in instance
    // namespace
    localHumanReadableSize: function ( size ) {
      return getHumanReadableSize( size );
    },
    clearFiles() {
      this.$store.commit("eraseDropFiles");
    },
    beginEncryptedUpload() {
      if (this.pubkey.length > 0) {
        this.recvkeys = this.recvkeys.concat(this.pubkey);
      }
      let upload = new EncryptedUploadSession(
        this.active,
        this.$route.params.owner ? this.$route.params.owner : this.active.id,
        this.$store.state.dropFiles,
        this.recvkeys,
        this.privkey,
        this.container,
        this.$route.query.prefix,
        this.passphrase,
        this.ephemeral,
        this.$store,
      );
      upload.initServiceWorker();
      upload.initServiceWorker();
      this.$store.commit("setCurrentUpload", upload);
      upload.cleanUp();
      this.toggleUploadModal();
    },
    cancelUpload() {
      this.$store.commit("eraseDropFiles");
      this.$router.go(-1);
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

@media screen and ( max-width: 1357px){
  #encryptionOptions {
    margin-top: 0;
  }
  
}

</style>