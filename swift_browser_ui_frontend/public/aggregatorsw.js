// ServiceWorker post-initialization JS part for WASM components

// ServiceWorker based downloads are needed for Firefox and Safari
// compatibility. Chromium-based browsers have File System API available,
// which can be used for directly downloading content into a file on
// user's machine – that will be used when available.

// Definitions
let
  streamController
;

let
  fileName
;

// ServiceWorker start requirements
self.addEventListener("install", (event) => {
  event.waitUntil(self.skipWaiting());
});
self.addEventListener("activate", (event) => {
  event.waitUntil(self.clients.claim());
});

// Event listener for file requests
self.addEventListener("fetch", (e) => {
  if (e.request.url.startsWith(self.location.origin + "/file")) {
    const stream = new ReadableStream({
      start(controller) {
        streamController = controller;
      }
    });
    const response = new Response(stream);
    response.headers.append(
      "Content-Disposition",
      'attachment; filename="' + fileName.replace(".c4gh", "") + '"',
    );
    e.respondWith(response);
  }
})


// Attach event listener for the ServiceWorker after WASM initialization
self.addEventListener("message", (e) => {
  e.stopImmediatePropagation();
  switch(e.data.cmd) {
    case "beginFile":
      if (streamController !== undefined) {
        streamController.close();
      }
      fileName = e.data.fileName;
      e.source.postMessage({
        eventType: "fileStarted",
      });
      break;
    case "addChunk":
      streamController.enqueue(e.data.chunk);
      e.source.postMessage({
        eventType: "chunkAdded",
      });
      break;
    case "downloadFinished":
      streamController.close();
      streamController = undefined;
      e.source.postMessage({
        eventType: "streamClosed",
      });
      break;
  }
});
