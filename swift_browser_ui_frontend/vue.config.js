module.exports = {  // eslint-disable-line
  publicPath: "/static",
  pages: {
    index: {
      entry: "src/entries/index.js",
      template: "public/index.html",
      filename: "index.html",
      title: "Swift browser UI",
      chunks: ["chunk-vendors", "chunk-common", "index"],
    },
    unauth: {
      entry: "src/entries/unauth.js",
      template: "public/index.html",
      filename: "401.html",
      title: "Unauthorized",
      chunks: ["chunk-vendors", "chunk-common", "unauth"],
    },
    forbid: {
      entry: "src/entries/forbid.js",
      template: "public/index.html",
      filename: "403.html",
      title: "Forbidden",
      chunks: ["chunk-vendors", "chunk-common", "forbid"],
    },
    notfound: {
      entry: "src/entries/notfound.js",
      template: "public/index.html",
      filename: "404.html",
      title: "Not Found",
      chunks: ["chunk-vendors", "chunk-common", "notfound"],
    },
    uidown: {
      entry: "src/entries/uidown.js",
      template: "public/index.html",
      filename: "503.html",
      title: "Not Found",
      chunks: ["chunk-vendors", "chunk-common", "uidown"],
    },
    browse: {
      entry: "src/entries/main.js",
      template: "public/index.html",
      filename: "browse.html",
      title: "Swift browser UI",
      chunks: ["chunk-vendors", "chunk-common", "browse"],
    },
    login: {
      entry: "src/entries/login.js",
      template: "public/index.html",
      filename: "login.html",
      title: "Swift browser UI – Login",
      chunks: ["chunk-vendors", "chunk-common", "login"],
    },
  },
};
