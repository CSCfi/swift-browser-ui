//container

describe("Create a container", function () {

  beforeEach(() => {
    cy.task("resetDB");
    cy.deleteDB();
    cy.visit(Cypress.config("baseUrl"));
    cy.login(Cypress.env("username"), Cypress.env("password"));
  });

  it("Creates a container with a random unique name and deletes it", () => {

    //create a unique name
    const folderName = Math.random().toString(36).substring(2, 7);

    // add new folder with a unique name and show it
    cy.addFolder(folderName);
    cy.wait(3000);

    //check the folder exists with search field
    cy.searchFolder(folderName);
    cy.get("[data-testid='search-result']")
      .contains(folderName)
      .should("exist");

    //then delete container
    cy.deleteFolder(folderName);
    cy.wait(1000);

    cy.get("[data-testid='container-toasts']")
      .find("c-toast")
      .should("have.class", "success");

    //check it was deleted
    cy.reload();
    cy.wait(3000);
    cy.contains(folderName).should("not.exist");
  });

  it("Several containers with different names are created and visible", function () {
    //create two folders
    const nameOne = Math.random().toString(36).substring(2, 7);
    const nameTwo = Math.random().toString(36).substring(2, 7);

    cy.addFolder(nameOne);
    cy.wait(3000);

    //check the folder 1 exists with search field
    cy.searchFolder(nameOne);
    cy.wait(3000);
    cy.get("[data-testid='search-result']")
      .contains(nameOne)
      .should("exist");

    cy.addFolder(nameTwo);
    cy.reload();
    cy.wait(3000);

    //check the folder 2 exists with search field
    cy.searchFolder(nameTwo);
    cy.wait(3000);
    cy.get("[data-testid='search-result']")
      .contains(nameTwo)
      .should("exist");

    //check there are multiple folders in the project
    cy.get("[data-testid='container-table']")
      .find("c-link")
      .should("have.length.gte", 2); //check
  });

  it("Creating more than 1 container with the same name is not possible in a project", () => {
    cy.visit(Cypress.config().baseUrl);
    cy.login(Cypress.env("username"), Cypress.env("password"));

    //create a unique name
    const folderName = Math.random().toString(36).substring(2, 7);

    // add new folder with a unique name and show it
    cy.addFolder(folderName);
    cy.wait(3000);

    cy.addFolder(folderName);

    //folder name input field should have a validation error
    cy.get("[data-testid='create-folder-modal']")
      .find("c-message")
      .should("be.visible");
    cy.get("[data-testid='cancel-save-folder']").click();
  });
});
