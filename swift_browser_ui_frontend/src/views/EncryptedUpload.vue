<template>
  <div
    id="encryption"
    class="contents"
  >
    <b-field label="Private Key">
      <b-input
        v-model="privkey"
        placeholder="Sender private key"
        type="textarea"
        maxlength="1024"
      />
    </b-field>
    <b-field label="Receiver Public Keys">
      <b-taginput
        v-model="recvkeys"
        placeholder="Paste a receiver public key"
        type="textarea"
      />
    </b-field>
    <b-field label="Container">
      <b-input
        v-model="container"
        placeholder="Upload container"
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
            <p>Drop files that will be encrypted and uploaded.</p>
          </div>
        </section>
      </b-upload>
    </b-field>
    <b-button
      type="is-success"
      icon-left="upload"
      @click="encryptAndUpload"
    >
      Encrypt and Upload
    </b-button>
  </div>
</template>

<script>
export default {
  name: "EncryptedUpload",
  data() {
    return {
      privkey: "",
      recvkeys: [],
      container: "",
      dropFiles: [],
    };
  },
  methods: {
    encryptFiles: function () {
      // Add keys to the filesystem
      FS.mkdir("/keys"); // eslint-disable-line
      FS.mkdir("/keys/recv_keys"); // eslint-disable-line
      FS.writeFile("/keys/pk.key", this.privkey); // eslint-disable-line
      for (let i = 0; i < this.recvkeys.length; i++) {
        FS.writeFile("/keys/pubkey_" + toString(i), this.recvkeys[i]); // eslint-disable-line
      }
      // Add files to the filesystem
      FS.mkdir("/data"); // eslint-disable-line
      for (let f of this.dropFiles) {
        FS.writeFile("/data/" + f.name, f.arrayBuffer()); // eslint-disable-line
      }
      _main(); // eslint-disable-line
    },
    encryptAndUpload: function () {
      this.$buefy.toast.open("Encrypting " + this.dropFiles.length + " files");
      this.encryptFiles();
      this.$buefy.toast.open("Encryption successful.");
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
