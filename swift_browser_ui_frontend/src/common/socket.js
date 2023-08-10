// Functions for handling interfacing between workers and upload API socket

import { getUploadSocket } from "./api";
import { DEV } from "./conv";


export default class UploadSocket {
  constructor(
    active,
    project = "",
    store,
  ) {
    this.active = active;
    this.project = project;
    this.$store = store;

    // Initialize the workers
    // The workers will handle threading by themselves, to avert
    // blocking the main browser thread
    this.upWorker = new Worker("libupload.js");
    this.downWorker = new Worker("libdownload.js");

    // We'll create a ServiceWorker only if we can't open a file for
    // writing
    if (
      ("serviceWorker") in navigator
      && window.showSaveFilePicker === undefined
    ) {
      let workerUrl = new URL("/aggregatorsw.js", document.location.origin);
      navigator.serviceWorker.register(workerUrl).then(reg => {
        reg.update();
      }).catch((err) => {
        if(DEV) console.log("Failed to register service worker.");
        if(DEV) console.log(err);
      });
    } else {
      if (DEV) console.log("Did not register ServiceWorker.");
    }

    // Add message handlers for upload and download workers
    this.upWorker.onmessage = this.handleUpWorker;
    this.downWorker.onmessage = this.handleDownWorker;

    this.socket = undefined;
  }

  handleUpWorker(e) {
    switch(e.data.eventType) {
      case "uploadCreated":
        if (DEV) console.log(e.data);
        break;
      case "webSocketOpened":
        if (DEV) console.log(e.data);
        break;
      case "progress":
        if (DEV) console.log(e.data);
        break;
      case "abort":
        if (DEV) console.log(e.data);
        break;
      case "success":
        if (DEV) console.log(e.data);
        break;
    }
  }

  handleDownWorker(e) {
    switch(e.data.eventType) {
      case "getHeaders":
        break;
      case "finished":
        console.log("download finished");
        console.log(e.data);
        break;
      case "success":
        console.log("file successfully downloaded");
        console.log(e.data);
        break;
      case "downloadSessionRemoved":
        break;
    }
  }

  // Get the latest upload endpoint
  async updateEndpoint() {
    let upinfo = await getUploadSocket(
      this.active.id,
      this.active.id,
    );

    this.$store.commit("setUploadInfo", upinfo);
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
    this.upWorker.postMessage({
      command: "addFiles",
      container: container,
      receivers: receivers,
      owner: owner,
      ownerName: ownerName,
      files: files,
    });

    if (DEV) console.log("Pushed new files to the service worker.");
  }

  // Schedule file/files for download
  async addDownload(
    container,
    objects,
  ) {
    let fileHandle = undefined;
    if (objects.length == 1) {
      // Download directly into the file if available.
      // Otherwise, use intermediary OPFS + ServiceWorker.
      if (window.showSaveFilePicker !== undefined) {
        // Match the file identifier
        const fident = objects[0].name.replace(".c4gh", "").match(/\.[^.]*$/g);

        fileHandle = await window.showSaveFilePicker({
          types: [
            {
              description: "Generic file",
              accept: {
                "application/octet-stream": [fident],
              },
            },
          ],
        });
      }

      this.downWorker.postMessage({
        command: "downloadFile",
        container: container,
        object: objects[0],
        handle: fileHandle,
      });
    } else {
      // Download directly into the archive if available.
      // Otherwise, use intermediary OPFS + ServiceWorker.
      if (window.showSaveFilePicker !== undefined) {
        fileHandle = await window.showSaveFilePicker({
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
        container: container,
        objects: objects[0],
        headers: undefined,
        handle: fileHandle,
      });
    }
  }
}
