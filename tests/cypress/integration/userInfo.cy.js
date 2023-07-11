describe("Login and log out a user", function () {
  it("should login with username + password and get to /browse route and log out", () => {
    cy.login(" Log In with SSO ");

    cy.selectProject("service");

    cy.location("pathname").should("match", /browse\/swift\/[0-9a-f]{32}/);
    cy.logout();
  });

  it("should login user with Finnish to username + password and remember the selection", () => {
    cy.visit(Cypress.config().baseUrl);
    cy.changeLang("fi");

    cy.login(" Kirjaudu SSO:ta käyttäen ");

    cy.selectProject("service");

    cy.location("pathname").should("match", /browse\/swift\/[0-9a-f]{32}/);
    cy.navigateUserMenu("Kirjaudu ulos");
  });
});

describe("Switch Languages after login", function () {
  beforeEach(function () {
    cy.visit(Cypress.config().baseUrl);
    cy.login(" Log In with SSO ");
  });

  afterEach(function () {
    cy.navigateUserMenu("Kirjaudu ulos");
  });

  it("should login the user with English but switch to Finnish", () => {
    cy.changeLang("fi");
    cy.get('[data-testid="project-selector"]')
      .find("label")
      .contains("Valitse projekti");
    cy.get("#searchbox")
      .invoke("attr", "placeholder")
      .should("contain", "Etsi nimellä");
  });
});

describe("Switch Languages after login", function () {
  beforeEach(function () {
    cy.visit(Cypress.config().baseUrl);
    cy.login(" Log In with SSO ");
  });

  afterEach(function () {
    cy.navigateUserMenu("Kirjaudu ulos");
  });

  it("should login the user with English but switch to Finnish", () => {
    cy.changeLang("fi");
    cy.get('[data-testid="project-selector"]')
      .find("label")
      .contains("Valitse projekti");
    cy.get("#searchbox")
      .invoke("attr", "placeholder")
      .should("contain", "Etsi nimellä");
  });
});

describe("Display mobile navigation on small resolution", function () {
  beforeEach(function () {
    cy.viewport(720, 1280);
    cy.visit(Cypress.config().baseUrl);
    cy.login(" Log In with SSO ");
  });

  afterEach(function () {
    cy.get("c-navigationbutton").click();
    cy.get("c-sidenavigationitem").contains(Cypress.env("username")).click();
    cy.get('[data-testid="logout"]').click();
  });

  it("should change language within mobile navigation", function () {
    cy.get("c-navigationbutton").click();
    cy.get("c-sidenavigationitem").contains("In English").click();
    cy.get("c-subnavigationitem").contains("Suomeksi").click();
    cy.get('[data-testid="project-selector"]')
      .find("label")
      .contains("Valitse projekti");
  });
});
