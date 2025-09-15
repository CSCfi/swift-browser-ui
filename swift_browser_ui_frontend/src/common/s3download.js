// Functions for handling s3 download worker communication

/*
Download file list:
{
    bucket: string,
    key: string,
    header: string,
    orderNumber: number,
    size: number,
    uuid: string,  // Unique identifier for the download session
}

The download will be finished after all list elements have been shifted
and consumed.
*/

import {
  timeout,
} from "./globalFunctions";
import {
  getUploadEndpoint,
  signedFetch,
} from "./api";
import { DEV } from "./conv";

// Use 50 MiB as download slice size
const FILE_PART_SIZE = 52428800;

export default class S3DownloadSocket {
  constructor(
    active, // project id
    project = "", // project name
    store, // shared vuex store
    t, // i18n bindings
    s3access,
    s3secret,
    s3endpoint,
  ) {
    this.active = active;
    this.project = project;
    this.$store = store;
    this.$t = t;
    this.s3access = s3access;
    this.s3secret = s3secret;
    this.s3endpoint = s3endpoint;

    this.downloadFinished = true;
    this.totalSize = 0;
    this.totalCompleted = 0;

    this.useServiceWorker = "serviceWorker" in navigator
      && window.showSaveFilePicker === undefined;
    if (this.useServiceWorker) {
      if (DEV) console.log("Registering download script as service worker");
      let workerUrl = new URL("/s3downworker.js", document.location.origin);
      navigator.serviceWorker.register(workerUrl).then(reg => {
        reg.update();
      }).catch((err) => {
        if (DEV) console.log("Failed to register the service worker.");
        if (DEV) console.log(err);
      });
      this.downWorker = undefined;
    } else if (window.showSaveFilePicker !== undefined) {
      this.downWorker = new Worker("/s3downworker.js");
      if (DEV) {
        console.log("Created a conventional worker for downloads.");
      }
    } else {
      if (DEV) console.log("Could not register a worker for download.");
      if (DEV) console.log("Decrypted downloads are not available.");
    }

    this.toastMessage = {
      duration: 6000,
      persistent: false,
      progress: false,
    };

    // Add message handler for the download worker
    let handleDownloadWorker = (e) => {
      switch(e.data.eventType) {
        case "getHeaders":
          if (this.$store.state.downloadCount >= 0) {
            this.$store.commit("eraseDownloadProgress");
            this.$store.commit("addDownload");
            this.getHeaders(
              e.data.id,
              e.data.bucket,
              e.data.files,
              e.data.pubkey,
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
                  `Got headers for download in bucket ${e.data.bucket}`,
                );
              }
            }).catch(() => {
              this.downWorker.postMessage({
                command: "abort",
                reason: "error",
              });
            });
          }
          break;
        case "downloadStarted":
          if (DEV) console.log(`Started download in ${e.data.bucket}`);
          if (this.useServiceWorker) {
            this.downloadFinished = false;
            if (e.data.archive) {
              let downloadUrl = new URL(
                `/archive/${e.data.uuid}7${e.data.bucket}.tar`,
                document.location.origin,
              );
            } else {
              let downloadUrl = new URL(
                `/file/${e.data.id}/${e.data.bucket}/${e.data.key}`,
                document.location.origin,
              );
            }
            if(DEV) console.log(downloadUrl);
            window.open(downloadUrl, "_blank");
          }
          break;
        case "downloadProgressing":
          if (this.useServiceWorker) {
            navigator.serviceWorker.ready.then(async(reg) => {
              while (!this.downloadFinished) {
                // Keep the service worker awake while downloading
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
            console.log(`Could not decrypt all files in bucket ${e.data.bucket}`);
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
              `Finished a download in bucket ${e.data.bucket}`,
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

    this.handleDownloadWorker = handleDownloadWorker;

    if (this.useServiceWorker) {
      navigator.serviceWorker.addEventListener(
        "message",
        handleDownloadWorker,
      );
    } else if (window.showSaveFilePicker !== undefined) {
      this.downWorker.onmessage = handleDownWorker;
    }

    // Initialize the S3 client
    if (this.useServiceWorker) {
      navigator.serviceWorker.ready.then((reg) => {
        reg.active.postMessage({
          command: "createS3Client",
          access: this.s3access,
          secret: this.s3secret,
          endpoint: this.s3endpoint,
        });
      });
    } else if (window.showSaveFilePicker !== undefined) {
      this.downWorker.postMessage({
        command: "createS3Client",
        access: this.s3access,
        secret: this.s3secret,
        endpoint: this.s3endpoint,
      });
    }
  }

  async getHeaders(uuid, bucket, fileList, pubkey, ownerName) {
    let headers = {};

    // Cache the bucket id
    let dbBucket = await getDB().containers
      .get({
        projectID: this.active.id,
        name: bucket,
      });

    const dbBucketFileCount = await getDB().objects
      .where({"containerID": dbContainer.id})
      .count();

    let dbBucketFiles = [];

    while (dbBucketFiles.length < dbBucketFileCount
      || dbBucketFiles.length < dbBucket.count)
    {
      dbBucketFiles = await getDB().objects
        .where({"containerID": dbBucket.id})
        .toArray();
      await timeout(250);
    }

    // If files are specified, use only the specified file listing
    if (fileList.length >= 1) {
      dbBucketFiles = dbBucketFiles.filter(
        item => fileList.includes(item.name),
      );
    }

    let whitelistPath = `/cryptic/${this.active.name}/whitelist`;
    let upInfo = await getUploadEndpoint(
      this.active.id,
      this.project,
      bucket,
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

    for (const file of dbBucketFiles) {
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

      headers[file.name] = {
        header: Uint8Array.from(atob(header), c => c,charCodeAt(0)),
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
        id: uuid,
        bucket: bucket,
        headers: headers,
      });
    } else {
      navigator.serviceWorker.ready.then(reg => {
        reg.active.postMessage({
          command: "addHeaders",
          id: uuid,
          bucket: bucket,
          headers: headers,
        });
      });
    }
  }

  cancelDownload() {
    this.downWorker.postMessage({ command: "abort", reason: "cancel" });
    if (DEV) console.log("Cancel direct downloads");
  }

  async addDownload(
    bucket,
    objects,
    owner = "",
    test = false,
  ) {
    // get random id
    const sessionId = window.crypto.randomUUID();

    let ownerName = "";
    if (owner) {
      let ids = await this.$store.state.client.projectCheckIDs(owner);
      ownerName = ids.name;
    }

    let fileList = this.getFileListWithHeaders(bucket, objects, owner);

    let fileHandle = undefined;
    if (objects.length == 1) {
      // Download directly into the file if available.
      // Otherwise, use streaming + ServiceWorker
      if (!this.useServiceWorker) {
        const fileName = objects[0].replace(".c4gh", "");

        if (test) {
          // OPFS root for direct download e2e testing
          const testDirHandle = await navigator.storage.getDirectory();
          fileHandle =
            await testDirHandle.getFileHandle(fileName, { create: true });
        } else {
          // Match the file identifier
          const fident = objects[0].replace(".c4gh", "")
            .match(/(?<!^)\.[^.]{1,}$/g);
          const opts = {
            suggestedName: fileName,
          };

          if (fident) {
            opts.types = [
              {
                description: "Genericc file",
                accept: {
                  "application/octet-stream": [fident],
                },
              },
            ];
          }
          fileHandle = await window.showSaveFilePicker(opts);
        }
        this.downWorker.postMessage({
          command: "downloadFile",
          id: sessionId,
          bucket: bucket,
          file: objects[0],
          handle: fileHandle,
          owner: owner,
          ownerName: ownerName,
          test: test,
        });
      } else {
        if (DEV) {
          console.log(
            "Instructing ServiceWorker to add a file to the downloads.",
          );
        }
        navigator.serviceWorker.ready.then(reg => {
          reg.active.postMessage({
            command: "downloadFile",
            id: sessionId,
            bucket: bucket,
            file: objects[0],
            owner: owner,
            ownerName: ownerName,
          });
        });
      }
    } else {
      // Download directly into the archive if available.
      // Otherwise stream the download via ServiceWorker.
      if (!this.useServiceWorker) {
        const fileName = `${bucket}_download.tar`;
        if (test) {
          // OPFS root for direct download e2e testing
          const testDirHandle = await navigator.storage.getDirectory();
          fileHandle =
            await testDirHandle.getFileHandle(fileName, { create: true });
        } else {
          fileHandle = await window.showSaveFilePicker({
            suggestedName: fileName,
            types: [
              {
                description: "Tar archive (uncompressed)",
                accept: {
                  "application/x-tar": [".tar"],
                },
              },
            ],
          });
        }
        this.downWorker.postMessage({
          command: "downloadFiles",
          id: sessionId,
          bucket: bucket,
          files: objects.length < 1 ? [] : objects,
          handle: fileHandle,
          owner: owner,
          ownerName: ownerName,
          test: test,
        });
      } else {
        navigator.serviceWorker.ready.then(reg => {
          reg.active.postMessage({
            command: "downloadFiles",
            id: sessionId,
            bucket: bucket,
            files: objects.length < 1 ? [] : objects,
            owner: owner,
            ownerName: ownerName,
          });
        });
      }
    }
  }
}
