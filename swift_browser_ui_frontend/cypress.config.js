const { defineConfig } = require("cypress");
const { cloudPlugin } = require("cypress-cloud/plugin");
const { Client } = require("pg");
const { spawn } = require("node:child_process");

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
    setupNodeEvents(on, config) {
      on("task", {
        async resetDB() {
          // Connect to Sharing DB from Node
          /* 'host' and 'port' can be changed if you have configured
            the Postgresql container to run in different host and port
          */
          const client = new Client({
            database: "swiftbrowserdb",
            host: "localhost",
            port: 5432,
            user: "sharing",
            password: "pass",
          });
          await client.connect();

          client.on("error", (err) => {
            console.error("Something wrong with Posgresql database", err.stack);
          });
          // Delete tables from Sharing DB
          await client.query("DELETE FROM Shares;");
          await client.query("DELETE FROM ProjectIDs;");
          await client.query("DELETE FROM Tokens;");

          // Regular containers are located in Openstack Swift's DB
          // We need to run another script to delete them from Openstack
          const ls = spawn("bash",
            ["../tests/cypress/support/delete-swiftContainers.sh"]);

          ls.stderr.on("data", (data) => {
            console.error(`stderr: ${data}`);
          });

          return null;
        },
      });
      return cloudPlugin(on, config);
    },
    // baseUrl: "https://172.17.0.1:8081/",
    baseUrl: "https://sd-connect.dev:8081/",

    specPattern: "../tests/cypress/integration/**/*.cy.{js,jsx,ts,tsx}",
    supportFile: "../tests/cypress/support/index.js",
    experimentalStudio: true,
    textFileLocation: "../tests/cypress/fixtures/text-files/",
  },
  env: {
    username: "swift",
    password: "veryfast",
    wrongusername: "swif11t",
    wrongpassword: "very11fast",
    username2: "admin",
    password2: "superuser",
  },
});
