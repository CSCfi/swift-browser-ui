module.exports = {
  publicPath: "/static",
  pages: {
    index: {
      entry: "src/index.js",
      template: "public/index.html",
      filename: "index.html",
      title: "Swift browser UI",
      chunks: ["chunk-vendors", "chunk-common", "index"],
    },
    unauth: {
      entry: "src/unauth.js",
      template: "public/index.html",
      filename: "401.html",
      title: "Unauthorized",
      chunks: ["chunk-vendors", "chunk-common", "unauth"],
    },
    forbid: {
      entry: "src/forbid.js",
      template: "public/index.html",
      filename: "403.html",
      title: "Forbidden",
      chunks: ["chunk-vendors", "chunk-common", "forbid"],
    },
    notfound: {
      entry: "src/notfound.js",
      template: "public/index.html",
      filename: "404.html",
      title: "Not Found",
      chunks: ["chunk-vendors", "chunk-common", "notfound"],
    },
    browse: {
      entry: "src/main.js",
      template: "public/index.html",
      filename: "browse.html",
      title: "Swift browser UI",
      chunks: ["chunk-vendors", "chunk-common", "browse"],
    },
    login: {
      entry: "src/login.js",
      template: "public/index.html",
      filename: "login.html",
      title: "Swift browser UI – Login",
      chunks: ["chunk-vendors", "chunk-common", "login"],
    },
  },
};
