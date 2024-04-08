//download

import SparkMD5 from "../../../swift_browser_ui_frontend/node_modules/spark-md5";

describe("Downloads a file, verifies content and checksum", function () {

  const useServiceWorker = "serviceWorker" in navigator
    && window.showSaveFilePicker === undefined;
  const fileName = Math.random().toString(36).substring(2, 7);

  beforeEach(() => {
    cy.task("resetDB");
    cy.deleteDB();
    cy.visit(Cypress.config("baseUrl"));
    cy.login(Cypress.env("username"), Cypress.env("password"));
    cy.generateFixture(fileName);
  });

  //Cypress may not fully support the interactions with service workers and the showSaveFilePicker API (handleDownWorker) out of the box. Some other testing other than e2e might be required

  it("should download a file", () => {

    //create a folder
    const folderName = Math.random().toString(36).substring(2, 7);
    cy.addFolder(folderName);
    cy.wait(3000);

    //access folder
    cy.searchFolder(folderName);
    cy.get("[data-testid='search-result']")
      .contains(folderName)
      .click({ force: true });
    cy.wait(5000);

    cy.fixture(
      "text-files/" + fileName + ".txt",
      "utf-8"
    ).then((contentOnUpload) => {
      //check file hash before upload (encryption)
      const hexHashUpload = SparkMD5.hash(contentOnUpload);
      cy.log("Upload hash", hexHashUpload);

      //upload the fixture file
      cy.uploadFileFromFolder(fileName);

      //close toast
      cy.get('[data-testid="close-upload-toast"]')
        .should("exist")
        .click();

      //check if the file name is on the page
      cy.contains(fileName).should("exist");

      //TEST SERVICE WORKER DOWNLOAD
      if (useServiceWorker) {
        cy.log("Testing file download with service worker");

        //click on download button
        cy.contains(fileName)
          .parent()
          .parent()
          .find("[testid='download-object']")
          .as("download")
          .click({force: true});

        cy.wait(3000);

        cy.readFile(Cypress.config("downloadsFolder") + "/" + fileName + ".txt")
          .should("exist");

        // Check file hash after download
        cy.fixture(
          "/downloads/" + fileName + ".txt",
          "utf-8"
        ).then((contentOnDownload) => {
          const hexHashDownload = SparkMD5.hash(contentOnDownload);
          cy.log(hexHashDownload);

          //match full file content before and after
          expect(contentOnUpload).to.eq(contentOnDownload);

          //match file checksum before and after
          expect(hexHashUpload).to.eq(hexHashDownload);
        });
      }

      //TODO TEST DIRECT DOWNLOAD
      else {
        cy.log("Testing direct file download");
      }
    });
  });
});
