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
          this.$store.commit("eraseNotClosable");
          this.$store.commit("eraseDropFiles");
          this.$store.commit("stopUploading");
          this.$store.commit("eraseProgress");
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
            e.data.owner,
            e.data.ownerName,
          ).then(() => {
            if (DEV) {
              console.log(
                `Got headers for download in container ${e.data.container}`,
              );
            }
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
                `/archive/${e.data.container}.tar`,
                document.location.origin,
              );
              if (DEV) console.log(downloadUrl);
              window.open(downloadUrl, "_blank");
            } else {
              let downloadUrl = new URL(
                `/file/${e.data.container}/${e.data.path}`,
                document.location.origin,
              );
              if (DEV) console.log(downloadUrl);
              window.open(downloadUrl, "_blank");
            }
          } else {
            //show download progress
            if (this.$store.state.downloadCount <= 0) {
              this.$store.commit("eraseDownloadProgress");
            }
            this.$store.commit("toggleDownloadNotification", true);
          }
          this.$store.commit("addDownload");
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
        case "error":
          this.$store.commit("setDownloadError", true);
          if (!this.useServiceWorker) {
            this.$store.commit("toggleDownloadNotification", false);
            this.$store.commit("removeDownload", true);
            this.$store.commit("eraseDownloadProgress");
          } else {
            this.$store.commit("removeDownload");
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
          }
          else {
            this.downloadFinished = true;
          }
          this.$store.commit("removeDownload");
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
  async getHeaders(container, fileList, pubkey, owner, ownerName) {
    let headers = {};

    // If no files are specified, get all files in the container
    let files;
    if (fileList.length < 1) {
      let dbContainer = await getDB().containers
        .get({
          projectID: this.active.id,
          name: container,
        });

      let objects = [];
      while (objects.length < dbContainer.count) {
        await timeout(250);
        objects = await getDB().objects
          .where({"containerID": dbContainer.id})
          .toArray();
      }

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

    for (const file of files) {
      // Get the file header
      let header = await signedFetch(
        "GET",
        this.$store.state.uploadEndpoint,
        `/header/${this.active.name}/${container}/${file}`,
        undefined,
        {
          session: upInfo.id,
          owner: ownerName,
        },
      );
      header = await header.text();

      // Prepare the file URL
      let fileUrl = new URL(
        `/download/${owner ? owner : this.active.id}/${container}/${file}`,
        document.location.origin,
      );
      fileUrl.searchParams.append("project", this.active.id);

      headers[file] = {
        header: Uint8Array.from(atob(header), c => c.charCodeAt(0)),
        url: fileUrl.toString(),
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

  cancelUpload(container) {
    this.upWorker.postMessage({ command: "closeWebSocket", container });
    if (DEV) console.log("Close the websocket and cancel current upload");
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
    owner = "",
  ) {
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
