//login

// successfull login with correct login and password

describe("Log in a user", () => {
  beforeEach(() => {
    cy.visit(Cypress.config().baseUrl);
  });

  it("Login button redirects to login page", () => {
    cy.get("c-login-card-actions>c-button").click();
    cy.url().should("include", "/login/");
  });

  it("Login with correct credentials redirects to project browsing page", () => {
    cy.login(Cypress.env("username"), Cypress.env("password"));
    cy.url().should("include", "browse");
    cy.get("[data-testid='create-folder']").should("be.visible");
    cy.getCookie("SWIFT_UI_SESSION").should("exist");
    cy.getCookie("OBJ_UI_LANG").should("have.property", "value", "en");
    cy.logout();
  });
});

// successful login with changing languages before logging in

describe("Switch UI language", () => {
  beforeEach(() => {
    cy.visit(Cypress.config().baseUrl);
  });

  afterEach(() => {
    cy.logout();
  });

  const defaultLang = "en";
  const otherLang = "fi";

  it("Switch language before logging in", () => {
    cy.getCookie("OBJ_UI_LANG").should("have.property", "value", defaultLang);
    cy.changeLang(otherLang);
    cy.login(Cypress.env("username"), Cypress.env("password"));
    cy.getCookie("OBJ_UI_LANG").should("have.property", "value", otherLang);
  });

  it("Switch language after logging in", () => {
    cy.getCookie("OBJ_UI_LANG").should("have.property", "value", defaultLang);
    cy.login(Cypress.env("username"), Cypress.env("password"));
    cy.changeLang(otherLang);
    cy.getCookie("OBJ_UI_LANG").should("have.property", "value", otherLang);
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
    cy.get("c-card-title").should("contain", "401");
    cy.get("[data-testid='return-to-login']")
      .should("exist");
  });

  it("password is incorrect", () => {
    cy.login(Cypress.env("username"), Cypress.env("wrongpassword"));
    cy.url().should("include", "credentials");
    cy.get("c-card-title").should("contain", "401");
    cy.get("[data-testid='return-to-login']")
      .should("exist");
  });

  it("username is empty", () => {
    cy.login("", Cypress.env("wrongpassword"));
    cy.url().should("include", "credentials");
    cy.get("c-card-title").should("contain", "400");
  });

  it("password is empty", () => {
    cy.login(Cypress.env("username"), "");
    cy.url().should("include", "credentials");
    cy.get("c-card-title").should("contain", "401");
    cy.get("[data-testid='return-to-login']")
      .should("exist");
  });

  it("both input fields empty ", () => {
    cy.login("", "");
    cy.url().should("include", "credentials");
    cy.get("c-card-title").should("contain", "400");
  });
});

describe("Log in and switch language with mobile navigation", function () {

  const lang = {key: "fi", text: "Suomeksi"};

  it("should be able to log in and change language", function () {
    cy.viewport(720, 1280);

    //log in
    cy.visit(Cypress.config().baseUrl);
    cy.login(Cypress.env("username"), Cypress.env("password"));

    //open menu
    cy.get("c-navigationbutton")
      .as("mobile-menu")
      .should("be.visible")
      .click();

    //change language
    cy.get("[data-testid='language-selector-mobile']")
      .click();
    cy.get("c-subnavigationitem")
      .contains(lang.text, { matchCase: false })
      .click();
    cy.getCookie("OBJ_UI_LANG").should("have.property", "value", lang.key);

    //log out
    cy.get("@mobile-menu").click();
    cy.get("[data-testid='user-menu-mobile']").click();
    cy.get("[data-testid='logout-mobile']").click();
  });
});
