import {
  PUT,
  GET,
  DELETE,
  getUploadEndpoint,
} from "@/common/api";

import {
  DEV,
} from "@/common/conv";

// Add a header to the ServiceWorker filesystem
function addHeader(header, fname, fsize) {
  navigator.serviceWorker.ready.then(reg => {
    reg.active.postMessage({
      cmd: "addHeader",
      header: header,
      fileName: fname,
      fileSize: fsize,
    });
  });
}

export function beginDownload() {
  navigator.serviceWorker.ready.then(reg => {
    reg.active.postMessage({
      cmd: "beginDownload",
    });
  });
}

export class DecryptedDownloadSession {
  constructor(
    active,
    project = "",
    objects = [],
    container = "",
    owner = "",
    store,
  ) {
    this.object = "";
    this.active = active;
    this.project = project;
    this.objects = objects;
    this.container = container;
    this.$store = store;
    this.finished = false;
    this.stream = undefined;
    this.size = 0;
    this.lastChunk = 0;
    this.chunks = 0;
    this.chunksLeft = 0;
    this.currentFinished = false;
    this.whitelistPath = `/cryptic/${this.active.name}/whitelist`;
    this.endpoint = store.state.uploadEndpoint;
    this.owner = owner,

    this.reader = undefined;
    this.chunk = undefined;
    this.readerDone = false;
    this.offset = 0;
    this.remainder = 0;
    this.chunkBuffer = [];

    this.controller = new AbortController();
  }

  async getFile(objectUrl) {
    const response = await fetch(objectUrl);
    let reader = response.body.getReader();
    this.reader = reader;
    let { value: chunk, done: readerDone } = await this.reader.read();

    this.chunk = chunk;
    this.readerDone = readerDone;

    this.offset = 0;
    this.remainder = 0;
    this.chunkBuffer = [];
  }

  async getSlice() {
    let chunk = this.chunk;
    let readerDone = this.readerDone;
    while (!this.readerDone) {
      this.remainder = 65564 - this.chunkBuffer.length;
      this.chunkBuffer = this.chunkBuffer.concat(
        Array.from(
          this.chunk.subarray(this.offset, this.offset + this.remainder),
        ),
      );

      if (this.chunk.length - this.offset > this.remainder) {
        this.offset += this.remainder;
        navigator.serviceWorker.ready.then(reg => {
          reg.active.postMessage({
            cmd: "decryptChunk",
            chunk: new Uint8Array(this.chunkBuffer),
          });
          this.chunkBuffer = [];
        });
        break;
      } else {
        this.offset = 0;
        ({ value: chunk, done: readerDone } = await this.reader.read());
        this.chunk = chunk;
        this.readerDone = readerDone;
      }
    }
    if (this.readerDone) {
      if (this.chunk !== undefined) {
        this.chunkBuffer = this.chunkBuffer.concat(
          Array.from(
            this.chunk.subarray(this.offset),
          ),
        );
        this.chunk = undefined;
      }

      if (this.chunkBuffer.length > 0) {
        navigator.serviceWorker.ready.then(reg => {
          reg.active.postMessage({
            cmd: "decryptChunk",
            chunk: new Uint8Array(this.chunkBuffer),
          });
          this.chunkBuffer = [];
        });
      } else {
        if (DEV) {
          console.log("Telling the serviceWorker that decryption is done.");
        }
        navigator.serviceWorker.ready.then(reg => {
          reg.active.postMessage({
            cmd: "decryptionFinished",
          });
        });
      }
    }
  }

  getFileUrl() {
    let project = this.owner != "" ? this.owner : this.project;
    let fileURL = new URL(
      `/download/${project}/${this.container}/${this.object}`,
      document.location.origin,
    );
    fileURL.searchParams.append("project", this.active.id);
    return fileURL;
  }

  async getHeader(pubkey) {
    let upInfo = await getUploadEndpoint(
      this.active.id,
      this.project,
      this.container,
    );
    this.$store.commit("setUploadInfo", upInfo);

    // Check the shared container owner canonical project name
    let ids = undefined;
    if (this.owner !== "") {
      ids = await this.$store.state.client.projectCheckIDs(this.owner);
    }

    // Check the shared container owner canonical project name
    let ids = undefined;
    if (this.owner !== "") {
      ids = await this.$store.state.client.projectCheckIDs(this.owner);
    }

    let signatureUrl = new URL(`/sign/${60}`, document.location.origin);
    signatureUrl.searchParams.append("path", this.whitelistPath);
    let signed = await GET(signatureUrl);
    signed = await signed.json();
    let whitelistUrl = new URL(this.endpoint.concat(this.whitelistPath));
    whitelistUrl.searchParams.append("valid", signed.valid);
    whitelistUrl.searchParams.append("signature", signed.signature);
    whitelistUrl.searchParams.append("flavor", "crypt4gh");
    whitelistUrl.searchParams.append(
      "session",
      this.$store.state.uploadInfo.id,
    );
    let resp = await PUT(whitelistUrl, pubkey);
    let headerPath = `/header/${this.active.name}/${this.container}/${this.object}`;
    signatureUrl = new URL(`/sign/${60}`, document.location.origin);
    signatureUrl.searchParams.append("path", headerPath);
    signed = await GET(signatureUrl);
    signed = await signed.json();
    let headerUrl = new URL(this.endpoint.concat(headerPath));
    if (this.owner !== "") {
      headerUrl.searchParams.append("owner", ids.name);
    }
    headerUrl.searchParams.append("valid", signed.valid);
    headerUrl.searchParams.append("signature", signed.signature);
    headerUrl.searchParams.append(
      "session",
      this.$store.state.uploadInfo.id,
    );
    resp = await GET(headerUrl);
    let header = await resp.text();
    header = Uint8Array.from(atob(header), c => c.charCodeAt(0));
    addHeader(
      header,
      this.object.split("/").pop(),
      undefined,
    );
  }

  initServiceWorker() {
    navigator.serviceWorker.addEventListener("message", (e) => {
      e.stopImmediatePropagation();
      switch (e.data.eventType) {
        case "downloadSessionOpened":
          this.object = this.objects.pop();
          this.currentFinished = false;
          if (this.object == undefined) {
            this.finished = true;
          }
          this.getHeader(e.data.pubKey).then(() => { });
          break;
        case "beginDecryption":
          window.open(new URL("/file", document.location.origin), "_blank");
          this.getFile(this.getFileUrl()).then(() => {
            this.getSlice().then(() => {
              if (DEV) console.log("Added first slice to serviceworker.");
            });
          });
          break;
        case "nextDecryptChunk":
          this.getSlice().then(() => { });
          break;
        case "streamClosed":
          (async () => {
            let signatureUrl = new URL(`/sign/${60}`, document.location.origin);
            signatureUrl.searchParams.append("path", this.whitelistPath);
            let signed = await GET(signatureUrl);
            signed = await signed.json();
            let whitelistUrl = new URL(
              this.endpoint.concat(this.whitelistPath),
            );
            whitelistUrl.searchParams.append("valid", signed.valid);
            whitelistUrl.searchParams.append("signature", signed.signature);
            await DELETE(whitelistUrl);
            if (this.objects.length > 0) {
              beginDownload();
            } else {
              this.controller.abort();
            }
          })();
          break;
      }
    }, { signal: this.controller.signal });
  }
}
