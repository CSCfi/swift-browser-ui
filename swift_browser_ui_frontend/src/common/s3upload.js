// Functions for handling s3 upload and header worker communication

/*
Upload cache schema:
[bucket]: {
  [key]: {
    size: number,
    isMultipart: bool,
    multipartSession: string,
    f: File,
    finished: bool,
    multipartParts: {
      [orderNumber]: {
        offset: number,
        size: number,
        done: bool,
      }
    }
  }
}
*/

/*
Parts cache schema:
{
  bucket: string,
  key: string,
  secret: Uint8Array,
  orderNumber: number,
  size: number,
  offset: number,
}
*/

import { DEV, timeout } from "./globalFunctions";
import { signedFetch, awsCreateBucket, awsAddBucketCors } from "./api";
import {
  checkBucketAccessible,
  awsCreateMultipartUpload,
  awsCompleteMultipartUpload,
  awsAbortMultipartUpload,
} from "./s3commands";

const MAX_UPLOAD_WORKERS = 8;
const MAX_SIMULTANEOUS_HEADER_UPLOADS = 32;
const FILE_PART_SIZE = 52428800;

export default class S3UploadSocket {
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

    this.inputFiles = {};
    this.outputFiles = {};

    this.uploads = {};
    this.parts = [];
    this.toInit = [];

    this.downloadFinished = true;

    this.totalSize = 0;
    this.totalCompleted = 0;
    this.headersNeeded = 0;
    this.headersAdded = 0;

    this.headerUploads = 0;

    // Initialize the workers.
    // Upload workers will use each available logical thread, maximum
    // of MAX_UPLOAD_WORKERS (Default: 8) threads will be used.
    // One download worker should suffice.
    this.upWorkers = [];
    for (
      let i = 0;
      i < window.navigator.hardwareConcurrency && i < MAX_UPLOAD_WORKERS;
      i++
    ) {
      if (DEV) {
        // Load the workers from frontend work directory when in
        // development mode
        this.upWorkers.push(new Worker("/s3upworker.js"));
      } else {
        // In production workers are defined in the static folder
        this.upWorkers.push(new Worker("/static/s3upworker.js"));
      }
    }
    if (DEV) {
      console.log(`${this.upWorkers.length} upload worker threads were created`);
      console.log(this.upWorkers);
    }

    // Initialize the header worker
    if (DEV) {
      // Load the workers from frontend work directory when in
      // development mode
      this.headerWorker = new Worker("/s3headerworker.js");
    } else {
      // In production the worker is defined in the static folder
      this.headerWorker = new Worker("/static/s3headerworker.js");
    }

    let headerWorkerHandler = (e) => {
      switch(e.data.eventType) {
        case "headerDone":
          if (DEV) console.log("File header done");
          this.processFile(
            e.data.bucket, e.data.key, e.data.header, e.data.secret,
          ).then(() => {
            if (DEV) console.log(`Initialized file ${e.data.bucket}/${e.data.key}`);
          });
          break;
      }
    };
    this.headerWorker.onmessage = headerWorkerHandler;

    this.toastMessage = {
      duration: 6000,
      persistent: false,
      progress: false,
    };

    // Create message handlers for upload and download workers
    for (const worker of this.upWorkers) {
      worker.onmessage = this.getUploadWorkerHandler(worker);
    }

