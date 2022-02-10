describe("Login and log out a user", function () {

    it("should login to sso and input token and get to /browse route and log out", () => {
        cy.login(' Log In with SSO ')
        cy.get('.buttons > .router-link-exact-active').should(($browse) => {
            expect($browse).to.have.length(1)
            expect($browse).to.contain('Browse')
        })
        cy.url().should('eq', Cypress.config().baseUrl + '/browse/testuser/test-id-0')
        cy.contains('Log Out').click()
    })

    it("should login user with Finnish to sso and remember the selection", () => {
        cy.get('select').select('Suomeksi')
        cy.login(' Kirjaudu SSO:ta käyttäen ')
        cy.get('.buttons > .router-link-exact-active').should(($browse) => {
            expect($browse).to.have.length(1)
            expect($browse).to.contain('Selain')
        })
        cy.url().should('eq', Cypress.config().baseUrl + '/browse/testuser/test-id-0')
        cy.contains('Kirjaudu ulos').click()
    })

})

describe("Retrieve User information", function () {

    beforeEach(function () {
        cy.login(' Log In with SSO ')
    });

    afterEach(function () {
        cy.contains('Log Out').click()
    });

    it("should login the user and switch to user infomation and retrieve correct data", () => {
        cy.url().should('eq', Cypress.config().baseUrl + '/browse/testuser/test-id-0')
        cy.contains('User information').click()
        cy.wait(1000)
        cy.url().should('eq', Cypress.config().baseUrl + '/browse/testuser')
        cy.contains('test-name-0')
        cy.contains('testuser')
        cy.contains('test-id-0')
        cy.contains('Buckets: 10')
    })

    it("should login to switch project and browser and view different information", () => {
        cy.get('.navbar-dropdown').invoke('css', 'display', 'block')
            .should('have.css', 'display', 'block')
        cy.wait(1000)
        cy.contains('test-name-0').click()
        cy.wait(1000)
        cy.url().should('eq', Cypress.config().baseUrl + '/browse/testuser/test-id-0')
        cy.contains('User information').click()
        cy.contains('testuser')
        cy.contains('Buckets: 10')
        cy.contains('test-name-0')
        cy.get('.navbar-dropdown').invoke('css', 'display', 'block')
        .should('have.css', 'display', 'block')
        cy.wait(2000)
        cy.contains('test-name-1').click()
        cy.wait(1000)
        cy.url().should('eq', Cypress.config().baseUrl + '/browse/testuser')
        cy.contains('.buttons > .button','Browser').click()
        cy.wait(2000)
        cy.url().should('eq', Cypress.config().baseUrl + '/browse/testuser/test-id-1')
    })

})

describe("Switch Languages after login", function () {

    beforeEach(function () {
        cy.login(' Log In with SSO ')
    });

    afterEach(function () {
        cy.contains('Kirjaudu ulos').click()
    });

    it("should login the user with English but switch to Finnish", () => {
        cy.get('.locale-changer > div > span select').select('Suomeksi')
        cy.contains('Nykyinen projekti')
        cy.get('.input').invoke('attr', 'placeholder').should('contain', 'Etsi nimellä')
    })

})
