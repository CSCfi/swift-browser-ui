var moduleStartComplete = false;

var Module = {
  onRuntimeInitialized: () => {
    console.log("WASM runtime has been initialized.");
    moduleStartComplete = true;
  },
};

var waitAsm = () => {
  if (moduleStartComplete) {
    console.log("WASM runtime has been initialized.");
    return true;
  } else {
    return new Promise(() => {
      setTimeout(waitAsm, 250);
    });
  }
}
