// eslint-disable-next-line
const { defineConfig } = require("cypress");
const { cloudPlugin } = require("cypress-cloud/plugin");

// eslint-disable-next-line
module.exports = defineConfig({
  fixturesFolder: "../tests/cypress/fixtures",
  viewportWidth: 1280,
  viewportHeight: 720,
  includeShadowDom: true,
  retries: {
    runMode: 3,
    openMode: 0,
  },
  videoCompression: false,
  defaultCommandTimeout: 10000,
  e2e: {
    // We've imported your old cypress plugins here.
    // You may want to clean this up later by importing these.
    setupNodeEvents(on, config) {
      // eslint-disable-next-line
      return cloudPlugin(on, config);
    },
    // baseUrl: "https://172.17.0.1:8081/",
    baseUrl: "https://sd-connect.dev:8000/",

    specPattern: "../tests/cypress/integration/**/*.cy.{js,jsx,ts,tsx}",
    supportFile: "../tests/cypress/support/index.js",
  },
  env: {
    username: "swift",
    password: "veryfast",
    wrongusername: "swif11t",
    wrongpassword: "very11fast",
  },
});
