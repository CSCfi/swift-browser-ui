// Functions for handling interfacing between workers and upload API socket

import { DELETE, GET, PUT, getUploadEndpoint, getUploadSocket } from "./api";
import { DEV } from "./conv";
import { getDB } from "./db";


export default class UploadSocket {
  constructor(
    active,
    project = "",
    store,
  ) {
    this.active = active;
    this.project = project;
    this.$store = store;

    this.inputFiles = {};
    this.outputFiles = {};

    this.useServiceWorker = "serviceWorker" in navigator
      && window.showSaveFilePicker === undefined;

    // Initialize the workers
    // The workers will eventually handle threading by themselves, to
    // avoid blocking the main browser thread
    this.upWorker = new Worker("/upworker.js");
    if (this.useServiceWorker) {
      if (DEV) console.log("Registering download script into service worker.");
      let workerUrl = new URL("/downworker.js", document.location.origin);
      navigator.serviceWorker.register(workerUrl).then(reg => {
        reg.update();
      }).catch((err) => {
        if (DEV) console.log("Failed to register the service worker.");
        if (DEV) console.log(err);
      });
      this.downWorker = undefined;
    } else if (window.showSaveFilePicker !== undefined) {
      if (DEV) {
        console.log("Registering the download script as a normal worker.");
      }
      this.downWorker = new Worker("/downworker.js");
    } else {
      if (DEV) console.log("Could not register a worker for download.");
      if (DEV) console.log("Decrypted downloads are not available.");
    }

    // Add message handlers for upload and download workers
    let handleUpWorker = (e) => {
      switch(e.data.eventType) {
        case "uploadCreated":
          break;
        case "webSocketOpened":
          break;
        case "retryChunk":
          if (DEV) console.log("Retrying a chunk.");
          break;
        case "activeFile":
          this.$store.commit(
            "setEncryptedFile",
            e.data.object,
          );
          break;
        case "progress":
          this.$store.commit(
            "updateEncryptedProgress",
            e.data.progress,
          );
          this.$store.commit(
            "updateProgress",
            e.data.progress,
          );
          break;
        case "abort":
          break;
        case "success":
          break;
        case "finished":
          this.$store.commit("eraseNotClosable");
          this.$store.commit("eraseDropFiles");
          this.$store.commit("stopUploading");
          break;
      }
    };
    let handleDownWorker = (e) => {
      switch(e.data.eventType) {
        case "getHeaders":
          this.getHeaders(
            e.data.container,
            e.data.files,
            e.data.pubkey,
          ).then(() => {
            if (DEV) {
              console.log(
                `Got headers for download in container ${e.data.container}`,
              );
            }
          });
          break;
        case "finished":
          if (DEV) {
            console.log(
              `Finished a download in container ${e.data.container}`,
            );
          }
          break;
      }
    };

    this.handleUpWorker = handleUpWorker;
    this.handleDownWorker = handleDownWorker;

    this.upWorker.onmessage = handleUpWorker;
    if (this.useServiceWorker) {
      navigator.serviceWorker.addEventListener(
        "message",
        handleDownWorker,
      );
    } else if (window.showSaveFilePicker !== undefined) {
      this.downWorker.onmessage = handleDownWorker;
    }
  }

  // Get headers for download
  async getHeaders(container, fileList, pubkey) {
    let headers = {};

    // If no files are specified, get all files in the container
    let files;
    if (fileList.length < 1) {
      let dbContainer = await getDB().containers
        .get({
          projectID: this.active.id,
          name: container,
        });
      let objects = await getDB().objects
        .where({"containerID": dbContainer.id})
        .toArray();
      files = objects.map(item => item.name);
    } else {
      files = fileList;
    }

    let whitelistPath = `/cryptic/${this.active.name}/whitelist`;

    let upInfo = await getUploadEndpoint(
      this.active.id,
      this.project,
      container,
    );

    let signatureUrl = new URL(`/sign/${60}`, document.location.origin);
    signatureUrl.searchParams.append("path", whitelistPath);
    let signed = await GET(signatureUrl);
    signed = await signed.json();
    let whitelistUrl = new URL(
      this.$store.state.uploadEndpoint.concat(whitelistPath),
    );
    whitelistUrl.searchParams.append("valid", signed.valid);
    whitelistUrl.searchParams.append("signature", signed.signature);
    whitelistUrl.searchParams.append("flavor", "crypt4gh");
    whitelistUrl.searchParams.append("session", upInfo.id);
    await PUT(whitelistUrl, pubkey);

    for (const file of files) {
      // Get the file header
      let headerPath = `/header/${this.active.name}/${container}/${file}`;
      signatureUrl = new URL(`/sign/${60}`, document.location.origin);
      signatureUrl.searchParams.append("path", headerPath);
      signed = await GET(signatureUrl);
      signed = await signed.json();
      let headerUrl = new URL(
        this.$store.state.uploadEndpoint.concat(headerPath),
      );
      headerUrl.searchParams.append("valid", signed.valid);
      headerUrl.searchParams.append("signature", signed.signature);
      headerUrl.searchParams.append("session", upInfo.id);
      let resp = await GET(headerUrl);
      let header = await resp.text();

      // Prepare and sign the file URL
      let fileUrl = new URL(
        `/download/${this.active.id}/${container}/${file}`,
        document.location.origin,
      );
      fileUrl.searchParams.append("project", this.active.id);

      headers[file] = {
        header: Uint8Array.from(atob(header), c => c.charCodeAt(0)),
        url: fileUrl.toString(),
      };
    }

    await DELETE(whitelistUrl);

    if (this.downWorker !== undefined) {
      this.downWorker.postMessage({
        command: "addHeaders",
        container: container,
        headers: headers,
      });
    } else {
      navigator.serviceWorker.ready.then((reg) => {
        reg.active.postMessage({
          command: "addHeaders",
          container: container,
          headers: headers,
        });
      });
    }
  }

