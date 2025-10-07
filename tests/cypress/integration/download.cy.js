//download

import SparkMD5 from "../../../swift_browser_ui_frontend/node_modules/spark-md5";

describe("Downloads file/bucket, verifies content and checksum", function () {
  const useServiceWorker =
    "serviceWorker" in navigator && window.showSaveFilePicker === undefined;
  const fileName = Math.random().toString(36).substring(2, 7);

  beforeEach(() => {
    cy.deleteFixtures();
    cy.task("resetDB");
    cy.deleteDB();
    cy.visit(Cypress.config("baseUrl"));
    cy.login(Cypress.env("username"), Cypress.env("password"));
    cy.generateFixture(fileName);
  });

  it("should download a file", () => {
    //create a bucket
    const bucketName = Math.random().toString(36).substring(2, 7);
    cy.addBucket(bucketName);
    cy.wait(3000);

    //access bucket
    cy.searchBucket(bucketName);
    cy.get("[data-testid='search-result']")
      .contains(bucketName)
      .click({ force: true });
    cy.wait(5000);

    cy.fixture("text-files/" + fileName + ".txt", "utf-8").then(
      ($contentOnUpload) => {
        //check file hash before upload (encryption)
        const hexHashUpload = SparkMD5.hash($contentOnUpload);
        cy.log("Upload hash", hexHashUpload);

        //upload the fixture file
        cy.uploadFileFromBucket(fileName);

        //close toast
        cy.get('[data-testid="close-upload-toast"]').should("exist").click();

        //check if the file name is on the page
        cy.contains(fileName).should("exist");

        //click on download button
        cy.contains(fileName)
          .parent()
          .parent()
          .find("[testid='download-object']")
          .as("download")
          .click({ force: true });

        cy.wait(3000);

        if (useServiceWorker) {
          //TEST SERVICE WORKER DOWNLOAD
          cy.log("Testing file download with service worker");
        } else {
          //TEST DIRECT DOWNLOAD
          //Since we cannot directly interact with user's file system through Cypress
          //testing is done through OPFS which doesn't have strict security checks
          cy.log("Testing direct file download");

          cy.getFileContentFromOPFS(fileName + ".txt").then(
            ($contentOnDownload) => {
              //create a fixture file from file content in OPFS
              cy.writeFile(
                Cypress.config("downloadsFolder") + "/" + fileName + ".txt",
                $contentOnDownload
              );
            }
          );
        }

        //read fails if file doesn't exist
        cy.readFile(
          Cypress.config("downloadsFolder") + "/" + fileName + ".txt"
        );

        // Check file hash after download
        cy.fixture("/downloads/" + fileName + ".txt", "utf-8").then(
          ($contentOnDownload) => {
            const hexHashDownload = SparkMD5.hash($contentOnDownload);
            cy.log("Download hash", hexHashDownload);

            //match full file content before and after
            expect($contentOnUpload).to.eq($contentOnDownload);

            //match file checksum before and after
            expect(hexHashUpload).to.eq(hexHashDownload);
          }
        );
      }
    );
  });

  it("should download an archive", () => {
    const bucketName = Math.random().toString(36).substring(2, 7);
    //check file hashes before upload
    let hexHashUpload;

    cy.fixture("text-files/" + fileName + ".txt", "utf-8").then(
      ($contentOnUpload) => {
        //check file hash before upload (encryption)
        hexHashUpload = SparkMD5.hash($contentOnUpload);

        //open upload modal
        cy.get("[data-testid='upload-file']").click();
        cy.wait(3000);

        //check that modal opened
        cy.get("[data-testid='upload-modal']").should("be.visible");

        //insert bucket name
        cy.get("[data-testid='upload-bucket-input']")
          .find("input")
          .type(bucketName);

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
        cy.get('[data-testid="close-upload-toast"]').should("exist").click();

        cy.wait(3000);

        cy.contains(bucketName).should("exist");

        //click download
        cy.contains(bucketName)
          .parent()
          .parent()
          .parent()
          .find("[testid='download-container']")
          .click({ force: true });

        cy.wait(3000);

        if (useServiceWorker) {
          //TEST SERVICE WORKER DOWNLOAD
          cy.log("Testing archive download with service worker");
        } else {
          //TEST DIRECT DOWNLOAD
          cy.log("Testing direct archive download");

          cy.getFileContentFromOPFS(bucketName + "_download.tar").then(
            ($contentOnDownload) => {
              //need to create a fixture file from file content in OPFS
              cy.writeFile(
                Cypress.config("downloadsFolder") +
                  "/" +
                  bucketName +
                  "_download.tar",
                $contentOnDownload
              );
            }
          );
        }

        const downloadName =
          bucketName + (useServiceWorker ? ".tar" : "_download.tar");
        //check that archive exists
        cy.readFile(Cypress.config("downloadsFolder") + "/" + downloadName);

        //extract file
        cy.task("extractArchive", {
          directory: Cypress.config("downloadsFolder"),
          archive: downloadName,
        });
        cy.wait(3000);

        //check if extraction successful
        cy.readFile(
          Cypress.config("downloadsFolder") + "/" + fileName + ".txt"
        );

        //compare checksums and content with upload file
        cy.fixture("/downloads/" + fileName + ".txt", "utf-8").then(
          ($contentOnExtract) => {
            const hexHashDownload = SparkMD5.hash($contentOnExtract);
            expect($contentOnUpload).to.eq($contentOnExtract);
            expect(hexHashUpload).to.eq(hexHashDownload);
          }
        );
      }
    );
  });
});
