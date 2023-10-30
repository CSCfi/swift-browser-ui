// Worker script for upload chunks

/*
Schema for storing the upload information:
{
  "containerName": {  // Container level session for the upload
    receivers: int;  // pointer to the receiver public key list (see uptypes.h)
    receiversLen: int;  // The amount of receivers listed
    files: {  // Files to upload, stored in an object
      "filePath": int;  // pointer to the unique session key (see uptypes.h)
      ...
      path_n: int;
    }
  }
}
*/
import msgpack from "@ygoe/msgpack";
import { checkPollutingName } from "./nameCheck";

let uploads = {};
let upinfo = undefined;
let socket = undefined;

let totalLeft = 0;
let totalDone = 0;
let totalFiles = 0;
let doneFiles = 0;
let progressInterval = undefined;
let uploadCount = 0;
let uploadCancelled = false;

// Create an upload session
function createUploadSession(container, receivers, projectName) {
  // Add the receiver public key files to the filesystem'
  // Use a temporary folder path unique enough to not cause a collision
  let tmpdirpath = `${container}_receivers_`
    + Math.random().toString(36)
    + Math.random().toString(36);
  FS.mkdir(tmpdirpath);
  let files = [];
  for (const receiver of receivers) {
    files.push(`${tmpdirpath}/pubkey_${receivers.indexOf(receiver).toString()}`);
    FS.writeFile(
      `${tmpdirpath}/pubkey_${receivers.indexOf(receiver).toString()}`,
      receiver,
    );
  }

  // Read and parse the receiver keys
  let receiversStructPtr = Module.ccall(
    "read_in_recv_keys_path",
    "number",
    ["string"],
    [tmpdirpath],
  );
  let receiversPtr = Module.ccall(
    "wrap_chunk_content",
    "number",
    ["number"],
    [receiversStructPtr],
  );
  let receiversLen = Module.ccall(
    "wrap_chunk_len",
    "number",
    ["number"],
    [receiversStructPtr],
  );

  for (const file of files) {
    FS.unlink(file);
  }
  FS.rmdir(tmpdirpath);

  // Store the upload session
  uploads[container] = {
    files: {},
    done_files: {},
    projectName: projectName,
    receivers: receiversPtr,
    receiversLen: receiversLen,
    owner: "",
    ownerName: "",
  };
}


// Add a file to the upload session
function createUploadSessionFile(container, path) {
  // We'll need an ephemeral keypair for the upload
  let keypairPtr = Module.ccall(
    "create_keypair",
    "number",
    [],
    [],
  );
  // We'll also need a session key for encryption
  let sessionKeyPtr = Module.ccall(
    "create_session_key",
    "number",
    [],
    [],
  );

  uploads[container].files[path].sessionkey = sessionKeyPtr;

  // We won't need anything else besides the private key for the header build
  let privateKeyPtr = Module.ccall(
    "get_keypair_private_key",
    "number",
    ["number"],
    [keypairPtr],
  );

  // Build the header using the keypair, session receivers and the file session key
  let header = Module.ccall(
    "create_crypt4gh_header",
    "number",
    ["number", "number", "number", "number"],
    [
      sessionKeyPtr,
      privateKeyPtr,
      uploads[container].receivers,
      uploads[container].receiversLen,
    ],
  );
  let headerPtr = Module.ccall(
    "wrap_chunk_content",
    "number",
    ["number"],
    [header],
  );
  let headerLen = Module.ccall(
    "wrap_chunk_len",
    "number",
    ["number"],
    [header],
  );

  // Create a new array from view, as views get stale as memory gets managed
  let headerView = new Uint8Array(HEAPU8.subarray(headerPtr, headerPtr + headerLen));

  Module.ccall(
    "free_chunk",
    "number",
    ["number"],
    [header],
  );
  // The keypair is not needed for upload after this, so it can be ditched
  Module.ccall(
    "free_keypair",
    undefined,
    "number",
    [keypairPtr],
  );

  uploads[container].files[path].header = headerView;
}


