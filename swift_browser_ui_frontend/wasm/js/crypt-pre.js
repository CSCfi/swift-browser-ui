import msgpack from "@ygoe/msgpack";

var moduleStartComplete = false;

var Module = {
  onRuntimeInitialized: () => {
    moduleStartComplete = true;
  },
  printErr: (text) => {
    console.log("WASM execution debug: ", text);
  },
};

function timeout(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function waitAsm() {
  // console.log("Begin wait for WASM readiness.");
  while (!moduleStartComplete) {
    // console.log("Waiting 250ms for WASM readiness.");
    await timeout(250);
  }
  // console.log("Module start finalized. Ready to answer.");
  return true;
}

var wasmReady = waitAsm();
