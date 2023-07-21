describe("Upload a file", function () {
  beforeEach(() => {
    cy.visit(Cypress.config("baseUrl"));
    cy.login(Cypress.env("username"), Cypress.env("password"));
    cy.generateFixture("text-file");
    cy.generateFixture("text-file-v2");
  });

  //upload from folder
  it("Upload file from the folder page", function () {
    //create a unique name
    const folderName = Math.random().toString(36).substring(2, 7);
    cy.addFolder(folderName);
    cy.wait(11000);
    cy.searchFolder(folderName);
    cy.get(".media-content").contains(folderName).click({ force: true });
    cy.wait(5000);

    //press upload button from folder
    cy.get('[data-testid="upload-file"]').click();
    cy.wait(11000);

    //upload the fixture file
    cy.get(".upload-btn-wrapper")
      .find("input")
      .invoke("show")
      .selectFile(`cypress/fixtures/text-files/text-file.txt`);
    cy.wait(15000);
    cy.get(".upload-card > c-card-actions.hydrated > :nth-child(2)").click();
    cy.wait(15000);

    //close the modal
    cy.get(".link-underline").click();

    cy.reload();
    cy.wait(15000);

    //check if the file name is on the page
    cy.contains("text-file").should("exist");

    //delete the file by checkbox

    cy.contains("text-file")
      .parent()
      .parent()
      .find("td")
      .eq(5)
      .find("button")
      .eq(2)
      .click({ force: true });
    cy.get("c-alert.hydrated > c-card-actions.hydrated > :nth-child(2)").click({
      force: true,
    });

    cy.wait(15000);
    cy.contains("This folder has no content.").should("exist");
  });

  //Upload from the main page
  it("Upload file from the main page, selecting folder with search field", () => {
    //create a unique name
    const randomName = Math.random().toString(36).substring(2, 7);
    cy.addFolder(randomName);
    cy.wait(10000);
    cy.get('[data-testid="upload-file"]').click({ force: true });
    cy.wait(10000);

    //trying to avoid '0x0' effective width and height error and type into input field
    cy.contains("Folder name")
      .parent()
      .find("input")
      .type(randomName, { force: true });

    cy.get('[role="listbox"]').find("li").contains(randomName).click();
    cy.wait(15000);

    //   upload the fixture file
    cy.get(".upload-btn-wrapper")
      .find("input")
      .invoke("show")
      .selectFile("cypress/fixtures/text-files/text-file.txt");
    cy.wait(15000);
    cy.get(".upload-card > c-card-actions.hydrated > :nth-child(2)").click();
    cy.wait(15000);

    //close the modal
    cy.get(".link-underline").click();

    //   check if the file name is on the page
    cy.reload();
    cy.wait(15000);
    cy.contains("text-file").should("exist");

    //delete the file
    cy.deleteFileCheckbox("text-file");

    cy.wait(10000);
    cy.contains("This folder has no content.").should("exist");
  });

  it("Two files with the same name can not be uploaded to a folder", () => {
    //create a unique name
    const randomName = Math.random().toString(36).substring(2, 7);
    cy.addFolder(randomName);
    cy.wait(10000);
    cy.get('[data-testid="upload-file"]').click({ force: true });
    cy.wait(10000);

    //trying to avoid '0x0' effective width and height error and type into input field
    cy.contains("Folder name")
      .parent()
      .find("input")
      .type(randomName, { force: true });

    cy.get('[role="listbox"]').find("li").contains(randomName).click();
    cy.wait(15000);

    //   upload the fixture file
    cy.get(".upload-btn-wrapper")
      .find("input")
      .invoke("show")
      .selectFile("cypress/fixtures/text-files/text-file.txt");
    cy.wait(10000);

    //try to upload the same file second time
    cy.get(".upload-btn-wrapper")
      .find("input")
      .invoke("show")
      .selectFile("cypress/fixtures/text-files/text-file.txt");
    cy.wait(10000);
    cy.get(".duplicate-notification").should("exist");
  });

  it("Several files with different names can be uploaded to a folder at once", () => {
    //create a unique name
    const randomName = Math.random().toString(36).substring(2, 7);
    cy.addFolder(randomName);
    cy.wait(10000);
    cy.get('[data-testid="upload-file"]').click({ force: true });
    cy.wait(10000);

    //trying to avoid '0x0' effective width and height error and type into input field
    cy.contains("Folder name")
      .parent()
      .find("input")
      .type(randomName, { force: true });

    cy.get('[role="listbox"]').find("li").contains(randomName).click();
    cy.wait(15000);

    // upload the first fixture file
    cy.get(".upload-btn-wrapper")
      .find("input")
      .invoke("show")
      .selectFile("cypress/fixtures/text-files/text-file.txt");
    cy.wait(15000);

    //upload another fixture file
    cy.get(".upload-btn-wrapper")
      .find("input")
      .invoke("show")
      .selectFile("cypress/fixtures/text-files/text-file-v2.txt");

    cy.wait(15000);
    cy.get(".upload-card > c-card-actions.hydrated > :nth-child(2)").click();
    cy.wait(15000);

    //close the modal
    cy.get(".link-underline").click();

    //check the success
    cy.reload();
    cy.wait(13000);
    cy.contains("text-file").should("exist");
    cy.contains("text-file-v2").should("exist");

    //delete the first file
    cy.deleteFileCheckbox("text-file-v2");

    cy.wait(10000);

    //delete the second file
    cy.deleteFileCheckbox("text-file");

    cy.wait(15000);
    cy.contains("This folder has no content.").should("exist");
  });

  it("Several files with different names can be uploaded to a folder one by one", () => {
    //create a unique name
    const folderName = Math.random().toString(36).substring(2, 7);
    cy.addFolder(folderName);
    cy.wait(11000);
    cy.searchFolder(folderName);
    cy.get(".media-content").contains(folderName).click({ force: true });
    cy.wait(5000);

    //press upload button from folder
    cy.get('[data-testid="upload-file"]').click();
    cy.wait(11000);

    // upload the first fixture file
    cy.get(".upload-btn-wrapper")
      .find("input")
      .invoke("show")
      .selectFile("cypress/fixtures/text-files/text-file.txt");
    cy.wait(15000);

    cy.wait(15000);
    cy.get(".upload-card > c-card-actions.hydrated > :nth-child(2)").click();
    cy.wait(15000);

    //close the modal
    cy.get(".toast-main > c-button.hydrated").click({ force: true });

    //press upload button from folder
    cy.get('[data-testid="upload-file"]').click();
    cy.wait(11000);

    //upload another fixture file
    cy.get(".upload-btn-wrapper")
      .find("input")
      .invoke("show")
      .selectFile("cypress/fixtures/text-files/text-file-v2.txt");

    cy.wait(15000);
    cy.get(".upload-card > c-card-actions.hydrated > :nth-child(2)").click();
    cy.wait(15000);

    //close the modal
    cy.get(".toast-main > c-button.hydrated").click({ force: true });

    //check the success
    cy.reload();
    cy.wait(13000);
    cy.contains("text-file").should("exist");
    cy.contains("text-file-v2").should("exist");

    //delete the first file
    cy.deleteFileCheckbox("text-file-v2");

    cy.wait(10000);

    //delete the second file
    cy.deleteFileCheckbox("text-file");

    cy.wait(15000);
    cy.contains("This folder has no content.").should("exist");
  });
  //TODO: test for FAIL uploading files with the SAME path one by one (two different upload modals)

});
