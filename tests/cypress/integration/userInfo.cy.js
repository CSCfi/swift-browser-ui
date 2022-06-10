describe("Login and log out a user", function () {

    it("should login with username + password and get to /browse route and log out", () => {
        cy.login(' Log In with SSO ')
        cy.get('.buttons > .router-link-exact-active').should(($browse) => {
            expect($browse).to.have.length(1)
            expect($browse).to.contain('Browse')
        })
        cy.location("pathname").should("match", /browse\/swift\/[0-9a-f]{32}/)
        cy.contains('Log Out').click()
    })

    it("should login user with Finnish to username + password and remember the selection", () => {
        cy.get("In English").click()
        cy.get("Suomeksi").click()
        cy.login(' Kirjaudu SSO:ta käyttäen ')
        cy.get('.buttons > .router-link-exact-active').should(($browse) => {
            expect($browse).to.have.length(1)
            expect($browse).to.contain('Selain')
        })
        cy.location("pathname").should("match", /browse\/swift\/[0-9a-f]{32}/)
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
        cy.location("pathname").should("match", /browse\/swift\/[0-9a-f]{32}/)
        cy.get('.navbar-dropdown').invoke('css', 'display', 'block')
            .should('have.css', 'display', 'block')
        cy.contains('service').click()
        cy.contains('User information').invoke("attr", 'href').should("match", /browse\/swift\/[0-9a-f]{32}\/info/)
        cy.contains('User information').click()
        cy.location("pathname").should("match", /browse\/swift/)
        cy.contains('Buckets: 15')
    })

    it("should login to switch project and browser and view different information", () => {
        cy.location("pathname").should("match", /browse\/swift\/[0-9a-f]{32}/)
        cy.get('.navbar-dropdown').invoke('css', 'display', 'block')
            .should('have.css', 'display', 'block')
        cy.contains('swift-project').click()
        cy.contains('User information').invoke("attr", 'href').should("match", /browse\/swift\/[0-9a-f]{32}\/info/)
        cy.contains('User information').click()
        cy.contains('Buckets: 10')
        cy.location("pathname").should("match", /browse\/swift/)
        cy.contains('.buttons > .button','Browser').click()
        cy.location("pathname").should("match", /browse\/swift\/[0-9a-f]{32}/)
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
