// successfull login with correct login and password

describe("Login a user", function () {
  beforeEach(() => {
    cy.visit(Cypress.config().baseUrl);
  });

  it("Login button redirects to login page", () => {
    cy.get("c-login-card-actions.hydrated > .hydrated").click();
    cy.url().should("include", "/login/");
  });

  it("Login with correct credentials redirects to project browsing page", () => {
    cy.login(Cypress.env("username"), Cypress.env("password"));
    cy.url().should("include", "browse");
    cy.get(".select-project").contains("Select");
    cy.getCookie("SWIFT_UI_SESSION").should("exist");
    cy.getCookie("OBJ_UI_LANG").should("have.property", "value", "en");
  });
});

// successful login with changing languages before pressing 'Login with SSO'

describe("Switch language EN (default) to FI upon selection before login", function () {
  it("Upon login languages can be switched, visible in cookies", () => {
    cy.visit(Cypress.config().baseUrl);
    cy.getCookie("OBJ_UI_LANG").should("have.property", "value", "en");
    cy.get('[data-testid="language-selector"]').click();
    cy.switchLang("Suomeksi");
    cy.login(Cypress.env("username"), Cypress.env("password"));
    cy.getCookie("OBJ_UI_LANG").should("have.property", "value", "fi");
    cy.get('[data-testid="language-selector"] > .menu-active').should(
      "contain",
      "Suomeksi"
    );
  });
});

// unsuccessful login where password and or login are incorrect or empty

describe("Displays errors if login goes wrong", function () {
  beforeEach(() => {
    cy.visit(Cypress.config().baseUrl);
  });

  it("username is incorrect", () => {
    cy.login(Cypress.env("wrongusername"), Cypress.env("password"));
    cy.url().should("include", "credentials");
    cy.get("c-card-title.hydrated").should("contain", "401");
    cy.get("c-card-content.hydrated").should(
      "contain",
      "The action requested requires logging in, or the log in credentials were incorrect"
    );
  });

  it("password is incorrect", () => {
    cy.login(Cypress.env("username"), Cypress.env("wrongpassword"));
    cy.url().should("include", "credentials");
    cy.get("c-card-title.hydrated").should("contain", "401");
    cy.get("c-card-content.hydrated").should(
      "contain",
      "The action requested requires logging in, or the log in credentials were incorrect"
    );
  });

  it("username is empty", () => {
    cy.get("c-login-card-actions.hydrated > .hydrated").click();
    cy.url().should("include", "/login/");
    cy.get('[type="password"]').type(Cypress.env("password"));
    cy.get('#classicform > [type="submit"]').click();
    cy.url().should("include", "credentials");
    cy.get("c-card-title.hydrated").should("contain", "400");
    cy.get("c-card-content.hydrated").should(
      "contain",
      "missing password and/or username"
    );
  });

  it("password is empty", () => {
    cy.get("c-login-card-actions.hydrated > .hydrated").click();
    cy.url().should("include", "/login/");
    cy.get('#classicform > [type="text"]').type(Cypress.env("username"));
    cy.get('#classicform > [type="submit"]').click();
    cy.url().should("include", "credentials");
    cy.get("c-card-title.hydrated").should("contain", "401");
    cy.get("c-card-content.hydrated").should(
      "contain",
      "The action requested requires logging in, or the log in credentials were incorrect"
    );
  });

  it("both input fields empty ", () => {
    cy.get("c-login-card-actions.hydrated > .hydrated").click();
    cy.url().should("include", "/login/");
    cy.get('#classicform > [type="submit"]').click();
    cy.url().should("include", "credentials");
    cy.get("c-card-title.hydrated").should("contain", "400");
    cy.get("c-card-content.hydrated").should(
      "contain",
      "missing password and/or username"
    );
  });
});