  // Get the latest upload endpoint
  async updateEndpoint() {
    let upinfo = await getUploadSocket(
      this.active.id,
      this.active.id,
    );

    return upinfo;
  }

  // Open the websocket for runner communication
  openSocket() {
    this.updateEndpoint().then(upinfo => {
      this.upWorker.postMessage({
        command: "openWebSocket",
        upinfo: upinfo,
      });
      if (DEV) console.log("Instructed upWorker to open the websocket.");
    });
  }

  // Schecule file/files for upload
  addUpload(
    container,
    files,
    receivers,
    owner = "",
    ownerName = "",
  ) {
    let uploadFiles = [];
    for (const file of files) {
      uploadFiles.push({
        relativePath: file.relativePath,
        file: file,
      });
    }

    this.upWorker.postMessage({
      command: "addFiles",
      container: container,
      receivers: receivers,
      projectName: this.active.name,
      owner: owner,
      ownerName: ownerName,
      files: uploadFiles,
    });

    if (DEV) console.log("Pushed new files to the service worker.");
    this.$store.commit("setUploading");
    this.$store.commit("setNotClosable");
  }

  // Schedule file/files for download
  async addDownload(
    container,
    objects,
  ) {
    let fileHandle = undefined;
    if (objects.length == 1) {
      // Download directly into the file if available.
      // Otherwise, use streaming + ServiceWorker.
      if (window.showSaveFilePicker !== undefined) {
        // Match the file identifier
        const fident = objects[0].replace(".c4gh", "").match(/\.[^.]*$/g);

        fileHandle = await window.showSaveFilePicker({
          suggestedName: objects[0].replace(".c4gh", ""),
          types: [
            {
              description: "Generic file",
              accept: {
                "application/octet-stream": [fident],
              },
            },
          ],
        });
        this.downWorker.postMessage({
          command: "downloadFile",
          container: container,
          file: objects[0],
          handle: fileHandle,
        });
      } else {
        if (DEV) {
          console.log("Instructing ServiceWorker to add a file to downloads.");
        }
        let downloadUrl = new URL(
          `/file/${container}/${objects[0]}`,
          document.location.origin,
        );
        if (DEV) console.log(downloadUrl);
        window.open(downloadUrl, "_blank");
        setTimeout(() => {
          navigator.serviceWorker.ready.then(reg => {
            reg.active.postMessage({
              command: "downloadFile",
              container: container,
              file: objects[0],
            });
          });
        }, 500);
      }
    } else {
      // Download directly into the archive if available.
      // Otherwise, use streaming + ServiceWorker.
      if (window.showSaveFilePicker !== undefined) {
        fileHandle = await window.showSaveFilePicker({
          suggestedName: `${container}_download.tar`,
          types: [
            {
              description: "Tar archive (uncompressed)",
              accept: {
                "application/x-tar": [".tar"],
              },
            },
          ],
        });
        this.downWorker.postMessage({
          command: "downloadFiles",
          container: container,
          files: objects.length < 1 ? [] : objects,
          handle: fileHandle,
        });
      } else {
        let downloadUrl = new URL(
          `/archive/${container}.tar`,
          document.location.origin,
        );
        if (DEV) console.log(downloadUrl, "_blank");
        window.open(downloadUrl, "_blank");
        setTimeout(() => {
          navigator.serviceWorker.ready.then(reg => {
            reg.active.postMessage({
              command: "downloadFiles",
              container: container,
              files: objects.length < 1 ? [] : objects,
            });
          });
        }, 500);
      }
    }
  }
}
