/* eslint-disable no-undef */
const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    "baseUrl": "http://localhost:8000",
    "fixturesFolder": "../tests/cypress/fixtures",
    "specPattern": "../tests/cypress/integration",
    "supportFile": "../tests/cypress/support/index.js",
    setupNodeEvents() {
      // e2e testing node events setup code
    },
    "viewportWidth": 1280,
    "viewportHeight": 720,
    "retries": {
      "runMode": 3,
      "openMode": 0,
    },
    "videoCompression": false,
    "defaultCommandTimeout": 10000,
  },
});


