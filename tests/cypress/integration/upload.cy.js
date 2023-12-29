//upload

describe("Upload a file", function () {
  beforeEach(() => {
    cy.visit(Cypress.config("baseUrl"));
    cy.login(Cypress.env("username"), Cypress.env("password"));
    cy.generateFixture("text-file");
    cy.generateFixture("text-file-v2");
  });

  //Happy scenarios
  //upload from folder
  it("Upload file from the folder page", () => {
    //create a unique name
    const folderName = Math.random().toString(36).substring(2, 7);
    cy.addFolder(folderName);
    cy.wait(3000);
    cy.searchFolder(folderName);
    cy.get(".media-content").contains(folderName).click({ force: true });
    cy.wait(3000);

    //press upload button from folder
    cy.get('[data-testid="upload-file"]').click({ force: true });
    cy.wait(3000);

    //upload the fixture file
    cy.get(".upload-btn-wrapper")
      .find("input")
      .invoke("show")
      .selectFile(`cypress/fixtures/text-files/text-file.txt`);
    cy.wait(3000);
    cy.get(".upload-card > c-card-actions.hydrated > :nth-child(2)").click({
      force: true,
    });
    cy.wait(3000);

    //close the modal
    cy.get(".link-underline").click({ force: true });

    cy.reload();
    cy.wait(3000);

    //check if the file name is on the page
    cy.contains("text-file").should("exist");

    //delete the file by checkbox
    cy.deleteFileCheckbox("text-file");

    cy.wait(3000);
    cy.contains("This folder has no content.").should("exist");
  });

  //Upload from the main page
  //TODO: make it work the new way
  xit("Upload file from the main page, selecting folder with search field", () => {
    //create a unique name

    cy.get('[data-testid="upload-file"]').click({ force: true });
    cy.wait(3000);

    const folderName = Math.random().toString(36).substring(2, 7);

    cy.get(`[title="Folder name"]`)
      .eq(1)

      .click({ force: true })
      .type(folderName, { force: true });

    //upload the fixture file
    cy.get(".upload-btn-wrapper")
      .find("input")
      .invoke("show")
      .selectFile("cypress/fixtures/text-files/text-file.txt");
    cy.wait(3000);
    cy.get(".upload-card > c-card-actions.hydrated > :nth-child(2)").click({
      force: true,
    });
    cy.wait(3000);

    //close the modal
    cy.get(".toggle-notification > .mdi").click({ force: true });
    cy.wait(3000);
    //  cy.contains("Close").click({ force: true });
    // cy.wait(3000);
    // // cy.reload();

    //check if the file name is on the folder page
    cy.searchFolder(folderName);
    cy.get(".media-content").contains(folderName).click({ force: true });
    // cy.contains("View destination").click({ force: true });
    cy.wait(3000);
    // cy.reload();
    // cy.wait(3000);
    cy.contains("text-file").should("exist");

    // //delete the file
    // cy.deleteFileCheckbox("text-file");

    // cy.wait(3000);
    // cy.contains("This folder has no content.").should("exist");
  });

  it("Several files with different names can be uploaded to a folder at once", () => {
    //create a unique name
    const folderName = Math.random().toString(36).substring(2, 7);
    cy.addFolder(folderName);
    cy.wait(3000);
    cy.searchFolder(folderName);
    cy.get(".media-content").contains(folderName).click({ force: true });
    cy.wait(3000);

    //press upload button from folder
    cy.get('[data-testid="upload-file"]').click({ force: true });
    cy.wait(3000);

    // upload the first fixture file
    cy.get(".upload-btn-wrapper")
      .find("input")
      .invoke("show")
      .selectFile("cypress/fixtures/text-files/text-file.txt", {
        force: true,
      });
    cy.wait(3000);

    //upload another fixture file
    cy.get(".upload-btn-wrapper")
      .find("input")
      .invoke("show")
      .selectFile("cypress/fixtures/text-files/text-file-v2.txt");

    cy.wait(3000);
    cy.get(".upload-card > c-card-actions.hydrated > :nth-child(2)").click({
      force: true,
    });
    cy.wait(3000);

    //close the modal
    cy.get(".link-underline").click({ force: true });

    //check the success
    cy.reload();
    cy.wait(3000);
    cy.contains("text-file").should("exist");
    cy.contains("text-file-v2").should("exist");

    //delete the first file
    cy.deleteFileCheckbox("text-file-v2");

    cy.wait(3000);

    //delete the second file
    cy.deleteFileCheckbox("text-file");

    cy.wait(3000);
    cy.contains("This folder has no content.").should("exist");
  });

  it("Several files with different names can be uploaded to a folder one by one", () => {
    //create a unique name
    const folderName = Math.random().toString(36).substring(2, 7);
    cy.addFolder(folderName);
    cy.wait(3000);
    cy.searchFolder(folderName);
    cy.get(".media-content").contains(folderName).click({ force: true });
    cy.wait(3000);

    //press upload button from folder
    cy.get('[data-testid="upload-file"]').click({ force: true });
    cy.wait(3000);

    //upload the first fixture file
    cy.get(".upload-btn-wrapper")
      .find("input")
      .invoke("show")
      .selectFile("cypress/fixtures/text-files/text-file.txt");
    cy.wait(3000);

    cy.get(".upload-card > c-card-actions.hydrated > :nth-child(2)").click({
      force: true,
    });
    cy.wait(3000);

    //close the modal
    cy.get(".link-underline").click();

    //press upload button from folder
    cy.get('[data-testid="upload-file"]').click({ force: true });
    cy.wait(3000);

    //upload another fixture file
    cy.get(".upload-btn-wrapper")
      .find("input")
      .invoke("show")
      .selectFile("cypress/fixtures/text-files/text-file-v2.txt");

    cy.wait(3000);
    cy.get(".upload-card > c-card-actions.hydrated > :nth-child(2)").click({
      force: true,
    });
    cy.wait(3000);

    //close the modal
    cy.get(".link-underline").click();

    //check the success
    cy.reload();
    cy.wait(3000);
    cy.contains("text-file").should("exist");
    cy.contains("text-file-v2").should("exist");

    //delete the first file
    cy.deleteFileCheckbox("text-file-v2");

    cy.wait(3000);

    //delete the second file
    cy.deleteFileCheckbox("text-file");

    cy.wait(3000);
    cy.contains("This folder has no content.").should("exist");
  });

  //Unhappy scenarios
  it("Two files with the same name can not be uploaded to a folder", () => {
    //create a unique name
    const folderName = Math.random().toString(36).substring(2, 7);
    cy.addFolder(folderName);
    cy.wait(3000);
    cy.searchFolder(folderName);
    cy.get(".media-content").contains(folderName).click({ force: true });
    cy.wait(3000);

    //press upload button from folder
    cy.get('[data-testid="upload-file"]').click({ force: true });
    cy.wait(3000);

    //upload the fixture file
    cy.get(".upload-btn-wrapper")
      .find("input")
      .invoke("show")
      .selectFile("cypress/fixtures/text-files/text-file.txt");
    cy.wait(3000);

    //try to upload the same file second time
    cy.get(".upload-btn-wrapper")
      .find("input")
      .invoke("show")
      .selectFile("cypress/fixtures/text-files/text-file.txt");
    cy.wait(3000);
    cy.contains("Files with the same paths are not allowed");
  });
});
