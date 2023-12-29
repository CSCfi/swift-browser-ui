//download

// import SparkMD5 from "../../../swift_browser_ui_frontend/node_modules/spark-md5";

describe("Downloads a file, verifies content and checksum", function () {
  beforeEach(() => {
    cy.visit(Cypress.config("baseUrl"));
    cy.login(Cypress.env("username"), Cypress.env("password"));
  });

  //Cypress may not fully support the interactions with service workers and the showSaveFilePicker API (handleDownWorker) out of the box. Some other testing other than e2e might be required

  xit("should download a file", () => {
    //create folder
    const folderName = Math.random().toString(36).substring(2, 7);
    const fileName = Math.random().toString(36).substring(2, 7);
    cy.generateFixture(fileName);
    cy.addFolder(folderName);
    cy.wait(300);

    //access folder
    cy.searchFolder(folderName);
    cy.get(".media-content").contains(folderName).click({ force: true });
    cy.wait(3000);

    //upload file
    cy.get('[data-testid="upload-file"]').click();
    cy.wait(3000);

    cy.fixture(
      `../../../swift_browser_ui_frontend/cypress/fixtures/text-files/${fileName}.txt`,
      "utf-8"
    ).then((contentOnUpload) => {
      //check file hash before upload (encryption)
      var hexHashUpload = SparkMD5.hash(contentOnUpload);
      cy.log("Upload hash", hexHashUpload);

      //upload the fixture file
      cy.get(".upload-btn-wrapper")
        .find("input")
        .invoke("show")
        .selectFile(`cypress/fixtures/text-files/${fileName}.txt`);
      cy.wait(3000);
      cy.get(".upload-card > c-card-actions.hydrated > :nth-child(2)").click();
      cy.wait(3000);

      //close the modal
      cy.get(".link-underline").click();

      cy.reload();
      cy.wait(3000);

      //check if the file name is on the page
      cy.contains(fileName).should("exist");

      //Clicking download button in any of the cases does not download files, cypress warning "Requires user gesture"

      cy.window().then((win) => {
        // Stub showSaveFilePicker to return a Blob with file content
        cy.stub(win, "showSaveFilePicker")
          .as("showSaveFilePicker")
          .returns(
            Promise.resolve({
              createWritable: () => {
                // Initialize an empty ArrayBuffer to hold the file content
                const arrayBuffer = new ArrayBuffer(0);

                // Create a WritableStream to write data to the ArrayBuffer
                const writableStream = new WritableStream({
                  write: (chunk) => {
                    // Convert the chunk to an ArrayBuffer and concatenate it
                    const chunkArrayBuffer = new TextEncoder().encode(
                      chunk
                    ).buffer;
                    const newArrayBuffer = new ArrayBuffer(
                      arrayBuffer.byteLength + chunkArrayBuffer.byteLength
                    );
                    new Uint8Array(newArrayBuffer).set(
                      new Uint8Array(arrayBuffer),
                      0
                    );
                    new Uint8Array(newArrayBuffer).set(
                      new Uint8Array(chunkArrayBuffer),
                      arrayBuffer.byteLength
                    );
                    arrayBuffer = newArrayBuffer;
                  },
                });

                // Return the WritableStream
                return writableStream;
              },
              close: () => {
                // Save the ArrayBuffer as a Blob
                const blob = new Blob([arrayBuffer], { type: "text/plain" });

                // Save the Blob to the fixtures folder
                cy.writeFile(
                  `cypress/fixtures/text-files/${fileName}.txt`,
                  blob
                );
              },
            })
          );
      });
      //click on download button
      cy.contains(fileName)
        .parent()
        .parent()
        .find("td")
        .eq(5)
        .find("c-button")
        .eq(0)
        .click({ force: true });

      cy.get("@showSaveFilePicker")
        .should("have.been.calledOnce")
        .invoke("restore");

      //TODO: Bypass "user gesture" requirement for clicking download button

      //Check file content after download (decryption)
      cy.readFile(`cypress/downloads/${fileName}.txt`).should(
        "contain",
        "hits"
      );
      // //Check file hash after download
      // cy.fixture(
      //   `../../../swift_browser_ui_frontend/cypress/downloads/${fileName}.txt`,
      //   "utf-8"
      // ).then((contentOnDownload) => {
      //   var hexHashDownload = SparkMD5.hash(contentOnDownload);
      //   cy.log(hexHashDownload);

      //   //match full file content before and after
      //   expect(contentOnUpload).to.eq(contentOnDownload);

      //   //match file checksum before and after
      //   expect(hexHashUpload).to.eq(hexHashDownload);
      // });
    });
  });
});
