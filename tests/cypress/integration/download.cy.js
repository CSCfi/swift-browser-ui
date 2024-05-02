//download

import SparkMD5 from "../../../swift_browser_ui_frontend/node_modules/spark-md5";

describe("Downloads file/container, verifies content and checksum", function () {

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
    ).then($contentOnUpload => {

      //check file hash before upload (encryption)
      const hexHashUpload = SparkMD5.hash($contentOnUpload);
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

        //read fails if file doesn't exist
        cy.readFile(Cypress.config("downloadsFolder") + "/" + fileName + ".txt")

        // Check file hash after download
        cy.fixture(
          "/downloads/" + fileName + ".txt",
          "utf-8"
        ).then($contentOnDownload => {
          const hexHashDownload = SparkMD5.hash($contentOnDownload);
          cy.log("Download hash", hexHashDownload);

          //match full file content before and after
          expect($contentOnUpload).to.eq($contentOnDownload);

          //match file checksum before and after
          expect(hexHashUpload).to.eq(hexHashDownload);
        });
      }

      //TEST DIRECT DOWNLOAD
      //Since we cannot directly interact with user's file system through Cypress
      //testing is done through OPFS which doesn't have strict security checks
      else {
        cy.log("Testing direct file download");

        cy.contains(fileName)
        .parent()
        .parent()
        .find("[testid='download-object']")
        .as("download")
        .click({force: true});

        cy.wait(5000);

        cy.getFileContentFromOPFS(fileName + ".txt").then(($contentOnDownload) => {
          const hexHashDownload = SparkMD5.hash($contentOnDownload);
          cy.log("Download hash", hexHashDownload);
          //match full file content before and after
          expect($contentOnUpload).to.eq($contentOnDownload);
          //match file checksum before and after
          expect(hexHashUpload).to.eq(hexHashDownload);
        });
      };
    });
  });

  it("should download an archive", () => {
    const folderName = Math.random().toString(36).substring(2, 7);
    //check file hashes before upload
    let hexHashUpload;
    let uploadedContent;

    cy.fixture(
      "text-files/" + fileName + ".txt",
      "utf-8"
    ).then($contentOnUpload => {
      //check file hash before upload (encryption)
      uploadedContent = $contentOnUpload;
      hexHashUpload = SparkMD5.hash($contentOnUpload);
    });

    //open upload modal
    cy.get("[data-testid='upload-file']").click();
    cy.wait(3000);

    //check that modal opened
    cy.get("[data-testid='upload-modal']").should("be.visible");

    //insert folder name
    cy.get("[data-testid='upload-folder-input']")
      .find("input")
      .type(folderName);

      //add the file
    cy.get("[data-testid='select-files-input']")
      .invoke("show")
      .selectFile(Cypress.config("textFileLocation") + fileName + ".txt");
    cy.wait(1000);

    //start upload
    cy.get("[data-testid='start-upload']")
      .should("not.have.class", "disabled")
      .click();
    cy.wait(3000);

    //close toast
    cy.get('[data-testid="close-upload-toast"]')
      .should("exist")
      .click();

    cy.wait(3000);

    cy.contains(folderName).should("exist");

    //TEST SERVICE WORKER DOWNLOAD
    if (useServiceWorker) {
      cy.log("Testing archive download with service worker");

      //click download
      cy.contains(folderName)
        .parent()
        .parent()
        .parent()
        .find("[testid='download-container']")
        .click({ force: true });
      cy.wait(3000);

      //check that archive exists
      cy.readFile(Cypress.config("downloadsFolder") + "/" + folderName + ".tar");

      //extract file
      cy.task("extractArchive",
        { directory: Cypress.config("downloadsFolder"), archive: folderName + ".tar" }
      );
      cy.wait(3000);

      //check if extraction successful
      cy.readFile(Cypress.config("downloadsFolder") + "/" + fileName + ".txt");

      //compare checksums and content with upload file
      cy.fixture(
        "downloads/" + fileName + ".txt",
        "utf-8"
      ).then($contentOnExtract => {
        const hexHashDownload = SparkMD5.hash($contentOnExtract);

        expect(uploadedContent).to.eq($contentOnExtract);
        expect(hexHashUpload).to.eq(hexHashDownload);
      });
    }

    //TODO TEST DIRECT DOWNLOAD
    else {
      cy.log("Testing direct archive download");
    }
  });
});
