//A container with a unique name is created and visible

describe("Creates and shows a container with unique name, checks existence", function () {
  it("should show unique container in swift project", () => {
    cy.visit(Cypress.config().baseUrl);
    cy.deleteDB();
    cy.login(Cypress.env("username"), Cypress.env("password"));

    //create a unique name
    const randomName = Math.random().toString(36).substring(2, 7);

    // add new folder with a unique name and show it
    cy.addFolder(randomName);
    cy.contains(randomName, { timeout: 45000 }).should("exist");

    // delete folder after checking it is there
    cy.deleteFolder(randomName);
    cy.wait(5000);
    cy.reload();
    //wait for the DB to update
    cy.wait(35000);
    cy.contains(randomName).should("not.exist");

    //TODO: is it possible to check folder deletion by intercepting network requests and responses (204 DELETE status?)
  });
});

//A container with not unique name can't be created

describe("Does not create one more container with not unique name", function () {
  it("should not add not unique container into swift project", () => {
    cy.visit(Cypress.config().baseUrl);
    cy.deleteDB();
    cy.login(Cypress.env("username"), Cypress.env("password"));

    //create a unique name
    const randomName = Math.random().toString(36).substring(2, 7);

    // add new folder with a unique name and show it
    cy.addFolder(randomName);

    cy.wait(30000);

    cy.addFolder(randomName);

    //the name should be in use already
    cy.get('[data-testid="createModal-toasts"]').contains("already in use");
    cy.get(".add-folder > c-card-actions.hydrated > :nth-child(1)").click();

    // delete folder after checking it is there
    cy.deleteFolder(randomName);
    cy.wait(5000);
    cy.reload();
    //wait for the DB to update
    cy.wait(35000);
    cy.contains(randomName).should("not.exist");
  });
});

//A container with predefined name can be created and is visible

describe("Creates container with predefined name, checks existence, deletes it, checks non-existence", function () {
  it("creates and shows container, after deletion it is not visible", () => {
    cy.visit(Cypress.config().baseUrl);
    cy.deleteDB();
    cy.login(Cypress.env("username"), Cypress.env("password"));

    //create a predefined name
    const definedName = "predef_12346";

    // add new folder with a predefined name and show it
    cy.addFolder(definedName);
    cy.wait(30000);
    cy.contains(definedName, { timeout: 40000 }).should("exist");

    // delete folder after checking it is there
    cy.deleteFolder(definedName);
    cy.wait(5000);
    cy.reload();

    //wait for the DB to update
    cy.wait(35000);
    cy.contains(definedName).should("not.exist");
  });
});

//Several containers are created and are visible

describe("Should show several containers", () => {
  before(() => {
    cy.visit(Cypress.config().baseUrl);
    cy.login(Cypress.env("username"), Cypress.env("password"));
  });

  it("Several containers are visible", function () {
    //create two folders
    const nameOne = Math.random().toString(36).substring(2, 7);
    const nameTwo = Math.random().toString(36).substring(2, 7);

    cy.addFolder(nameOne);
    cy.addFolder(nameTwo);

    cy.reload();
    //wait for all folders to load
    cy.wait(20000);
    cy.get("table")
      .find("a.icon", { timeout: "30000" })
      .should("have.length.greaterThan", 1);
  });
});

//Folder search from main page

describe("Should perform folder search", () => {
  before(() => {
    cy.visit(Cypress.config().baseUrl);
    cy.login(Cypress.env("username"), Cypress.env("password"));
  });

  it("finding a folder via search field", function () {
    //create a unique name
    const randomName = Math.random().toString(36).substring(2, 7);

    // add new folder with a unique name and show it
    cy.addFolder(randomName);
    cy.get('[data-testid="create-folder"]', { timeout: 40000 }).click();

    cy.get(".c-input-menu__input")
      .find("input")
      .eq(0)
      .invoke("show")
      .type(randomName, { force: true });
  });

  //TODO select folder in search
});