    for (const worker of this.upWorkers) {
      worker.postMessage({
        command: "createS3Client",
        access: this.s3access,
        secret: this.s3secret,
        endpoint: this.s3endpoint,
      });
    }
  }

  getUploadWorkerHandler(worker) {
    return (e) => {
      switch(e.data.eventType) {
        case "uploadPartComplete":
          if (DEV) {
            console.log(
              `A segment for ${e.data.bucket}/${e.data.key} was finished.`,
            );
          }
          if (this.uploads[e.data.bucket][e.data.key].isMultipart) {
            if (DEV) {
              console.log(
                `Multipart chunk ${e.data.orderNumber} for object ${e.data.key} was completed. ETag was ${e.data.ETag}`,
              );
            }

            this.uploads[e.data.bucket][e.data.key].multipartParts[e.data.orderNumber].ETag =
            e.data.ETag;
            this.uploads[e.data.bucket][e.data.key].multipartParts[e.data.orderNumber].done = true;

            this.checkFinishedFile(e.data.bucket, e.data.key).then(() => {
              if (DEV) console.log(`Checked if file ${e.data.bucket}/${e.data.key} is finished.`);
            });
          } else {
            if (DEV) {
              console.log(`Flagging regular object ${e.data.bucket}/${e.data.key} as finished.`);
            }
            this.uploads[e.data.bucket][e.data.key].finished = true;
          }

          // Schedule next part if there's more to process,
          // otherwise check if we're done.
          if (this.parts.length > 0) {
            if (DEV) console.log("Sending next part to worker.");
            this.getNextPart(worker);
          } else {
            this.checkFinished().then(
              () => {
                if (DEV) console.log("Checked if all the parts are finished.");
              },
            );
          }
          break;
        case "filesAdded":
          if (DEV) console.log("Files added to WorkerFS");
          break;
        case "progress":
          if (DEV) console.log(`Incrementing completed amount by ${e.data.amount}`);
          this.totalCompleted += e.data.amount;
          this.updateProgress();
          break;
        case "filesRemoved":
          if (DEV) console.log("File handles closed in the WorkerFS");
          break;
        case "s3ClientCreated":
          if (DEV) console.log("Worker created an S3 client session.");
          break;
      }
    };
  }

  // Wrapper for updating upload progress
  updateProgress() {
    if (DEV) {
      `Updating progress to ${this.totalCompleted / this.totalSize}`;
    }

    this.$store.commit("updateProgress", this.totalCompleted / this.totalSize);
  }

  // Check if all the parts are done
  async checkFinished() {
    let finished = true;
    for (const bucket of Object.keys(this.uploads)) {
      for (const key of Object.keys(this.uploads[bucket])) {
        if (!this.uploads[bucket][key].finished) {
          finished = false;
          break;
        }
      }
    }

    if (finished) {
      if (DEV) {
        console.log("Upload has finished.");
      }
      this.finalizeUpload();
    }
  }

  async checkFinishedFile(bucket, key) {
    let finished = true;
    for (const part of Object.keys(this.uploads[bucket][key].multipartParts)) {
      if (!this.uploads[bucket][key].multipartParts[part].done) {
        finished = false;
        break;
      }
    }

    if (finished) {
      if (DEV) console.log(`File ${bucket}/${key} is finished, completing multipart.`);
      this.uploads[bucket][key].finished = true;

      let parts = [];
      for (const entry of Object.entries(
        this.uploads[bucket][key].multipartParts,
      )) {
        parts.push({
          PartNumber: Number(entry[0]),
          ETag: entry[1].ETag.replaceAll("\"", ""),
        });
      }

      const response = await awsCompleteMultipartUpload(
        bucket,
        key.concat(".c4gh"),
        parts,
        this.uploads[bucket][key].multipartSession,
      );
      if (DEV) {
        console.log(`Got following response when completing multipart upload ${this.uploads[bucket][key]}: ${response}`);
      }
    }
  }

  async getNextPart(worker) {
    let nextPart = this.parts.pop();

    if (nextPart === undefined) {
      return;
    }

    this.$store.commit("setEncryptedFile", nextPart.key);

    if (this.uploads[nextPart.bucket][nextPart.key].multipartKeyPending){
      while (
        this.uploads[nextPart.bucket][nextPart.key].multipartSession === ""
      ) {
        await timeout(250);
      }
    }

    if (
      this.uploads[nextPart.bucket][nextPart.key].isMultipart
      && this.uploads[nextPart.bucket][nextPart.key].multipartSession === ""
    ) {
      this.uploads[nextPart.bucket][nextPart.key].multipartKeyPending = true;

      const response = await awsCreateMultipartUpload(
        nextPart.bucket,
        nextPart.key.concat(".c4gh"),
        "bucket-owner-full-control",
      );

      this.uploads[nextPart.bucket][nextPart.key].multipartSession = response.UploadId;

      if (DEV) {
        console.log(`Starting upload for ${nextPart.bucket}/${nextPart.key} with upload id ${response.UploadId}`);
      }
    }
    worker.postMessage({
      command: "nextPart",
      part: nextPart,
      session: this.uploads[nextPart.bucket][nextPart.key].multipartSession,
    });
  }

  // Start the parts queue consumption
  async beginUpload() {
    for (const worker of this.upWorkers) {
      await this.getNextPart(worker);
    }
  }

  // Process a file header to begin uploading
  async processFile(bucket, key, header, secret) {
    if (this.uploads[bucket][key].isMultipart) {
      let partsTotal = Math.floor(
        this.uploads[bucket][key].size / FILE_PART_SIZE,
      );
      let finalPart = this.uploads[bucket][key].size % FILE_PART_SIZE;

      for (let i = 0; i < partsTotal; i++) {
        this.parts.push({
          bucket: bucket,
          key: key,
          secret: secret,
          orderNumber: i + 1,
          size: FILE_PART_SIZE,
          offset: i * FILE_PART_SIZE,
        });
        this.uploads[bucket][key].multipartParts[i + 1] = {
          offset: i * FILE_PART_SIZE,
          size: FILE_PART_SIZE,
          done: false,
        };
      }

      if (finalPart > 0) {
        this.parts.push({
          bucket: bucket,
          key: key,
          secret: secret,
          orderNumber: partsTotal + 1,
          size: finalPart,
          offset: partsTotal * FILE_PART_SIZE,
        });
        this.uploads[bucket][key].multipartParts[partsTotal + 1] = {
          offset: partsTotal * FILE_PART_SIZE,
          size: finalPart,
          done: false,
        };
      }
    } else {
      this.parts.push({
        bucket: bucket,
        key: key,
        secret: secret,
        orderNumber: 0,
        size: this.uploads[bucket][key].size,
        offset: 0,
      });
    }

    if (DEV) console.log(`Header for ${bucket}/${key}: ${header}`);

    // Throttle header pushes to stay under fetch pending request limit
    while (this.headerUploads >= MAX_SIMULTANEOUS_HEADER_UPLOADS) {
      // Wait for a random amount of ms to stagger header upload waits
      await timeout(Math.floor(1 + Math.random() * 100));
    }

    this.headerUploads++;

    if (DEV && this.uploads[bucket][key].ownerName) {
      console.log(`Shared upload, using ${this.uploads[bucket][key].ownerName} as owner.`);
    }

    // Push header to Vault
    let headerBase = this.$store.state.uploadEndpoint;
    let headerPath = `/header/${this.project}/${bucket}/${key}.c4gh`;
    await signedFetch(
      "PUT",
      headerBase,
      headerPath,
      header,
      this.uploads[bucket][key].ownerName
        ? {owner: this.uploads[bucket][key].ownerName}
        : undefined,
    );

    this.headerUploads--;
    this.headersAdded++;

    if (this.headersNeeded == this.headersAdded) {
      if (DEV) console.log("All headers are done, starting upload");
      this.headersAdded = 0;
      this.headersNeeded = 0;
      this.$store.commit("updateProgress", 0);
      this.beginUpload().then(() => {
        if (DEV) console.log("Upload started successfully.");
      });
    }
  }

  // Add files for encrypted upload
  async addEncryptedUploads(bucket, files, receivers, ownerName) {
    // If the upload is already defined, we're adding files to an ongoing
    // upload – no need to check existence or initialization.
    if (this.uploads[bucket] === undefined) {
      // Check that the bucket exists and can be accessed
      const accessible = await checkBucketAccessible(bucket);
      if (!accessible) {
        // If there's no metadata, we're likely running into a CORS
        // error. It may mean that the bucket doesn't exist, or that
        // the bucket CORS doesn't exist. Let's try implicitly creating
        // the bucket, and fixing CORS if that doesn't help.
        try {
          let resp = await awsCreateBucket(this.active, bucket);
          switch (resp) {
            case 400:
              if (DEV) {
                console.log(`Couldn't create bucket ${bucket} due to a client error.`);
              }
              return;
            case 403:
              if (DEV) {
                console.log(
                  `Couldn't create bucket ${bucket} due to it being forbidden.`,
                );
                console.log(
                  "The bucket is probably owned by some other project.",
                );
              }
              return;
          }
        } catch (e) {
          if (DEV) console.log("Coudln't start upload, reason: ", e);
          return;
        }

        // After creating the bucket, ensure we have CORS access
        try {
          await awsAddBucketCors(this.active, bucket);
        } catch (e) {
          if (DEV) {
            console.error(`Couldn't add CORS for bucket ${bucket}`);
          }
          return;
        }
      }

      this.uploads[bucket] = {};
    }
    this.headersNeeded = files.length;

    if (DEV) console.log("Adding the listed files to the worker filesystems.");
    for (const worker of this.upWorkers) {
      if (DEV) console.log(worker);
      worker.postMessage({
        command: "mountFiles",
        bucket: bucket,
        files: files,
      });
    }

    this.$store.commit("setEncryptedFile", "file pending...");

    for (const file of files) {
      if (DEV) console.log(`Adding file ${file.relativePath}`);
      this.uploads[bucket][file.relativePath] = {
        size: file.size,
        isMultipart: file.size > 100 * 1024 * 1024,
        multipartSession: "",
        multipartKeyPending: false,
        multipartParts: {},
        finished: false,
        f: file,
        ownerName: ownerName,
      };

      if (DEV) console.log(this.uploads[bucket][file.relativePath]);

      this.headerWorker.postMessage({
        command: "createHeader",
        bucket: bucket,
        key: file.relativePath,
        receivers: receivers,
        // file: this.uploads[bucket][file.relativePath],
      });

      this.totalSize += file.size;
    }
    if (DEV) console.log(`Scheduled files for uploading in bucket ${bucket}`);
    this.$store.commit("eraseProgress");
    this.$store.commit("setUploading");
  }

  // Cancel the ongoing upload in bucket
  async cancelUpload(bucket) {
    // Remove the ongoing parts in bucket
    this.parts = this.parts.filter(part => part.bucket == bucket);

    // Cancel each file that's being uploaded
    if (DEV) console.log(`Terminating uploads in ${bucket}`);
    for (const key in this.uploads[bucket]) {
      // Cancel the multipart process
      await awsAbortMultipartUpload(
        bucket,
        key.concat(".c4gh"),
        this.uploads[bucket][key].multipartSession,
      ).catch((err) => {
        if (DEV) {
          console.log("Failed to abort multipart on cancel.");
          console.log(err);
        }
      });
    }
    this.finalizeUpload();
  }

  finalizeUpload() {
    if (DEV) console.log("Erasing files from storage");
    for (const worker of this.upWorkers) {
      for (const bucket of Object.keys(this.uploads)) {
        this.uploads[bucket] = {};
        worker.postMessage({ command: "uploadFinished", bucket: bucket });
      }
    }
    this.$store.commit("eraseDropFiles");
    this.$store.commit("stopUploading");
    this.$store.commit("setEncryptedFile", "");
    this.$store.commit("eraseProgress");
  }
}
