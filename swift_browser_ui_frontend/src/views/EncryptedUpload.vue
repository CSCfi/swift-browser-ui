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
    <b-field label="Public Key">
      <b-input
        v-model="pubkey"
        placeholder="Sender public key"
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
      pubkey: "",
      recvkeys: [],
      container: "",
      dropFiles: [],
    };
  },
  methods: {
    encryptAndUpload: function () {
      this.$buefy.toast.open("Init upload");
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
