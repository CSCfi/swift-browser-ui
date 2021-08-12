describe("login and log out user", function () {

    it("should login to sso and input token and get to /browse route and log out", () => {
        cy.login(' Log In with SSO ')
        cy.get('.buttons > .router-link-exact-active').should(($browse) => {
            expect($browse).to.have.length(1)
            expect($browse).to.contain('Browse')
        })
        cy.contains('Log Out').click()
    })

    it("should login user with Finnish to sso and remember the selection", () => {
        cy.get('select').select('Suomeksi')
        cy.login(' Kirjaudu SSO:ta käyttäen ')
        cy.get('.buttons > .router-link-exact-active').should(($browse) => {
            expect($browse).to.have.length(1)
            expect($browse).to.contain('Selain')
        })
        cy.contains('Kirjaudu ulos').click()
    })

})
