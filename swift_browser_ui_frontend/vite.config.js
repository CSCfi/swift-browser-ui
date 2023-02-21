
import { defineConfig } from "vite";
import { createVuePlugin as vue } from "vite-plugin-vue2";

import path from "node:path";

const proxyTo = {
  target: `http://${process.env.BACKEND_HOST || "localhost"}:${process.env.BACKEND_PORT || "8080"}`,
  changeOrigin: true,
  secure: false,  // Won't check certificates
};

const oidcEnabled = process.env.OIDC_ENABLED === "True";

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
  let base = undefined;
  if (command === "build") base = "/static/";

  return {
    root,
    base,
    plugins: [vue()],
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
      strictPort: true,
      proxy: {
        "/static":              proxyTo,
        "/api":                 proxyTo,
        "/browse":              proxyTo,
        "/discover":            proxyTo,
        "/login":               proxyTo,
        "/libupload":           proxyTo,
        "/login/oidc":          proxyTo,
        "/login/oidc-front":    proxyTo,
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
      },
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
