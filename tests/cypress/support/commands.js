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

Cypress.Commands.add("login", (loginMessage) => {
    cy.visit(Cypress.config().baseUrl)
    cy.contains(loginMessage).click(10, 10)

    cy.get('#classicform input[name=username]').type('swift')
    cy.get('#classicform input[name=password]').type('veryfast')
    cy.get('#classicform [type="submit"]').click()
})

Cypress.Commands.add("logout", () => {
    cy.get('[data-testid="user-menu"]').click()
    .find('li').contains('Log Out').click()
})

// CSC Design System renders inside of shadow DOM and therefore needs to be queried
// with .shadow() method.
Cypress.Commands.add("changeLang", (locale) => {
    const locales = [
        {key: 'en', label: 'In English'},
        {key: 'fi', label: 'Suomeksi'},
    ]
    cy.get('[data-testid="language-selector"]').click()
    .find('li').contains(locales.find(item => item.key === locale).label).click()
})

Cypress.Commands.add("navigateUserMenu", (menuItem) => {
    cy.get('[data-testid="user-menu"]').click()
    .find('li').contains(menuItem).click()
})

Cypress.Commands.add("selectProject", (projectName) => {
    cy.get('[data-testid="project-selector"]').click()
    .find('li').contains(projectName).click()
})

Cypress.Commands.add("deleteDB", () => {
    indexedDB.deleteDatabase("sd-connect")
})
// some exceptions like API reponse from delete we are not catching
// and we don't need to, thus we ignore
Cypress.on("uncaught:exception", () => {
    return false
})

Cypress.Commands.add("navigateTableRowMenu", (index, menuItem) => {
    cy.get("tbody tr").eq(index).within(() => {
        cy.get("c-menu").click()
        cy.get("c-menu").find("li").contains(menuItem).click()
      })
})