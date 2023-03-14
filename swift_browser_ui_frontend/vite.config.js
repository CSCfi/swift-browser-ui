
import { defineConfig } from "vite";
import { createVuePlugin as vue } from "vite-plugin-vue2";

import fs from "node:fs";
import path from "node:path";

const TLS_ENABLED = process.env.VITE_TLS === "True";
const http_mode = TLS_ENABLED ? "https" : "http";
// paths should be absolute or relative to vite.config.js
const TLS_CERT_PATH = process.env.VITE_TLS_CERT || undefined;
const TLS_KEY_PATH = process.env.VITE_TLS_KEY || undefined;

let https = null;
if (TLS_ENABLED) {
  console.log("vite dev serve will expect https");
  https = {
    key:  fs.readFileSync(TLS_KEY_PATH),
    cert: fs.readFileSync(TLS_CERT_PATH),
  };
}

const proxyTo = {
  target: `${http_mode}://${process.env.BACKEND_HOST || "localhost"}:${process.env.BACKEND_PORT || "8080"}`,
  changeOrigin: true,
  secure: false,  // Won't check certificates
};

const oidcEnabled = process.env.OIDC_ENABLED === "True";
const root = path.resolve(__dirname, "src");
let pages = {
  "index":         path.resolve(root, "index.html"),
  "select":        path.resolve(root, "select.html"),
  "badrequest":    path.resolve(root, "400.html"),
  "unauth":        path.resolve(root, "401.html"),
  "forbid":        path.resolve(root, "403.html"),
  "notfound":      path.resolve(root, "404.html"),
  "uidown":        path.resolve(root, "503.html"),
  "browse":        path.resolve(root, "browse.html"),
  "loginpassword": path.resolve(root, "loginpassword.html"),
  "login":         path.resolve(root, "login.html"),
  "login2step":    path.resolve(root, "login2step.html"),
};
if (oidcEnabled) {
  pages["index"] = path.resolve(root, "index_oidc.html");
}
let proxy = {
  "/static/assets":       proxyTo,
  "/api":                 proxyTo,
  "/discover":            proxyTo,
  "/libupload":           proxyTo,
  "/login/oidc":          proxyTo,
  "/login/oidc_front":    proxyTo,
  "/login/oidc-redirect": proxyTo,
  "/login/credentials":   proxyTo,
  "/login/return":        proxyTo,
  "/login/rescope":       proxyTo,
  "/upload":              proxyTo,
  "/enupload":            proxyTo,
  "/download":            proxyTo,
  "/sign":                proxyTo,
  "/replicate":           proxyTo,
  "/token":               proxyTo,
  "/ws": {
    target: `ws${process.env.SWIFT_UI_SECURE_WEBSOCKET}://${process.env.SWIFT_UI_TLS_HOST}:${process.env.SWIFT_UI_TLS_PORT}/ws`,
    ws: true,
  },
};

// Vite doesn't work "out-of-the-box" with multiple SPAs
// This middleware loads existing html pages and
// forwards all routes starting with "/browse" to "browse.html"
// solution based on https://github.com/vitejs/vite/issues/2958#issuecomment-1065810046
const multipagePlugin = () => ({
  name: "multipage-middleware",
  configureServer(server) {
    server.middlewares.use(async (req, res, next) => {
      // Remove query, hash and trailing slash
      let url = req.url
        .replace(/\?.*$/s, "")
        .replace(/#.*$/s, "")
        .replace(/.+\/$/, "");

      // skip proxy paths
      const proxyUrls = Object.keys(proxy);
      for (let index in proxyUrls) {
        if (url.startsWith(proxyUrls[index])) {
          return next();
        }
      }

      // redirect to defined page's HTML file
      let pageName = url.split("/")[1];
      // eslint-disable-next-line no-prototype-builtins
      if (pages.hasOwnProperty(pageName)) {
        let pathArray = pages[pageName].split("/");
        req.url = "/" + pathArray[pathArray.length - 1];
      }
      next();
    });
  },
});

// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {

  if (mode === "development") {
    const { execSync } = require("child_process");
    const shell = (cmd) => execSync(cmd, {encoding: "utf8"}).trim();
  
    try {
      const branch = shell("git branch --show-current");
      const version = shell("git describe --always --long --tags");
      const hash = shell("git rev-parse HEAD");
      const url = "https://github.com/CSCfi/swift-browser-ui/commit/";
  
      process.env.VITE_GIT_VERSION = `${branch} | ${version}`;
      process.env.VITE_GIT_LINK = url + hash;

      console.log(process.env.VITE_GIT_VERSION);
      console.log(process.env.VITE_GIT_LINK);
    }
    catch(error){
      console.log("Failed to get version from git");
      console.log(error);
    }
  }
  let base = undefined;
  if (command === "build") base = "/static/";

  return {
    root,
    base,
    appType: "mpa", // set the dev server as a multi-page app
    plugins: [
      vue(), 
      multipagePlugin(),
    ],
    build: {
      outDir: path.resolve(__dirname, "dist"),
      emptyOutDir: true,
      reportCompressedSize: false,
      rollupOptions: {
        input: pages,
        output: {
          dir: "dist",
        },
      },
    },
    server: {
      host: "0.0.0.0",
      port: process.env.FRONTEND_PORT || "8081",
      https,
      strictPort: true,
      proxy,
    },
    resolve: {
      alias: {
        "@": root,
      },
    },
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: `
            @import "./src/css/prod.scss";
          `,
        },
      },
    },
  };
});
