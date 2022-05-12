var moduleStartComplete = false;

var Module = {
  onRuntimeInitialized: () => {
    moduleStartComplete = true;
  },
};

var waitAsm = (resolve, reject) => {
  if (moduleStartComplete) {
    resolve(true);
    return;
  } else {
    setTimeout(waitAsm, 250, resolve, reject);
  }
}
