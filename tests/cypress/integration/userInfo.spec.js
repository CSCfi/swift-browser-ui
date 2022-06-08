describe("Login and log out a user", function () {

    it("should login with username + password and get to /browse route and log out", () => {
        cy.login(' Log In with SSO ')

        cy.selectProject('service')
        cy.navigateUserMenu('Browser')

        cy.location("pathname").should("match", /browse\/swift\/[0-9a-f]{32}/)
        cy.logout()
    })

    it("should login user with Finnish to username + password and remember the selection", () => {
        cy.changeLang('fi')

        cy.login(' Kirjaudu SSO:ta käyttäen ')

        cy.selectProject('service')
        cy.navigateUserMenu('Selain')

        cy.location("pathname").should("match", /browse\/swift\/[0-9a-f]{32}/)
        cy.navigateUserMenu('Kirjaudu ulos')
    })

})

describe("Retrieve User information", function () {

    beforeEach(function () {
        cy.login(' Log In with SSO ')
    });

    afterEach(function () {
        cy.logout()
    });

    it("should login the user and switch to user infomation and retrieve correct data", () => {
        cy.location("pathname").should("match", /browse\/swift\/[0-9a-f]{32}/)
        cy.selectProject('service')
        cy.navigateUserMenu('User information')
        cy.location("pathname").should("match", /browse\/swift/)
        cy.contains('Buckets: 15')
    })

    it("should login to switch project and browser and view different information", () => {
        cy.location("pathname").should("match", /browse\/swift\/[0-9a-f]{32}/)
        cy.selectProject('swift-project')
        cy.contains('swift-project')
        cy.navigateUserMenu('User information')
        cy.contains('Buckets: 10')


        cy.location("pathname").should("match", /browse\/swift/)
        cy.navigateUserMenu('Browser')
        cy.location("pathname").should("match", /browse\/swift\/[0-9a-f]{32}/)
    })

})

describe("Switch Languages after login", function () {

    beforeEach(function () {
        cy.login(' Log In with SSO ')
    });

    afterEach(function () {
        cy.navigateUserMenu('Kirjaudu ulos')
    });

    it("should login the user with English but switch to Finnish", () => {
        cy.changeLang('fi')
        cy.get('[data-testid="project-selector"]').shadow().find('label').contains('Valitse projekti')
        cy.get('.input').invoke('attr', 'placeholder').should('contain', 'Etsi nimellä')
    })

})
