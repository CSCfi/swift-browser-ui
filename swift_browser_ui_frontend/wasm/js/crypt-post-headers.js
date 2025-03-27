// JS code for the header creation worker

// Create a c4ghtransit header for the file with the given parameters
function createFileHeader(e) {
  // Read in the receivers
  let recvDirPath = `${e.data.bucket}_receivers_${Math.random().toString(36)}`;
  FS.mkdir(recvDirPath);
  let files = [];
  // Add receiver keys to the filesystem
  for (const receiver of e.data.receivers) {
    let tmpRecvPath = `${recvDirPath}/pubkey_${e.data.receivers.indexOf(receiver).toString()}`;
    files.push(tmpRecvPath);
    FS.writeFile(tmpRecvPath, receiver);
  }

  // Create the session key
  let sessionKeyPtr = Module.ccall(
    "create_session_key",
    "number",
    [],
    [],
  );
  // Build the header using the session key and added receivers
  let header = Module.ccall(
    "create_header_from_key",
    "number",
    ["string", "number"],
    [recvDirPath, sessionKeyPtr],
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

  // Copy the session key from the pointer (Curve25519 keys are 32 bytes long)
  let sessionKey = new Uint8Array(HEAPU8.subarray(sessionKeyPtr, sessionKeyPtr + 32));
  // Copy the resulting header from memory before the memory view gets stale
  let headerView = new Uint8Array(HEAPU8.subarray(headerPtr, headerPtr + headerLen));

  // Clean up the resources
  Module.ccall(
    "free_chunk",
    "number",
    ["number"],
    [header],
  );
  Module.ccall(
    "free_crypt4gh_session_key",
    undefined,
    ["number"],
    [sessionKeyPtr],
  );
  Module.ccall(
    "rmrecv",
    undefined,
    ["string"],
    [recvDirPath],
  );

  postMessage({
    eventType: "headerDone",
    bucket: e.data.bucket,
    key: e.data.key,
    header: headerView,
    secret: sessionKey,
  });
}

self.addEventListener("message", (e) => {
  e.stopImmediatePropagation();

  switch(e.data.command) {
    case "createHeader":
      createFileHeader(e);
      break;
  }
})