// Encrypt a single chunk of an upload
function encryptChunk(container, path, deChunk) {
  let chunk = Module.ccall(
    "encrypt_chunk",
    "number",
    ["number", "array", "number"],
    [
      uploads[container].files[path].sessionkey,
      deChunk,
      deChunk.length,
    ],
  );
  let chunkPtr = Module.ccall(
    "wrap_chunk_content",
    "number",
    ["number"],
    [chunk],
  );
  let chunkLen = Module.ccall(
    "wrap_chunk_len",
    "number",
    ["number"],
    [chunk],
  );

  // As above, need a new array from view as it will get stale
  let ret = new Uint8Array(HEAPU8.subarray(chunkPtr, chunkPtr + chunkLen));

  Module.ccall(
    "free_chunk",
    "number",
    ["number"],
    [chunk],
  );

  return ret;
}

class StreamSlicer{
  constructor(
    input,
    container,
    path,
  ) {
    this.file = input;
    this.container = container;
    this.path = path;
    this.chunk = undefined;
    this.done = false;
    this.offset = 0;
    this.remainder = 0;
    this.bytes = 0;
    this.totalBytes = 0;
    this.iter = 0;
    this.interval = undefined;

    this.reader = this.file.stream();
  }

  async getStart() {
    ({ value: this.chunk, done: this.done } = await this.reader.read());
  }

  async getChunk(iter) {
    let enChunk = await this.file.slice(iter * 65536, iter * 65536 + 65536);

    if (enChunk === undefined || enChunk.length === 0 || enChunk.size === 0
      || uploadCancelled
    ) {
      clearInterval(this.interval);
      if (uploadCancelled) uploadCount = 0;
      return;
    }

    let enBuffer = await enChunk.arrayBuffer();

    if (uploads[this.container]) {
      let enData = encryptChunk(
        this.container,
        this.path,
        new Uint8Array(enBuffer),
      );


      let msg = msgpack.serialize({
        command: "add_chunk",
        container: this.container,
        object: this.path,
        order: iter,
        data: enData,
      });

      if (socket.readyState === 1) {
        socket.send(msg);
      }
    }
  }

  async nextChunk () {
    let iter = this.iter;
    this.iter++;
    totalDone += 65536;
    return await this.getChunk(iter);
  }

  retryChunk(iter) {
    this.getChunk(iter).then(() => {});
  }

  async sendFile() {
    // Uploads need to be throttled a bit, without throttling
    // upload doesn't progress fast enough to keep the upload
    // connection open.
    while (uploadCount > 4) {
      await timeout(250);
    }
    uploadCount++;
    this.interval = setInterval(() => {
      if (socket.bufferedAmount < 5242880) {
        this.nextChunk().then(() => {});
      }
    }, 1);
    // Update the frontend with the active file.
    postMessage({
      eventType: "activeFile",
      object: this.file.name,
    });
  }

  finishFile() {
    let msg = msgpack.serialize({
      command: "finish",
      container: this.container,
      object: this.path,
    });
    socket.send(msg);
    uploadCount--;
    doneFiles++;
    Module.ccall(
      "free_crypt4gh_session_key",
      undefined,
      ["number"],
      [uploads[this.container].files[this.path].sessionkey],
    );
  }
}

// Safely free and remove an upload session
function finishUploadSession(container) {
  _free(uploads[container].receivers);
  delete uploads[container];
  return;
}


// Open the websocket for communicating with the runner
async function openWebSocket (
  upinfo,
) {
  // Skip socket initialization if the socket is connecting or open
  if (socket !== undefined) {
    if (socket.readyState === 0 || socket.readyState === 1) {
      return;
    }
  }

  let socketURL = new URL(upinfo.wsurl);
  socketURL.searchParams.append(
    "session",
    upinfo.id,
  );
  socketURL.searchParams.append(
    "valid",
    upinfo.wssignature.valid,
  );
  socketURL.searchParams.append(
    "signature",
    upinfo.wssignature.signature,
  );

  socket = new WebSocket(socketURL);
  socket.binaryType = "arraybuffer";

  socket.onmessage = msg => {
    let msg_data = msgpack.deserialize(msg.data);

    switch (msg_data.command) {
      // Abort the upload
      case "abort":
        socket.close();
        doneFiles = 0;
        totalFiles = 0;
        uploadCount = 0;
        postMessage({
          eventType: "abort",
          container: msg_data.container,
          object: msg_data.object,
          reason: msg_data.reason,
        });
        break;
      // A file was successfully uploaded
      case "success":
        if(!uploadCancelled) {
          uploads[msg_data.container].files[msg_data.object].slicer.finishFile();
          postMessage({
            eventType: "success",
            container: msg_data.container,
            object: msg_data.object,
          });
        }
        break;
      // Push the next chunk to the websocket
      case "start_upload":
        if(!uploadCancelled) {
          uploads[msg_data.container].files[msg_data.object].slicer.sendFile().then(
            () => {},
          );
        }
        break;
      // Retry a chunk in the websocket
      case "retry_chunk":
        if(!uploadCancelled) {
          uploads[msg_data.container].files[msg_data.object].slicer.retryChunk(msg_data.order);
        }
        break;
    }
  };

  await waitAsm();
  Module.ccall("libinit", undefined, undefined, undefined);
}

