import {
  getUploadCryptedEndpoint,
  killUploadEndpoint,
} from "@/common/api";
import { getDB } from "@/common/db";

// Add a private key to the ServiceWorker filesystem
function addPrivKey(pkey) {
  navigator.serviceWorker.ready.then(reg => {
    reg.active.postMessage({
      cmd: "addPrivKey",
      privkey: pkey,
    });
  });
}

// Append a public key to the ServiceWorker filesystem
function appendPubKey(pub, name) {
  navigator.serviceWorker.ready.then(reg => {
    reg.active.postMessage({
      cmd: "appendPubkey",
      pubkey: pub,
      keyname: name,
    });
  });
}

// Start an ephemeral file encryption
function initEphemeral(filename) {
  navigator.serviceWorker.ready.then(reg => {
    reg.active.postMessage({
      cmd: "initEphemeral",
      fileName: filename,
    });
  });
}

// Start a normal file encryption
function initNormal(
  filename,
  passphrase,
) {
  navigator.serviceWorker.ready.then(reg => {
    reg.active.postMessage({
      cmd: "initNormal",
      passphrase: passphrase,
      fileName: filename,
    });
  });
}

// Ask ServiceWorker to create the file header
function createHeader() {
  navigator.serviceWorker.ready.then(reg => {
    reg.active.postMessage({
      cmd: "createHeader",
    });
  });
}

export default class EncryptedUploadSession {
  constructor(
    active,
    project = "",
    files = [],
    receivers = [],
    pkey = "",
    container = "",
    prefix = "",
    passphrase = "",
    ephemeral = true,
    store,
    el,
  ) {
    this.active = active;
    this.project = project;
    this.files = files;
    this.container = container;
    this.prefix = prefix.length == 0 ? "" : `${prefix}/`;
    this.$store = store;
    this.$el = el;
    this.ephemeral = ephemeral;
    this.receivers = receivers;
    this.pkey = pkey;
    this.passphrase = passphrase;
    this.signal = store.state.uploadAbort.signal;

    this.totalFiles = this.files.length;
    this.finished = false;
    this.currentFile = "";
    this.ptr = 0;
    this.currentTotalBytes = 0;
    this.currentUpload = undefined;
    this.currentTotalChunks = 0;
    this.socket = undefined;
    this.headUrl = undefined;
    this.ingestUrl = undefined;
    this.currentChunks = [];
    this.totalChunks = 0;

    for (let f of this.files) {
      this.totalChunks += Math.floor(f.size / 65536);
      if (f.size % 65536) this.totalChunks++;
    }
    this.totalUploadedChunks = 0;

    this.handleMessage = (e) => {
      e.stopImmediatePropagation();
      switch (e.data.eventType) {
        case "wasmFilesystemInitialized":
          this.$store.commit("stopChunking");
          this.$store.commit("setUploading");
          if (!this.ephemeral) {
            addPrivKey(this.pkey);
          }
          appendPubKey(this.receivers[0], 1);
          break;
        case "wasmFilesystemPubkeyAdded":
          if (e.data.publicKeyOrder < this.receivers.length)  {
            appendPubKey(
              this.receivers[e.data.publicKeyOrder],
              e.data.publicKeyOrder + 1,
            );
          }
          else if (this.ephemeral) {
            initEphemeral(this.currentFile);
          }
          else {
            initNormal(
              this.passphrase,
              this.currentFile,
            );
          }
          break;
        case "encryptSessionInitiated":
          this.ptr = e.data.ptr;
          createHeader();
          break;
        case "encryptedHeaderReady":
          this.headUrl = new URL(this.$store.state.uploadInfo.url);
          this.headUrl.searchParams.append(
            "session",
            this.$store.state.uploadInfo.id,
          );
          this.headUrl.searchParams.append(
            "valid", this.$store.state.uploadInfo.signature.valid,
          );
          this.headUrl.searchParams.append(
            "signature", this.$store.state.uploadInfo.signature.signature,
          );
          this.headUrl.searchParams.append("total", this.currentTotalBytes);
          this.currentUpload = fetch(
            this.headUrl,
            {
              method: "PUT",
              mode: "cors",
              cache: "no-cache",
              headers: {
                "Content-Type": "application/octet-stream",
              },
              body: e.data.header,
            },
          ).then(() => {
            this.ingestUrl = new URL(this.$store.state.uploadInfo.wsurl);
            this.ingestUrl.searchParams.append(
              "session",
              this.$store.state.uploadInfo.id,
            );
            this.ingestUrl.searchParams.append(
              "valid", this.$store.state.uploadInfo.wssignature.valid,
            );
            this.ingestUrl.searchParams.append(
              "signature", this.$store.state.uploadInfo.wssignature.signature,
            );
            this.socket = new WebSocket(this.ingestUrl);
            this.socket.onmessage = (message) => {
              let mout = JSON.parse(message.data);
              switch (mout.cmd) {
                case "nextChunk":
                  this.encryptChunk(this.currentChunks.shift());
                  break;
                case "retryChunk":
                  this.encryptChunk(mout.iter);
                  break;
                case "canClose":
                  this.socket.close();
                  this.cleanUp();
                  break;
              }
            };
            this.socket.onopen = () => {
              this.socket.send("startPull");
            };
          });
          break;
        case "nextChunk":
          if (this.finished) {
            break;
          }
          this.$store.commit(
            "updateEncryptedFileProgress",
            this.currentByte / this.currentTotalBytes,
          );
          this.$store.commit(
            "updateProgress",
            this.totalUploadedChunks / this.totalChunks,
          );
          // Simplest way found for JS array -> binary conversion
          this.socket.send(JSON.stringify({
            iter: e.data.iter,
            chunk: btoa(String.fromCharCode(...e.data.chunk)),
          }));
          break;
        case "cleanUpDone":
          delete this.socket;
          this.$store.commit(
            "updateEncryptedProgress",
            (this.totalFiles - this.files.length) / this.totalFiles,
          );

          // Cache the succeeded file metadata to IndexedDB
          getDB().containers.get({
            projectID: this.project,
            name: this.container,
          }).then(async container => {
            await this.$store.dispatch("updateObjects", {
              projectID: this.project,
              container: container,
              signal: undefined,
            });
          }).catch(() => {});

          if (this.files.length > 0) {
            this.currentFile = undefined;
            this.initFileSystem();
          }
          else {
            this.$store.commit("eraseEncryptedProgress");
            this.$store.commit("eraseEncryptedFile");
            this.$store.commit("eraseEncryptedFileProgress");
            this.$store.commit("stopUploading");
            this.$store.commit("stopChunking");
            killUploadEndpoint(
              this.active.id,
              this.project,
            ).then(() => {})
              .catch(() => {});
            document
              .getElementById("mainContent")
              .dispatchEvent(new Event("uploadComplete"));
            // Try if purging the upload session from inside the upload
            // session doesn't break anything
            this.$store.commit("abortCurrentUpload");
            this.$store.commit("eraseCurrentUpload");
          }
          break;
      }
    };
  }

