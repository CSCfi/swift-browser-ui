// Normal required listeners for starting the service worker
self.addEventListener("install", (event) => {
  event.waitUntil(self.skipWaiting());
});
self.addEventListener("activate", (event) => {
  event.waitUntil(self.clients.claim());
});

let sessionPtr, fileName, headerPtr, headerLen, chunkPtr, chunkLen, chunk, header, chunkArray;

console.log(Module);
console.log(FS);

wasmReady.then(() => {
  console.log("Adding sw event listeners.");
  self.addEventListener("message", (e) => {
    switch(e.data.cmd) {
      case "pingWasm":
        e.source.postMessage({
          eventType: "wasmReady",
        });
        break;
      case "initFileSystem":
        FS.mkdir("/keys");
        FS.mkdir("/keys/recv_keys");
        FS.mkdir("/data");
        // Create output device
        e.source.postMessage({
          eventType: "wasmFilesystemInitialized",
        });
        break;
      case "appendPubkey":
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
        try {
          Module.ccall(
            "clean_session",
            undefined,
            ["number"],
            [sessionPtr],
          );
          FS.rmdir("/keys/recv_keys")
          FS.rmdir("/keys");
          FS.rmdir("/data");
        } catch (e) {
          console.log("FS ignoring error on remove ", e);
        } finally {
          e.source.postMessage({
            eventType: "cleanUpDone",
          });
        }
        break;
    }
  });
});