/*
Add a batch of files to the current upload session.
*/
async function addFiles(files, container) {
  for (const file of files) {
    let handle = file.file;

    if (checkPollutingName(file.relativePath)) return;

    let path = `${file.relativePath}.c4gh`;
    let totalBytes = Math.floor(handle.size / 65536) * 65564;
    let totalChunks = Math.floor(handle.size / 65536);

    // Add the last block to total bytes and total chunks in case it exists
    if (handle.size % 65536 > 0) {
      totalBytes += handle.size % 65536 + 28;
      totalChunks++;
    }

    totalLeft += handle.size;
    totalFiles++;

    // Add the chunks that need to be uploaded
    let chunks = [];
    for (let i = 0; i < totalChunks; i++) {
      chunks.push(i);
    }

    // Add the file to the upload session
    uploads[container].files[path] = {
      totalBytes: totalBytes,
      currentByte: 0,
      totalChunks: totalChunks,
      totalUploadedChunks: 0,
      chunks: chunks,
      file: handle,
      slicer: new StreamSlicer(handle, container, path),
    };

    // Create the file header
    createUploadSessionFile(container, path);

    let msg = {
      command: "add_header",
      container: container,
      object: path,
      name: uploads[container].projectName,
      total: totalBytes,
      data: uploads[container].files[path].header,
    };

    if (uploads[container].owner !== "") {
      msg.owner = uploads[container].owner;
    }
    if (uploads[container].ownerName !== "") {
      msg.owner_name = uploads[container].ownerName;
    }

    while (socket.readyState !== 1 && !uploadCancelled) {
      await timeout(250);
      // Ensure the websocket has stayed open
      openWebSocket(upinfo);
    }
    if (socket.readyState === 1) {
      // Upload the file header
      socket.send(msgpack.serialize(msg));
    }
  }

  // Create an interval for updating progress
  progressInterval = setInterval(() => {
    if (doneFiles >= totalFiles) {
      postMessage({
        eventType: "finished",
        container: container,
      });
      totalDone = 0;
      totalLeft = 0;
      totalFiles = 0;
      doneFiles = 0;
      clearInterval(progressInterval);
    } else {
      postMessage({
        eventType: "progress",
        totalFiles: totalFiles,
        progress: totalDone / totalLeft < 1 ? totalDone / totalLeft : 1,
      });
    }
  }, 250);
}


function closeWebSocket(container) {
  let msg = msgpack.serialize({
    command: "cancel",
  });
  socket.send(msg);
  finishUploadSession(container);
}

self.addEventListener("message", (e) => {
  e.stopImmediatePropagation();

  // Sanity check container name
  if (checkPollutingName(e.data.container)) return;

  switch(e.data.command) {
    // Create a new upload session with provided files
    case "addFiles":
      uploadCancelled = false;
      // Create new upload session if it doesn't already exist
      if (uploads[e.data.container] === undefined) {
        createUploadSession(
          e.data.container,
          e.data.receivers,
          e.data.projectName,
        );
      }

      if (e.data.owner !== "") {
        uploads[e.data.container].owner = e.data.owner;
      }
      if (e.data.ownerName !== "") {
        uploads[e.data.container].ownerName = e.data.ownerName;
      }

      // Add the files in the upload request
      addFiles(e.data.files, e.data.container);

      postMessage({
        eventType: "uploadCreated",
        container: e.data.container,
      });
      break;
    // Abort the upload in question
    case "openWebSocket":
      upinfo = e.data.upinfo;
      openWebSocket(upinfo);
      postMessage({
        eventType: "webSocketOpened",
      });
      break;
    case "closeWebSocket":
      uploadCancelled = true;
      closeWebSocket(e.data.container);
      break;
    case "abortUpload":
      finishUploadSession(e.data.container);
      break;
  }
});

export var uploadRuntime = Module;
export var uploadFileSystem = FS;
