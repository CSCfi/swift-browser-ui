// Functions for handling interfacing between workers and upload API socket

import { getUploadEndpoint, getUploadSocket, signedFetch } from "./api";
import { DEV } from "./conv";
import { getDB } from "./db";
import { timeout } from "./globalFunctions";


export default class UploadSocket {
  constructor(
    active,
    project = "",
    store,
    t,
  ) {
    this.active = active;
    this.project = project;
    this.$store = store;
    this.$t = t;

    this.inputFiles = {};
    this.outputFiles = {};

    this.downloadFinished = true; // track download progress with service worker

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

    this.toastMessage = {
      duration: 6000,
      persistent: false,
      progress: false,
    };

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
            "updateProgress",
            e.data.progress,
          );
          break;
        case "abort":
          this.$store.commit("setUploadAbortReason", e.data.reason);
          this.$store.commit("stopUploading", true);
          this.$store.commit("toggleUploadNotification", false);
          this.$store.commit("eraseProgress");
          this.$store.commit("eraseDropFiles");
          break;
        case "success":
          break;
        case "finished":
          this.$store.commit("eraseDropFiles");
          this.$store.commit("stopUploading");
          this.$store.commit("eraseProgress");
          break;
      }
    };
    let handleDownWorker = (e) => {
      switch(e.data.eventType) {
        case "getHeaders":
          if (this.$store.state.downloadCount <= 0) {
            this.$store.commit("eraseDownloadProgress");
          }
          this.$store.commit("addDownload");
          this.getHeaders(
            e.data.id,
            e.data.container,
            e.data.files,
            e.data.pubkey,
            e.data.owner,
            e.data.ownerName,
          ).then(() => {
            if (this.useServiceWorker) {
              this.$store.commit("removeDownload");
              this.$store.commit("toggleDownloadNotification", false);
            } else {
              if (this.$store.state.downloadProgress === undefined) {
                this.$store.commit("updateDownloadProgress", 0);
              }
            }
            if (DEV) {
              console.log(
                `Got headers for download in container ${e.data.container}`,
              );
            }
          }).catch(() =>  {
            this.downWorker.postMessage({ command: "abort", reason: "error" });
          });
          break;
        case "downloadStarted":
          if (DEV) {
            console.log(
              `Started downloading in container ${e.data.container}`,
            );
          }
          if (this.useServiceWorker) {
            this.downloadFinished = false;
            if (e.data.archive) {
              let downloadUrl = new URL(
                `/archive/${e.data.id}/${e.data.container}.tar`,
                document.location.origin,
              );
              if (DEV) console.log(downloadUrl);
              window.open(downloadUrl, "_blank");
            } else {
              let downloadUrl = new URL(
                `/file/${e.data.id}/${e.data.container}/${e.data.path}`,
                document.location.origin,
              );
              if (DEV) console.log(downloadUrl);
              window.open(downloadUrl, "_blank");
            }
          }
          break;
        case "downloadProgressing":
          if (this.useServiceWorker) {
            navigator.serviceWorker.ready.then(async(reg) => {
              while (!this.downloadFinished) {
                // keep the service worker awake while downloading
                reg.active.postMessage({
                  command: "keepDownloadProgressing",
                });
                await timeout(10000);
              }
            });
          }
          break;
        case "notDecryptable":
          if (DEV) {
            console.log(`Could not decrypt all files in container ${e.data.container}`);
          }
          document.querySelector("#decryption-toasts").addToast(
            {
              ...this.toastMessage,
              type: "warning",
              message: this.$t("message.notDecryptable"),
            },
          );
          break;
        case "abort":
          this.$store.commit("setDownloadAbortReason", e.data.reason);
          if (!this.useServiceWorker) {
            this.$store.commit("removeDownload", true);
            this.$store.commit("eraseDownloadProgress");
          }
          break;
        case "progress":
          this.$store.commit("updateDownloadProgress", e.data.progress);
          break;
        case "finished":
          if (DEV) {
            console.log(
              `Finished a download in container ${e.data.container}`,
            );
          }
          if (!this.useServiceWorker) {
            if (this.$store.state.downloadCount === 1) {
              this.$store.commit("updateDownloadProgress", 1);
              this.downWorker.postMessage({
                command: "clear",
              });
              if (DEV) {
                console.log("Clearing download progress interval");
              }
            }
            this.$store.commit("removeDownload");
          }
          else {
            this.downloadFinished = true;
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
  async getHeaders(id, container, fileList, pubkey, owner, ownerName) {
    let headers = {};

    // Cache the container ID
    let dbContainer = await getDB().containers
      .get({
        projectID: this.active.id,
        name: container,
      });

    const dbContainerFileCount = await getDB().objects
      .where({"containerID": dbContainer.id})
      .count();

    let dbContainerFiles = [];

    while (dbContainerFiles.length < dbContainerFileCount
      || dbContainerFiles.length < dbContainer.count) {
      //check both: container.count not updated in obj view, and
      //obj count might not be updated in time if there's many
      dbContainerFiles = await getDB().objects
        .where({"containerID": dbContainer.id})
        .toArray();
      await timeout(250);
    }

    // If files are specified, use only the specified file listing
    if (fileList.length >= 1) {
      dbContainerFiles = dbContainerFiles.filter(
        item => fileList.includes(item.name),
      );
    }

    let whitelistPath = `/cryptic/${this.active.name}/whitelist`;

    let upInfo = await getUploadEndpoint(
      this.active.id,
      this.project,
      container,
    );

    await signedFetch(
      "PUT",
      this.$store.state.uploadEndpoint,
      whitelistPath,
      pubkey,
      {
        flavor: "crypt4gh",
        session: upInfo.id,
      },
    );

    for (const file of dbContainerFiles) {
      // Get the file header
      let header = await signedFetch(
        "GET",
        this.$store.state.uploadEndpoint,
        `/header/${this.active.name}/${container}/${file.name}`,
        undefined,
        {
          session: upInfo.id,
          owner: ownerName,
        },
      );
      header = await header.text();

      // Prepare the file URL
      let fileUrl = new URL(
        `/download/${owner ? owner : this.active.id}/${container}/${file.name}`,
        document.location.origin,
      );
      fileUrl.searchParams.append("project", this.active.id);

      headers[file.name] = {
        header: Uint8Array.from(atob(header), c => c.charCodeAt(0)),
        url: fileUrl.toString(),
        size: file.bytes,
      };
    }

    await signedFetch(
      "DELETE",
      this.$store.state.uploadEndpoint,
      whitelistPath,
      undefined,
      {
        session: upInfo.id,
      },
    );

    if (!this.useServiceWorker) {
      this.downWorker.postMessage({
        command: "addHeaders",
        id: id,
        container: container,
        headers: headers,
      });
    } else {
      navigator.serviceWorker.ready.then((reg) => {
        reg.active.postMessage({
          command: "addHeaders",
          id: id,
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

  cancelUpload(container) {
    this.upWorker.postMessage({ command: "closeWebSocket", container });
    if (DEV) console.log("Close the websocket and cancel current upload");
  }

  cancelDownload() {
    this.downWorker.postMessage({ command: "abort", reason: "cancel" });
    if (DEV) console.log("Cancel direct downloads");
  }

  // Schedule file/files for upload
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
  }

  // Schedule file/files for download
  async addDownload(
    container,
    objects,
    owner = "",
  ) {

    //get random id
    const sessionId = Math.random().toString(36).slice(2, 8);

    let ownerName = "";
    if (owner) {
      let ids = await this.$store.state.client.projectCheckIDs(owner);
      ownerName = ids.name;
    }
    let fileHandle = undefined;
    if (objects.length == 1) {
      // Download directly into the file if available.
      // Otherwise, use streaming + ServiceWorker.
      if (!this.useServiceWorker) {
        // Match the file identifier
        const fident = objects[0].replace(".c4gh", "")
          .match(/(?<!^)\.[^.]{1,}$/g);
        const opts = {
          suggestedName: objects[0].replace(".c4gh", ""),
        };

        if (fident) {
          opts.types = [
            {
              description: "Generic file",
              accept: {
                "application/octet-stream": [fident],
              },
            },
          ];
        }
        fileHandle = await window.showSaveFilePicker(opts);

        this.downWorker.postMessage({
          command: "downloadFile",
          id: sessionId,
          container: container,
          file: objects[0],
          handle: fileHandle,
          owner: owner,
          ownerName: ownerName,
        });
      } else {
        if (DEV) {
          console.log("Instructing ServiceWorker to add a file to downloads.");
        }
        navigator.serviceWorker.ready.then(reg => {
          reg.active.postMessage({
            command: "downloadFile",
            id: sessionId,
            container: container,
            file: objects[0],
            owner: owner,
            ownerName: ownerName,
          });
        });
      }
    } else {
      // Download directly into the archive if available.
      // Otherwise, use streaming + ServiceWorker.
      if (!this.useServiceWorker) {
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
          id: sessionId,
          container: container,
          files: objects.length < 1 ? [] : objects,
          handle: fileHandle,
          owner: owner,
          ownerName: ownerName,
        });
      } else {
        navigator.serviceWorker.ready.then(reg => {
          reg.active.postMessage({
            command: "downloadFiles",
            id: sessionId,
            container: container,
            files: objects.length < 1 ? [] : objects,
            owner: owner,
            ownerName: ownerName,
          });
        });
      }
    }
  }
}
