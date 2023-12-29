//container

//A container with a unique name is created and visible

describe("Creates and shows a container with a random unique name", function () {
  it("should show unique container in swift project", () => {
    cy.visit(Cypress.config().baseUrl);
    cy.login(Cypress.env("username"), Cypress.env("password"));

    //create a unique name
    const folderName = Math.random().toString(36).substring(2, 7);

    // add new folder with a unique name and show it
    cy.addFolder(folderName);
    cy.wait(3000);

    //check the folder exists with search field
    cy.searchFolder(folderName);
    cy.get(".media-content").contains(folderName).should("exist");
  });
});

//A container with not unique name can't be created
describe("Creating more than 1 container with the same name is not possible in a project", function () {
  it("should not add not unique container into swift project", () => {
    cy.visit(Cypress.config().baseUrl);
    cy.login(Cypress.env("username"), Cypress.env("password"));

    //create a unique name
    const folderName = Math.random().toString(36).substring(2, 7);

    // add new folder with a unique name and show it
    cy.addFolder(folderName);

    cy.wait(3000);

    cy.addFolder(folderName);

    //the name should be in use already
    cy.contains("already in use");
    cy.get(".add-folder > c-card-actions.hydrated > :nth-child(1)").click();
  });
});

//Several containers are created and are visible

describe("Several containers with different names are created and visible", () => {
  before(() => {
    cy.visit(Cypress.config().baseUrl);
    cy.login(Cypress.env("username"), Cypress.env("password"));
  });

  it("Several containers are visible", function () {
    //create two folders
    const nameOne = Math.random().toString(36).substring(2, 7);
    const nameTwo = Math.random().toString(36).substring(2, 7);

    cy.addFolder(nameOne);
    cy.wait(3000);

    //check the folder 1 exists with search field
    cy.searchFolder(nameOne);
    cy.wait(3000);
    cy.get(".media-content").contains(nameOne).should("exist");

    cy.addFolder(nameTwo);
    cy.wait(3000);

    cy.reload();

    //check the folder 2 exists with search field
    cy.searchFolder(nameTwo);
    cy.wait(3000);
    cy.get(".media-content").contains(nameTwo).should("exist");

    //check there are multiple folders in the project
    cy.get("table")
      .find("a.icon", { timeout: "3000" })
      .should("have.length.greaterThan", 1);
  });
});

describe("A container can be deleted", () => {
  before(() => {
    cy.visit(Cypress.config().baseUrl);
    cy.login(Cypress.env("username"), Cypress.env("password"));
  });

  it("creates and deletes a container", function () {
    //create a unique name
    const folderName = Math.random().toString(36).substring(2, 7);

    // add new folder with a unique name and show it
    cy.addFolder(folderName);
    cy.wait(3000);

    //check the folder exists with search field
    cy.searchFolder(folderName);
    cy.get(".media-content").contains(folderName).should("exist");

    //check the folder exists, then delete
    cy.deleteFolder(folderName);
    cy.contains("Folder was deleted").should("exist");
    cy.wait(3000);

    //check it was deleted
    cy.reload();
    cy.wait(3000);
    cy.contains(folderName).should("not.exist");
  });
});
