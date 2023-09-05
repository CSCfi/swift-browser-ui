var moduleStartComplete = false;

console.log("Download/upload worker started.");
console.log("Runner is running in a service worker.");


// Detect if inside a ServiceWorker
let inServiceWorker = false;
if (typeof ServiceWorkerGlobalScope !== "undefined") {
  inServiceWorker = self instanceof ServiceWorkerGlobalScope;
}


function timeout(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

const waitAsm = async () => {
  while (!moduleStartComplete) {
    await timeout(250);
  }

  return true;
}

self.addEventListener("install", (event) => {
  console.log("Service Worker installed.");
  event.waitUntil(waitAsm());
});
self.addEventListener("activate", (event) => {
  console.log("Service worker activated.");
  event.waitUntil(self.clients.claim());
});

var Module = {
  onRuntimeInitialized: () => {
    moduleStartComplete = true;
  },
  printErr: (text) => {
    console.log("WASM execution debug: ", text);
  },
};

// Example: https://devenv:8443/file/test-container/examplefile.txt.c4gh
const fileUrl = new RegExp("/file/[^/]*/.*$");
// Example: https://devenv:8443/archive/test-container.tar
const archiveUrl = new RegExp("/archive/[^/]*\.tar$");
const fileUrlStart = new RegExp("/file/[^/]*/");

// Add listener for fetch events
self.addEventListener("fetch", (e) => {
  console.log(e);
  const url = new URL(e.request.url);

  console.log(url);

  let fileName;
  let containerName;

  if (fileUrl.test(url.path)) {
    fileName = url.path.replace(fileUrlStart, "");
    containerName = url.path.replace("/file/", "").replace(fileName, "");
  } else if (archiveUrl.test(url.path)) {
    fileName = request.path.replace("/archive/", "");
    containerName = fileName.replace(/\.tar$/, "");
  } else {
    return;
  }

  if (fileUrl.test(url.path) || archiveUrl.test(url.path)) {
    let streamController;
    const stream = new ReadableStream({
      start(controller) {
        streamController = controller;
      },
    });
    const response = new Response(stream);
    response.headers.append(
      "Content-Disposition",
      'attachment; filename="' + fileName.replace(".c4gh", "") + '"',
    );

    createDownloadSession(containerName, streamController, archiveUrl.test(url.path));

    let files;
    if (fileUrl.test(url.path)) {
      files = [fileName];
    } else if (url.searchParams.get("files") !== null) {
      files = url.searchParams.get("files").split(",");
    } else {
      files = [];  // empty list signifies all files in a specific container
    }

    e.waitUntil(
      (async () => {
        await clients.matchAll().then(clients => {
          clients.forEach(client => {
            client.postMessage({
              eventType: "getHeaders",
              container: containerName,
              files: files,
              publickey: downloads[containerName].pubkey,
            });
          });
        });
        r.respondWith(response);
      }),
    );
  }
});

self.addEventListener("message", (e) => {
  if (inServiceWorker) {
    e.stopImmediatePropagation();
  } else {
    return;
  }

  switch (e.data.command) {
    case "addHeaders":
      beginDownloadInSession(
        e.data.container,
        e.data.headers,
      );
      e.source.postMessage({
        eventType: "downloadStarted",
        container: e.data.container,
      });
      break;
  }
});
