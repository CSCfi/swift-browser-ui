var moduleStartComplete = false;

console.log("Download/upload worker started.");

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

var Module = {
  onRuntimeInitialized: () => {
    moduleStartComplete = true;
  },
  printErr: (text) => {
    console.log("WASM execution debug: ", text);
  },
};
