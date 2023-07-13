describe("Upload a file", function () {
  beforeEach(() => {
    cy.visit(Cypress.config().baseUrl);
    cy.login(Cypress.env("username"), Cypress.env("password"));
  });

  //upload from folder
  xit("create folder, open folder, upload file, check xit is there,delete file", function () {
    //create a unique name
    const randomName = Math.random().toString(36).substring(2, 7);
    cy.addFolder(randomName);
    cy.wait(30000);
    cy.contains(randomName).click();
    cy.get('[data-testid="upload-file"]').click();

    //upload the fixture file
    cy.get(".upload-btn-wrapper")
      .find("input")
      .invoke("show")
      .selectFile("cypress/fixtures/text-files/text-file.txt");
    cy.get(".upload-card > c-card-actions.hydrated > :nth-child(2)").click();

    //TODO below wait times for file upload and deletion might be increased, to be sure

    cy.wait(15000);
    cy.get(".link-underline").click();
    //check if the file name is on the page
    cy.reload();
    cy.wait(15000);
    cy.contains("text-file").should("exist");

    //delete the file
    cy.contains("text-file")
      .parent()
      .parent()
      .find("td")
      .eq(5)
      .find("button")
      .eq(2)
      .click();

    //confirm deletion
    cy.get(
      "c-alert.hydrated > c-card-actions.hydrated > :nth-child(2)"
    ).click();
    cy.wait(10000);
    cy.contains("This folder has no content.").should("exist");

    //return to main page to delete the folder
    cy.get(
      '[href="/browse/swift/0997f0be2294404092dd981a826c6d4f"] > p'
    ).click();
    cy.wait(30000);

    // delete folder after checking xit is there
    cy.deleteFolder(randomName);
    cy.wait(10000);
    cy.reload();
    //wait for the DB to update
    cy.wait(40000);
    cy.contains(randomName).should("not.exist");
  });

  //Upload from the main page
  xit("create folder, click upload, choose folder, upload", () => {
    //create a unique name
    const randomName = Math.random().toString(36).substring(2, 7);
    cy.addFolder(randomName);
    cy.wait(30000);
    cy.get('[data-testid="upload-file"]').click({ force: true });
    cy.wait(10000);

    //trying to avoid '0x0' effective width and height error and type into input field
    cy.contains("Folder name")
      .parent()
      .find("input")
      .type(randomName, { force: true });
    //   });

    cy.get('[role="listbox"]').find("li").contains(randomName).click();

    //   upload the fixture file
    cy.get(".upload-btn-wrapper")
      .find("input")
      .invoke("show")
      .selectFile("cypress/fixtures/text-files/text-file.txt");
    cy.get(".upload-card > c-card-actions.hydrated > :nth-child(2)").click();
    cy.wait(5000);
    cy.get(".link-underline").click();

    //   check if the file name is on the page
    cy.reload();
    cy.wait(15000);
    cy.contains("text-file").should("exist");

    //delete the file
    cy.contains("text-file")
      .parent()
      .parent()
      .find("td")
      .eq(5)
      .find("button")
      .eq(2)
      .click();

    //confirm deletion
    cy.get(
      "c-alert.hydrated > c-card-actions.hydrated > :nth-child(2)"
    ).click();
    cy.wait(7000);
    cy.contains("This folder has no content.").should("exist");

    // delete folder
    cy.get(
      '[href="/browse/swift/0997f0be2294404092dd981a826c6d4f"] > p'
    ).click();
    cy.wait(30000);

    // delete folder after checking xit is there
    cy.deleteFolder(randomName);
    cy.reload();
    //wait for the DB to update
    cy.wait(40000);
    cy.contains(randomName).should("not.exist");
  });

  xit("New file with not unique name can not be uploaded to a folder", () => {
    //Upload
    //create a unique name
    const randomName = Math.random().toString(36).substring(2, 7);
    cy.addFolder(randomName);
    cy.wait(30000);
    cy.get('[data-testid="upload-file"]').click({ force: true });
    cy.wait(10000);

    //trying to avoid '0x0' effective width and height error and type into input field
    cy.contains("Folder name")
      .parent()
      .find("input")
      .type(randomName, { force: true });

    cy.get('[role="listbox"]').find("li").contains(randomName).click();

    //   upload the fixture file
    cy.get(".upload-btn-wrapper")
      .find("input")
      .invoke("show")
      .selectFile("cypress/fixtures/text-files/text-file.txt");

    //try to upload the same file second time
    cy.get(".upload-btn-wrapper")
      .find("input")
      .invoke("show")
      .selectFile("cypress/fixtures/text-files/text-file.txt");
    cy.get(".duplicate-notification").should("exist");

    //close upload window
    cy.get(".upload-card > c-card-actions.hydrated > :nth-child(1)").click();
    cy.wait(10000);

    //TODO -- OR upload the first file and delete the file and the folder
    cy.deleteFolder(randomName);
  });

  xit("Several files with different names can be uploaded to a folder", () => {
    //Upload
    //create a unique name
    const randomName = Math.random().toString(36).substring(2, 7);
    cy.addFolder(randomName);
    cy.wait(30000);
    cy.get('[data-testid="upload-file"]').click({ force: true });
    cy.wait(10000);

    //trying to avoid '0x0' effective width and height error and type into input field
    cy.contains("Folder name")
      .parent()
      .find("input")
      .type(randomName, { force: true });

    cy.get('[role="listbox"]').find("li").contains(randomName).click();

    //   upload the fixture file
    cy.get(".upload-btn-wrapper")
      .find("input")
      .invoke("show")
      .selectFile("cypress/fixtures/text-files/text-file.txt");

    //upload another file
    //check the success
  });
});
