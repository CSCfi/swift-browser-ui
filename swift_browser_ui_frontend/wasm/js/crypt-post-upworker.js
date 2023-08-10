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
let uploads = {};
let socket = WebScoket;


// Create an upload session
function createUploadSession(container, receivers, projectName) {
  // Add the receiver public key files to the filesystem'
  // Use a temporary folder path unique enough to not cause a collision
  let tmpdirpath = `${container}_receivers_`
    + Math.random().toString(36)
    + Math.random().toString(36);
  FS.mkdir(tmpdirpath);
  for (const receiver of receivers) {
    FS.writeFile(
      `${tmpdirpath}/pubkey_${receivers.indexOf(receiver).toString()}`,
      receiver,
    );
  }

  // Read and parse the receiver keys
  let receiversStructPtr = Module.ccall([
    "read_in_recv_keys_path",
    "number",
    ["string"],
    [tmpdirpath],
  ]);
  let receiversPtr = Module.ccall([
    "wrap_chunk_content",
    "number",
    ["number"],
    [receiversStructPtr],
  ]);
  let receiversLen = Module.ccall([
    "wrap_chunk_len",
    "number",
    ["number"],
    [receiversStructPtr],
  ]);

  // Clean up after reading the receiver list
  Module.ccall([
    "rmrecv",
    "number",
    ["string"],
    [tmpdirpath],
  ]);
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
  let keypairPtr = Module.ccall([
    "create_keypair",
    "number",
    [],
    [],
  ]);
  // We'll also need a session key for encryption
  let sessionKeyPtr = Module.ccall([
    "create_session_key",
    "number",
    [],
    [],
  ]);

  uploads[container].files[path] = {
    sessionKey: sessionKeyPtr,
  };

  // We won't need anything else besides the private key for the header build
  let privateKeyPtr = Module.ccall([
    "get_keypair_private_key",
    "number",
    ["number"],
    [keypairPtr],
  ]);

  // Build the header using the keypair, session receivers and the file session key
  let header = Module.ccall([
    "create_crypt4gh_header",
    "number",
    ["number", "number", "number", "number"],
    [
      sessionKeyPtr,
      privateKeyPtr,
      uploads[container].receivers,
      uploads[container].receiversLen,
    ],
  ]);
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
  let chunk = Module.ccall([
    "encrypt_chunk",
    "number",
    ["number", "array", "number"],
    [
      uploads[container].files[path],
      deChunk,
    ],
  ]);
  let chunkPtr = Module.ccall([
    "wrap_chunk_content",
    "number",
    ["number"],
    [chunk],
  ]);
  let chunkLen = Module.ccall([
    "wrap_chunk_len",
    "number",
    ["number"],
    [chunk],
  ]);

  // As above, need a new array from view as it will get stale
  let ret = new Uint8Array(HEAPU8.subarray(chunkPtr, chunkPtr + chunkLen));

  Module.ccall([
    "free_chunk",
    "number",
    ["number"],
    [chunk],
  ]);

  return ret;
}

// Slice and encrypt the next chunk
function getChunk(container, path, iter) {
  // Get the iterator and offset of the next chunk
  let ptr = iter * 65536;

  // Slice out the next chunk, encrypt it and send via websocket
  uploads[container].files[path].file
    .slice(ptr, ptr + 65536)
    .arrayBuffer()
    .then(c => {
      socket.send(msgpack.serialize({
        command: "add_chunk",
        container: container,
        object: path,
        order: iter,
        data: encryptChunk(container, path, c),
      }));
      uploads[container].files[path].currentByte += 65536;
      uploads[container].files[path].totalUploadedChunks += 1;

      postMessage({
        eventType: "progress",
        container: container,
        object: path,
        done: uploads[container].files[path].currentByte,
        total: uploads[container].files[path].totalBytes,
      });
    });
}

// Encrypt the next chunk if it exists
function nextChunk(container, path) {
  let iter = uploads[container].files[path].chunks.shift();

  // If shift doesn't return a chunk location, the file has been consumed
  if (iter === undefined) {
    return;
  }

  getChunk(container, path, iter);
}

// Safely free and remove an upload session
function finishUploadSession(container) {
  return;
}


// Open the websocket for communicating with the runner
async function openWebSocket (
  upinfo,
) {
  let socketURL = new URL(upinfo.webSocketUrl);
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

  socket = new WebSocket(socketURL, "binary");
  socket.binaryType = "arraybuffer";

  socket.onmessage = msg => {
    let msg_data = msgpack.deserialize(msg.data);

    switch (msg_data.command) {
      // Abort the upload
      case "abort":
        postMessage({
          eventType: "abort",
          container: msg_data.container,
          object: msg_data.object,
          reason: msg_data.reason,
        });
        break;
      // A file was successfully uploaded
      case "success":
        postMessage({
          eventType: "success",
          container: msg_data.container,
          object: msg_data.object,
        });
        break;
      // Push the next chunk to the websocket
      case "next_chunk":
        nextChunk(msg_data.container, msg_data.object);
        break;
      // Retry a chunk in the websocket
      case "retry_chunk":
        getChunk(msg_data.container, msg_data.object, msg_data.order);
        break;
    }
  }
}

/*
Add a batch of files to the current upload session.
*/
function addFiles(session, files, container) {
  for (const file of files) {
    let path = `${file.name}.c4gh`
    let totalBytes = Math.floor(file.size / 65536) * 65564;
    let totalChunks = Math.floor(file.size / 65536);

    // Add the last block to total bytes and total chunks in case it exists
    if (file.size % 65536 > 0) {
      totalBytes += file.size % 65536 + 28;
      totalChunks++;
    }

    // Add the chunks that need to be uploaded
    let chunks = []
    for (let i = 0; i < this.totalChunks; i++) {
      chunks.push(i);
    }

    // Add the file to the upload session
    session.files[path] = {
      totalBytes: totalBytes,
      currentByte: 0,
      totalChunks: totalChunks,
      totalUploadedChunks: 0,
      chunks: chunks,
      file: file,
    }

    // Create the file header
    createUploadSessionFile(container, path);

    let msg = {
      command: "add_header",
      container: container,
      object: path,
      name: session.projectName,
      total: totalBytes,
      data: session.files[path].header,
    };

    if (session.owner !== "") {
      msg.owner = session.owner;
    }
    if (session.ownerName !== "") {
      msg.owner_name = session.ownerName;
    }

    // Upload the file header
    socket.send(msgpack.serialize(msg));
  }
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
        );
      }

      if (e.data.owner !== "") {
        uploads[container].owner = e.data.owner;
      }
      if (e.data.ownerName !== "") {
        uploads[container].ownerName = e.data.ownerName;
      }

      // Add the files in the upload request
      addFiles(uploads[e.data.container], e.data.files);

      e.source.postMessage({
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
