import { buffer, iif } from "@/../node_modules/rxjs/dist/types/index";
import { getUploadCryptedEndpoint } from "./api";

// Add a header to the ServiceWorker filesystem
function addHeader(header) {
  navigator.serviceWorker.ready.then(reg => {
    reg.active.postMessage({
      cmd: "addHeader",
      header: header,
    });
  });
}

function beginDownload() {
  navigator.serviceWorker.ready.then(reg => {
    reg.active.postMessage({
      cmd: "beginDownload",
    });
  });
}

export default class DecryptedDownloadSession {
  constructor(
    active,
    project = "",
    objects = [],
    container = "",
    store,
  ) {
    this.object = "";
    this.active = active;
    this.project = project;
    this.objects = objects;
    this.continer = container;
    this.$store = store;
    this.finished = false;
    this.stream = undefined;
    this.size = 0;
    this.lastChunk = 0;
    this.chunks = 0;
    this.chunksLeft = 0;
    this.currentFinished = false;
  }

  async processBytes({done, value}) {
    if (done) {
      return;
    }

    buffer = value.buffer;
    offset += value.byteLength;

    done, value = await reader.read(new Uint8Array(
      buffer,
      offset,
      buffer.byteLength - offset,
    ));

    return await processBytes({done, value});
}

  // Imagine needing a separate function to specify chunk size when reading
  // response streams SMH
  async readChunk() {
    let buffer = new ArrayBuffer(65564);

    let offset = 0;
    let reader = this.stream;

    let done, value;

    while (offset < buffer.byteLength) {
      done, value = await reader.read(new Uint8Array(
        buffer,
        offset,
        buffer.byteLength - offset
      ));

      if(done) {
        this.finished = true;
        break;
      }

      await processBytes(done, value);
    }

    console.log(buffer);
    return buffer;
  }

  async decryptChunk() {
    if (this.finished) {
      await navigator.serviceWorker.ready.then(reg => {
        reg.active.postMessage({
          cmd: "decryptionFinishded",
        });
      });
    }
    let buf = await this.readChunk();
    await navigator.serviceWorker.ready.then(reg => {
      reg.active.postMessage({
        cmd: "decryptChunk",
        chunk: buf,
      });
    });
  }

  initServiceWorker() {
    navigator.serviceWorker.addEventListener("message", (e) => {
      e.stopImmediatePropagation();
      switch(e.data.eventType) {
        case "downloadSessionOpened":
          break;
        case "beginDecryption":
          this.object = objects.pop();
          this.currentFinished = false;
          if (this.object == undefined) {
            this.finished = true;
          }
          
          let fileURL = new URL(
            `/download/${project}/${container}/${this.object}`,
            document.location.origin,
          );
          fileURL.searchParams.append("project", this.active.id);
          fetch(fileURL)
            .then(resp => {
              // Open the buffer in BYOB mode to allow chunking properly
              this.stream = resp.body.getReader({
                mode: "byob",
              });
              this.size = resp.headers.get("Content-Length");
              this.chunks = Math.floor(
                this.size / 65564
              );
              if (this.size % 65564 > 0) {
                this.lastChunk = this.size % 65564;
              }
            })
            .then(() => {
              this.decryptChunk();
            });
          break;
        case "nextDecryptChunk":
          this.decryptChunk();
          break;
        case "streamClosed":
          break;
      }
    });
  }
}