  encryptChunk(i) {
    if (i === undefined) {
      return;
    }
    let ptr = i * 65536;
    navigator.serviceWorker.ready.then(reg => {
      this.currentFile.slice(
        ptr,
        ptr + 65536,
      ).arrayBuffer().then(c => {
        reg.active.postMessage(
          {
            cmd: "encryptChunk",
            chunk: c,
            iter: i,
          },
        );
        this.currentByte += 65536;
        this.totalUploadedChunks += 1;
      });
    });
  }

  // Ask ServiceWorker to clean up the filesystem
  cleanUp() {
    navigator.serviceWorker.ready.then(reg => {
      reg.active.postMessage({
        cmd: "cleanUp",
      });
    });
  }

  // Initialize filesystem for encrypting a file
  initFileSystem() {
    this.currentFile = this.files.pop();
    this.$store.commit(
      "setEncryptedFile",
      this.currentFile.name + ".c4gh",
    );
    // Total size of the file will be increased by 28 bytes per
    // each 64KiB block
    this.currentTotalBytes = Math.floor(
      this.currentFile.size / 65536,
    ) * 65564;
    this.currentByte = 0;
    // Plus the last block if it exists
    if (this.currentFile.size % 65536 > 0) {
      this.currentTotalBytes += this.currentFile.size % 65536 + 28;
    }
    this.currentTotalChunks = Math.floor(
      this.currentFile.size / 65536,
    );
    if (this.currentFile.size % 65536) {
      this.currentTotalChunks++;
    }
    for (let i= 0; i < this.currentTotalChunks; i++) {
      this.currentChunks.push(i);
    }
    getUploadCryptedEndpoint(
      this.active.id,
      this.project,
      this.container,
      `${this.prefix}${this.currentFile.relativePath ? this.currentFile.relativePath : this.currentFile.name}.c4gh`,
    ).then(resp => {
      this.$store.commit("setUploadInfo", resp);
      navigator.serviceWorker.ready.then(reg => {
        reg.active.postMessage({
          cmd: "initFileSystem",
        });
      });
    });
  }

  cancelUpload() {
    this.finished = true;
    this.files = [];
    this.socket.close();
    this.cleanUp();
  }

  // Initialize the service worker for upload session
  initServiceWorker() {
    // Add event listener for the current upload session
    navigator.serviceWorker.addEventListener(
      "message",
      this.handleMessage, {signal: this.signal},
    );
  }
}
