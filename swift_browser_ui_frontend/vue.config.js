module.exports = {  // eslint-disable-line
  publicPath: "/static",
  devServer: {
    // eslint-disable-next-line
    proxy: `http://${process.env.BACKEND_HOST || "localhost"}:${process.env.BACKEND_PORT || "8080"}`,
    hot: "only",
    client: {
      // eslint-disable-next-line
      webSocketURL: `ws://${process.env.BACKEND_HOST || "localhost"}:${process.env.BACKEND_PORT || "8080"}/ws`,
    },
  },
  pages: {
    index: {
      entry: "src/entries/index.js",
      template: "public/index.html",
      filename: "index.html",
      title: "Swift browser UI",
      chunks: ["chunk-vendors", "chunk-common", "index"],
    },
    badrequest: {
      entry: "src/entries/badrequest.js",
      template: "public/index.html",
      filename: "400.html",
      title: "Bad Request",
      chunks: ["chunk-vendors", "chunk-common", "badrequest"],
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
    loginpassword: {
      entry: "src/entries/loginpassword.js",
      template: "public/index.html",
      filename: "loginpassword.html",
      title: "Swift browser UI – Login",
      chunks: ["chunk-vendors", "chunk-common", "loginpassword"],
    },
  },
};
