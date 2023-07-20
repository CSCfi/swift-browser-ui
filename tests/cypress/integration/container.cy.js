//A container with a unique name is created and visible

describe("Creates and shows a container with a random unique name", function () {
  it("should show unique container in swift project", () => {
    cy.visit(Cypress.config().baseUrl);
    cy.login(Cypress.env("username"), Cypress.env("password"));

    //create a unique name
    const randomName = Math.random().toString(36).substring(2, 7);

    // add new folder with a unique name and show it
    cy.addFolder(randomName);
    cy.wait(5000);

    //check the folder exists with search field
    cy.searchFolder(randomName);
    cy.get(".media-content").contains(randomName).should("exist");
  });
});

//A container with not unique name can't be created

describe("Creating more than 1 container with the same name is not possible in a project", function () {
  it("should not add not unique container into swift project", () => {
    cy.visit(Cypress.config().baseUrl);
    cy.login(Cypress.env("username"), Cypress.env("password"));

    //create a unique name
    const randomName = Math.random().toString(36).substring(2, 7);

    // add new folder with a unique name and show it
    cy.addFolder(randomName);

    cy.wait(5000);

    cy.addFolder(randomName);

    //the name should be in use already
    cy.get('[data-testid="createModal-toasts"]').contains("already in use");
    cy.get(".add-folder > c-card-actions.hydrated > :nth-child(1)").click();
  });
});

//Several containers are created and are visible

describe("Several containers with different names are created and visible", () => {
  before(() => {
    cy.visit(Cypress.config().baseUrl);
    cy.login(Cypress.env("username"), Cypress.env("password"));
  });

  it.only("Several containers are visible", function () {
    //create two folders
    const nameOne = Math.random().toString(36).substring(2, 7);
    const nameTwo = Math.random().toString(36).substring(2, 7);

    cy.addFolder(nameOne);
    cy.wait(5000);

    //check the folder 1 exists with search field
    cy.searchFolder(nameOne);
    cy.wait(5000);
    cy.get(".media-content").contains(nameOne).should("exist");

    cy.addFolder(nameTwo);
    cy.wait(5000);

    cy.reload();

    //check the folder 2 exists with search field
    cy.searchFolder(nameTwo);
    cy.wait(5000);
    cy.get(".media-content").contains(nameTwo).should("exist");

    //check there are multiple folders in the project
    cy.get("table")
      .find("a.icon", { timeout: "5000" })
      .should("have.length.greaterThan", 1);
  });
});

describe("A container can be deleted", () => {
  before(() => {
    cy.visit(Cypress.config().baseUrl);
    cy.login(Cypress.env("username"), Cypress.env("password"));
  });

  it("creates and deletes a container", function () {
    //create a folder
    cy.addFolder("1111aaaa");
    cy.wait(5000);
    cy.contains("1111aaaa").should("exist");

    //check the folder exists, then delete
    cy.deleteFolder("1111aaaa");
    cy.wait(5000);

    //check it was deleted
    cy.contains("1111aaaa").should("not.exist");
  });
});
