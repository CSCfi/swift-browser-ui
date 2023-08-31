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

let uploads = {};
let socket = undefined;

let totalLeft = 0;
let totalDone = 0;
let totalFiles = 0;
let progressInterval = undefined;

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
    console.log(receiver);
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

  console.log(receiversLen);

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
    [header]
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

  async getSliceFromStream() {
    let enChunk = new Uint8Array(65536);
    this.bytes = 0;

    while (!this.done) {
      this.remainder = 65536 - this.bytes;
      let toSet = this.chunk.subarray(this.offset, this.offset + this.remainder);
      enChunk.set(toSet, this.bytes);
      this.bytes += toSet.length;

      if (this.chunk.length - this.offset > this.remainder) {
        this.offset += this.remainder;
        this.totalBytes += 65564;
        return enChunk;
      } else {
        this.offset = 0;
        ({ value: this.chunk, done: this.done } = await this.reader.read());
      }
    }

    if (this.chunk !== undefined) {
      let toSet = this.chunk.subarray(this.offset);
      enChunk.set(toSet, this.bytes);
      this.bytes += toSet.length;
      this.totalBytes += toSet.length - 28;
    }

    if (this.bytes > 0) {
      return enChunk.slice(0, this.bytes);
    }

    return undefined
  }

  async getChunk(iter) {
    let enChunk = await this.file.slice(iter * 65536, iter * 65536 + 65536);

    if (enChunk === undefined || enChunk.length === 0 || enChunk.size === 0) {
      clearInterval(this.interval);
      return;
    }

    let enBuffer = await enChunk.arrayBuffer();

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

    socket.send(msg);
  }

  async nextChunk () {
    let iter = this.iter;
    this.iter++;
    totalDone += 65536;
    return await this.getChunk(iter);
  }

  retryChunk(iter) {
    this.getChunk(iter).then(() => {
      console.log(`Retried chunk ${iter}.`);
    })
  }

  sendFile() {
    console.log("Slicer started.");
    console.log(this.file);
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
    console.log("File finished.");
    let msg = msgpack.serialize({
      command: "finish",
      container: this.container,
      object: this.path,
    });
    socket.send(msg);
  }
}

// Safely free and remove an upload session
function finishUploadSession(container) {
  return;
}


// Open the websocket for communicating with the runner
async function openWebSocket (
  upinfo,
) {
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
        console.log("File aborted");
        console.log(msg_data);
        postMessage({
          eventType: "abort",
          container: msg_data.container,
          object: msg_data.object,
          reason: msg_data.reason,
        });
        break;
      // A file was successfully uploaded
      case "success":
        console.log("File successful");
        console.log(msg_data);
        uploads[msg_data.container].files[msg_data.object].slicer.finishFile();
        postMessage({
          eventType: "success",
          container: msg_data.container,
          object: msg_data.object,
        });
        break;
      // Push the next chunk to the websocket
      case "start_upload":
        console.log("Upload started");
        console.log(msg_data);
        console.log(uploads);
        uploads[msg_data.container].files[msg_data.object].slicer.sendFile();
        break;
      // Retry a chunk in the websocket
      case "retry_chunk":
        console.log("Retrying chunk");
        console.log(msg_data);
        uploads[msg_data.container].files[msg_data.object].slicer.retryChunk(msg_data.order);
        break;
    }
  }

  setTimeout(() => {
    Module.ccall("libinit", undefined, undefined, undefined);
  }, 2000);
}

/*
Add a batch of files to the current upload session.
*/
function addFiles(files, container) {
  console.log(files);
  for (const file of files) {
    console.log(file);

    let handle = file.file;

    let path = `${file.relativePath}.c4gh`
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
    let chunks = []
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
    }

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

    // Upload the file header
    socket.send(msgpack.serialize(msg));
  }

  // Create an interval for updating progress
  progressInterval = setInterval(() => {
    if (totalDone == totalLeft) {
      postMessage({
        eventType: "finish",
        container: container,
      });
      totalDone = 0;
      totalLeft = 0;
      totalFiles = 0;
    } else {
      postMessage({
        eventType: "progress",
        totalFiles: totalFiles,
        progress: totalDone / totalLeft,
      });
    }
  }, 250);
}

self.addEventListener("message", (e) => {
  e.stopImmediatePropagation();

  switch(e.data.command) {
    // Create a new upload session with provided files
    case "addFiles":
      // Create new upload session if it doesn't already exist
      if (uploads[e.data.container] === undefined) {
        createUploadSession(
          e.data.container,
          e.data.receivers,
          e.data.projectName,
        );
      }

      if (e.data.owner !== "") {
        uploads[container].owner = e.data.owner;
      }
      if (e.data.ownerName !== "") {
        uploads[container].ownerName = e.data.ownerName;
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
      openWebSocket(e.data.upinfo);
      postMessage({
        eventType: "webSocketOpened",
      })
    case "abortUpload":
      finishUploadSession(e.data.container);
      break;
  }
})

export var uploadRuntime = Module;
export var uploadFileSystem = FS;
