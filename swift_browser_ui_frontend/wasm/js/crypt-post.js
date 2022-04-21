// Wait until calledRun is done
var waitAsm = async () => {
  console.log("Wait asm called.");
  if (calledRun) {
    console.log("Wait asm finished.");
    return true;
  } else {
    return new Promise(() => {
      setTimeout(waitAsm, 2500);
    });
  }
}

self.addEventListener("install", (event) => {
  console.log("Install called");
  event.waitUntil(self.skipWaiting());
  console.log("Install finished");
});
self.addEventListener("activate", (event) => {
  console.log("Activate called.");
  event.waitUntil(self.clients.claim());
  console.log("Activate finished.");
});

let streamController, sessionPtr, fileName, headerPtr, headerLen, chunkPtr, chunkLen, chunk, header, chunkArray;

self.addEventListener("fetch", (e) => {
  if (e.request.url.includes("encrypted")) {
    const stream = new ReadableStream({
      start(controller) {
        streamController = controller;
      },
    });
    const response = new Response(stream);
    response.headers.append(
      "Content-Disposition",
      'attachment; filename="' + fileName + '"'
    );
    e.respondWith(response);
  }
});

self.addEventListener("message", (e) => {
  switch(e.data.cmd) {
    case "initFileSystem":
      console.log("Received call to initialize filesystem.");
      FS.mkdir("/keys");
      FS.mkdir("/keys/recv_keys");
      FS.mkdir("/data");
      // Create output device
      e.source.postMessage({
        eventType: "wasmFilesystemInitialized",
      });
      break;
    case "appendPubkey":
      console.log("Received call to add a public key.");
      FS.writeFile(
        "/keys/recv_keys/pubkey_" + e.data.keyname.toString(),
        e.data.pubkey,
      );
      e.source.postMessage({
        eventType: "wasmFilesystemPubkeyAdded",
        publicKey: e.data.pubkey,
        publicKeyOrder: e.data.keyname,
      });
      break;
    case "addPrivKey":
      console.log("Received call to add a private key.");
      FS.writeFile(
        "/keys/pk.key",
        e.data.privkey,
      );
      e.source.postMessage({
        eventType: "wasmFilesystemPrivkeyAdded",
        privKey: e.data.privkey,
      })
      break;
    case "initEphemeral":
      console.log("Initiating ephemeral encryption.");
      sessionPtr = Module.ccall(
        "open_session_eph",
        "number",
        [],
        [],
      );
      fileName = e.data.filename + ".c4gh";
      e.source.postMessage({
        eventType: "encryptSessionInitiated",
        ptr: sessionPtr,
      });
      break;
    case "initNormal":
      console.log("initializing a normal encryption session.");
      sessionPtr = Module.ccall(
        "open_session",
        "number",
        ["string"],
        [e.data.passphrase],
      );
      fileName = e.data.filename + ".c4gh";
      e.source.postMessage({
        eventType: "encryptSessionInitiated",
        ptr: sessionPtr,
      });
      break;
    case "createHeader":
      console.log("Creating a header.");
      header = Module.ccall(
        "wrap_crypt4gh_header",
        "number",
        ["number"],
        [sessionPtr],
      );
      headerPtr = Module.ccall(
        "wrap_chunk_content",
        "number",
        ["number"],
        [header]
      );
      headerLen = Module.ccall(
        "wrap_chunk_len",
        "number",
        ["number"],
        [header],
      )
      // Copy chunk buffer contents to new array and answer
      e.source.postMessage({
        eventType: "encryptedHeaderReady",
        header: new Uint8Array(HEAPU8.subarray(headerPtr, headerPtr + headerLen)),
      });
      // Free header memory
      Module.ccall(
        "free_chunk",
        "number",
        ["number"],
        [header],
      );
      break;
    case "encryptChunk":
      chunkArray = new Uint8Array(e.data.chunk);
      chunk = Module.ccall(
        "encrypt_chunk",
        "number",
        ["number", "array", "number"],
        [sessionPtr, chunkArray, chunkArray.length],
      );
      chunkPtr = Module.ccall(
        "wrap_chunk_content",
        "number",
        ["number"],
        [header]
      );
      chunkLen = Module.ccall(
        "wrap_chunk_len",
        "number",
        ["number"],
        [header],
      );
      // Respond with the chunk, and ask for the next one
      e.source.postMessage({
        eventType: "nextChunk",
        chunk: new Uint8Array(HEAPU8.subarray(chunkPtr, chunkPtr + chunkLen)),
        iter: e.data.iter,
      });
      Module.ccall(
        "free_chunk",
        "number",
        ["number"],
        [chunk],
      )
      break;
    case "cleanUp":
      console.log("Serviceworker cleaning up.");
      if (streamController != undefined) {
        streamController.close();
      }
      Module.ccall(
        "clean_session",
        undefined,
        ["number"],
        [sessionPtr],
      );
      e.source.postMessage({
        eventType: "cleanUpDone",
      });
  }
});
