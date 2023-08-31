var moduleStartComplete = false;

// Detect if inside a ServiceWorker
function detectServiceWorker() {
  if (typeof ServiceWorkerGlobalScope !== "undefined") {
    return self instanceof ServiceWorkerGlobalScope;
  }
  return false;
}

console.log("Download/upload worker started.");
console.log("Checking if running in a service worker.");

function timeout(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function waitAsm() {
  while (!moduleStartComplete) {
    await timeout(250);
  }

  return true;
}

if (detectServiceWorker()) {
  console.log("Running in a service worker.");
  self.addEventListener("install", (event) => {
    console.log("Service Worker installed.");
    event.waitUntil(waitAsm());
  });
  self.addEventListener("activate", (event) => {
    console.log("Service worker activated.");
    event.waitUntil(self.clients.claim());
  });
}

var Module = {
  onRuntimeInitialized: () => {
    moduleStartComplete = true;
  },
  printErr: (text) => {
    console.log("WASM execution debug: ", text);
  },
};
