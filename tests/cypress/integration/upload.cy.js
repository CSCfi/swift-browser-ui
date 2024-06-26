//upload

describe("Upload a file", function () {

  const file1 = "text-file-1";
  const file2 = "text-file-2";
  const fileLocation = Cypress.config("textFileLocation");

  beforeEach(() => {
    cy.deleteFixtures();
    cy.task("resetDB");
    cy.deleteDB();
    cy.visit(Cypress.config("baseUrl"));
    cy.login(Cypress.env("username"), Cypress.env("password"));
    cy.wait(3000);
    cy.generateFixture(file1);
    cy.generateFixture(file2);
  });

  //Happy scenarios
  //upload from folder
  it("Upload file from the folder page and delete it", () => {

    //create a folder and go inside it
    const folderName = Math.random().toString(36).substring(2, 7);
    cy.addFolder(folderName);
    cy.wait(3000);

    cy.searchFolder(folderName);
    cy.get("[data-testid='search-result']")
      .contains(folderName)
      .click({ force: true });
    cy.wait(5000);

    //upload file from destination folder
    cy.uploadFileFromFolder(file1);

    //close upload toast
    cy.get("[data-testid='close-upload-toast']")
      .should("exist")
      .click();
    cy.wait(3000);

    //check if the file name is on the page
    cy.contains(file1).should("exist");

    //delete the file by checkbox
    cy.deleteFileCheckbox(file1);
    cy.wait(3000);

    cy.get("[data-testid='object-table']")
      .invoke("attr", "no-data-text")
      .then(($value) => {
        cy.contains($value).should("exist");
      })
  });

  //Upload from the main page
  it("Upload file from the main page to a new folder", () => {

    //upload file and create a folder at the same time
    const folderName = Math.random().toString(36).substring(2, 7);
    cy.uploadFileFromMain(folderName, file1);

    //close upload toast
    cy.get("[data-testid='close-upload-toast']")
      .should("exist")
      .click();
    cy.wait(3000);

    //check if the file name is on the folder page
    cy.searchFolder(folderName);
    cy.get("[data-testid='search-result']")
      .contains(folderName)
      .click({ force: true });
    cy.wait(5000);

    cy.contains(file1).should("exist");
  });

  it("Several files with different names can be uploaded to a folder at once", () => {

    //open upload modal
    cy.get("[data-testid='upload-file']").click();
    cy.wait(3000);

    //add folder name
    const folderName = Math.random().toString(36).substring(2, 7);
    cy.get("[data-testid='upload-folder-input']")
      .find("input")
      .type(folderName);

    //add the fixture files
    cy.get("[data-testid='select-files-input']")
      .invoke("show")
      .selectFile(fileLocation + file1 + ".txt");
    cy.wait(3000);

    cy.get("[data-testid='select-files-input']")
      .invoke("show")
      .selectFile(fileLocation + file2 + ".txt");
    cy.wait(3000);

    //start upload
    cy.get("[data-testid='start-upload']")
      .should("not.have.class", "disabled")
      .click();
    cy.wait(1000);

    //view destination folder
    cy.get("a.link-underline").click();
    cy.wait(5000);

    //close upload toast
    cy.get("[data-testid='close-upload-toast']")
      .should("exist")
      .click();

    cy.contains(file1).should("exist");
    cy.contains(file2).should("exist");
  });

  it("Several files with different names can be uploaded to a folder one by one and deleted", () => {

    //create a unique name
    const folderName = Math.random().toString(36).substring(2, 7);
    cy.addFolder(folderName);
    cy.wait(3000);

    //access folder
    cy.searchFolder(folderName);
    cy.get("[data-testid='search-result']")
      .contains(folderName)
      .click({ force: true });
    cy.wait(5000);

    //upload first file
    cy.uploadFileFromFolder(file1);

    //close toast
    cy.get("[data-testid='close-upload-toast']")
      .should("exist")
      .click();

    //upload second file
    cy.uploadFileFromFolder(file2);

    //close toast
    cy.get("[data-testid='close-upload-toast']")
      .should("exist")
      .click();

    //check the success
    cy.contains(file1).should("exist");
    cy.contains(file2).should("exist");

    //delete both files
    cy.deleteFilesOnPageCheckbox();
    cy.wait(3000);

    cy.get("[data-testid='object-table']")
      .invoke("attr", "no-data-text")
      .then(($value) => {
        cy.contains($value).should("exist");
      })
  });

  //Unhappy scenarios
  it("Two files with the same name can not be uploaded to a folder at the same time", () => {

    //open upload modal
    cy.get("[data-testid='upload-file']").click({ force: true });
    cy.wait(3000);

    //check that modal opened
    cy.get("[data-testid='upload-modal']").should("be.visible");

    //create and insert new folder name
    const folderName = Math.random().toString(36).substring(2, 7);

    cy.get("[data-testid='upload-folder-input'")
      .find("input")
      .type(folderName);

    //add the fixture file
    cy.get("[data-testid='select-files-input']")
      .invoke("show")
      .selectFile(fileLocation + file1 + ".txt")
    cy.wait(2000);

    //try to add the same file second time
    cy.get("[data-testid='select-files-input']")
      .invoke("show")
      .selectFile(fileLocation + file1 + ".txt")
    cy.wait(1000);

    //check for error alert
    cy.get("[data-testid='drop-files-error']")
      .should("be.visible");

    //check that file is added once
    cy.get("[data-testid='upload-modal']")
      .find("tr")
      .filter(`:contains(${file1})`)
      .should("have.length", 1);
  });
});
