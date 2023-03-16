// from https://github.com/CSCfi/csc-ui-vue-directive/blob/bf642973c750b7b423aae0f64fae32300b11c6f5/src/vControl.ts
// csc-ui-vue-directive has imports for vue2, and can't be used as is
const eventHandler = (el) => (event) => {
  let _a = event === null || event === void 0 ? void 0 : event.detail;
  el.value = _a !== null && _a !== void 0 ? _a : null;
  el.dispatchEvent(new Event("input", { bubbles: true }));
};
export const vControl = {
  mounted(el) {
    el.addEventListener("changeValue", eventHandler(el));
  },
  beforeUnmount(el) {
    el.removeEventListener("changeValue", eventHandler(el));
  },
};
