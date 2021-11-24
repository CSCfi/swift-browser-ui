<template>
  <div
    id="encryption"
    class="contents"
  >
    <b-field :label="$t('message.encrypt.ephemeral')"> 
      <b-switch
        v-model="ephemeral"
        size="is-large"
      />
    </b-field>
    <b-field
      v-if="!ephemeral"
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
      v-if="!ephemeral"
      :label="$t('message.encrypt.phrase')"
    >
      <b-input
        v-model="passphrase"
        :placeholder="$t('message.encrypt.phrase_msg')"
        type="password"
      />
    </b-field>
    <b-field :label="$t('message.encrypt.pubkey')">
      <b-input
        v-model="addRecvkey"
        :placeholder="$t('message.encrypt.pubkey_msg')"
        type="textarea"
        maxlength="1024"
      />
    </b-field>
    <b-field>
      <b-button
        type="is-success"
        icon-left="plus"
        @click="appendPublicKey"
      >
        {{ $t("message.encrypt.addkey") }}
      </b-button>
    </b-field>
    <b-field :label="$t('message.encrypt.bucket')">
      <b-input
        v-model="container"
        :placeholder="$t('message.encrypt.bucket_msg')"
      />
    </b-field>
    <b-field>
      <b-upload
        v-model="dropFiles"
        multiple
        drag-drop
        expanded
      >
        <section class="section">
          <div class="content has-text-centered">
            <p>
              <b-icon
                icon="upload"
                size="is-large"
              />
            </p>
            <p>{{ $t('message.encrypt.drop_msg') }}</p>
          </div>
        </section>
      </b-upload>
    </b-field>
    <b-taglist>
      <b-tag
        v-for="item in recvkeys"
        :key="item"
        closable
        type="is-info"
        @close="recvkeys.splice(recvkeys.indexOf(item), 1)"
      >
        {{ item }}
      </b-tag>
    </b-taglist>
    <b-button
      type="is-success"
      :disabled="noUpload"
      icon-left="upload"
      @click="encryptAndUpload"
    >
      {{ $t('message.encrypt.enup').concat(
        dropFiles.length,
        $t('message.encrypt.enfiles'),
      ) }}
    </b-button>
  </div>
</template>

<script>
export default {
  name: "EncryptedUpload",
  data() {
    return {
      ephemeral: true,
      privkey: "",
      recvkeys: [],
      container: "",
      passphrase: "",
      dropFiles: [],
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
  },
  watch: {
    container: function () {
      this.$router.replace({
        name: "EncryptedUpload",
        params: {
          "project": this.$route.params.project,
          "container": this.container,
        },
      });
      this.$route.params.container = this.container;
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
  },
  created () {
    this.setContainer();
  },
  methods: {
    setContainer: function () {
      if(this.$route.params.container) {
        this.container = this.$route.params.container;
      }
    },
    encryptFiles: async function () {
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
      for (let f of this.dropFiles) {
        let buf = new Uint8Array(await f.arrayBuffer());
        let outname = "/data/" + f.name;
        FS.writeFile(outname, buf); // eslint-disable-line
      }

      let res = 0;
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
      console.log(res);
    },
    encryptAndUpload: function () {
      this.$buefy.toast.open("Encrypting " + this.dropFiles.length + " files");
      this.encryptFiles().then(() => {
        this.$buefy.toast.open("Encryption successful.");
        this.$store.commit("setAltContainer", this.$route.params.container);
        let files = [];
        for (let f of this.dropFiles) {
          let outname = "/data/" + f.name + ".c4gh";
          let newFile = new Blob(
            [FS.readFile(outname).buffer], // eslint-disable-line
            {
              type: "binary/octet-stream",
            },
          );
          newFile.name = f.name + ".c4gh";
          files.push(newFile);
        }
        this.res.addFiles(files, undefined);
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
          || !this.dropFiles.length
        );
      } else {
        this.noUpload (
          !this.recvkeys.length
            || !this.container
            || !this.dropFiles.length
            || !this.passphrase
            || !this.privkey,
        );
      }
    },
  },
};
</script>

<style scoped>
#encryption {
  width: 80%;
  margin: auto;
}
</style>
