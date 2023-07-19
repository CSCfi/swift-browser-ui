// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add("login", (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add("drag", { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add("dismiss", { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite("visit", (originalFn, url, options) => { ... })

import { faker } from "../../../swift_browser_ui_frontend/node_modules/@faker-js/faker";

Cypress.Commands.add("login", (username, password) => {
  cy.get("c-login-card-actions.hydrated > .hydrated").click();
  cy.url().should("include", "/login/");
  cy.get('#classicform > [type="text"]').type(username);
  cy.get('[type="password"]').type(password);
  cy.get('#classicform > [type="submit"]').click();
});

Cypress.Commands.add("logout", () => {
  cy.contains('[data-testid="user-menu"]').click();
  cy.get("ul.c-menu-items").find("li").contains("Log out").click();
});

// CSC Design System renders inside of shadow DOM and therefore needs to be queried
// with .shadow() method.
Cypress.Commands.add("changeLang", (locale) => {
  const locales = [
    { key: "en", label: "In English" },
    { key: "fi", label: "Suomeksi" },
  ];
  cy.get('[data-testid="language-selector"]')
    .click()
    .find("li")
    .contains(locales.find((item) => item.key === locale).label)
    .click();
});

Cypress.Commands.add("switchLang", (lang) => {
  cy.get("ul.c-menu-items").find("li").contains(lang).click();
});

Cypress.Commands.add("navigateUserMenu", (menuItem) => {
  cy.get('[data-testid="user-menu"]')
    .click()
    .find("li")
    .contains(menuItem)
    .click();
});

Cypress.Commands.add("selectProject", (projectName) => {
  cy.get('[data-testid="project-selector"]')
    .click()
    .find("li")
    .contains(projectName)
    .click();
});

Cypress.Commands.add("deleteDB", () => {
  indexedDB.deleteDatabase("sd-connect");
});

// some exceptions like API reponse from delete we are not catching
// and we don't need to, thus we ignore
Cypress.on("uncaught:exception", () => {
  return false;
});

Cypress.Commands.add("navigateTableRowMenu", (index, menuItem) => {
  cy.get("tbody tr")
    .eq(index)
    .within(() => {
      cy.get("c-menu").click();
      cy.get("c-menu").find("li").contains(menuItem).click();
    });
});

Cypress.Commands.add("addFolder", (folderName) => {
  cy.get('[data-testid="create-folder"]').click();
  cy.wait(3000);
  cy.get('[data-testid="folder-name"]').click({ force: true });
  cy.get('[data-testid="folder-name"]').click({ force: true }).type(folderName);
  cy.wait(3000);
  cy.get('[data-testid="save-folder"]').click({ force: true });
});

Cypress.Commands.add("deleteFolder", (folderName) => {
  cy.contains(folderName)
    .parent()
    .parent()
    .parent()
    .find("td")
    .eq(6)
    .find("div")
    .eq(0)
    .children(".children")
    .eq(0)
    .children("c-menu")
    .eq(0)
    .find("c-button")
    .click();

  cy.get("ul.c-menu-items").find("li").contains("Delete").click();
});

Cypress.Commands.add("uploadFile", (fileName) => {});

Cypress.Commands.add("deleteFile", (fileName) => {
  cy.contains(fileName)
    .parent()
    .parent()
    .find("td")
    .eq(2)
    .find("button")
    .click();
});

Cypress.Commands.add("searchFolder", (folderName) => {
  cy.get(".c-input--text")
    .eq(1)
    .children()
    .eq(0)
    .children()
    .eq(0)
    .children()
    .eq(1)
    .children()
    .eq(1)
    .children()
    .eq(0)
    .find("input")
    .eq(0)
    .type(folderName, { force: true });
  cy.wait(5000);
});

Cypress.Commands.add("generateFixture", (name) => {
  cy.writeFile(`cypress/fixtures/text-files/${name}.txt`, {
    hits: Cypress._.times(20, () => {
      return faker.lorem.paragraphs(50);
    }),
  });
});
