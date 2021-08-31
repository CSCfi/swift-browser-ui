describe("Browse buckets and test operations", function () {

  beforeEach(function () {
    cy.login(' Log In with SSO ')
  });

  afterEach(function () {
    cy.contains('Log Out').click()
  });

  it("should be able to filter table, adjust display buckets per page and pagination", () => {
    cy.get('[data-testid="bucketsPerPage"]').select('5 per page')
    cy.contains('1-5 / 10')
    cy.contains('Paginated').parent().click()
    cy.get('[data-testid="bucketsPerPage"]').should('be.disabled')
    cy.get('.input').type('test-container-5')
  })

  it("should browse table, check download and delete buttons", () => {
    // we take the first container that is not empty
    cy.get('table').contains('td', 'MiB').then(($elem) => {
      cy.get($elem)
        .parent('tr')
        .within(() => {
          cy.get('td').eq(0).then(($elem) => {
            cy.get($elem).dblclick()
            cy.url().should('eq', Cypress.config().baseUrl + '/browse/test_user_id/placeholder/' + $elem.get(0).innerText.trim())
            cy.wait(2000)
            
          })
        })
    })

    // we check the new table
    cy.get('table').contains('td', 'KiB').then(($elem) => {
      cy.get($elem)
        .parent('tr')
        .within(() => {
          cy.get('td').eq(0).click()
          cy.get('td').eq(1).then(($elem) => {
            expect($elem.get(0).innerText.trim()).to.have.lengthOf(40)
          })
        })
    })

    // check the table info was properly open
    // we check the hash is in table as td and as a li in table info
    cy.contains('File Download')
    cy.contains('Hash: ').then(($elem) => {
      cy.get($elem).parent().then(($hashElem)=> {
        const hashFirstElem = $hashElem.get(0).innerText.replace("Hash: ", "")
        cy.get('td').contains(hashFirstElem).should('have.length', 1)
        cy.get('li').contains(hashFirstElem).should('have.length', 1)
        // not sure we have a prettier way to do this
        // as cypress seems to have some issues with new window being opened
        cy.get(':nth-child(1) > :nth-child(5) > .field > .control > .button').invoke('attr', 'href').should('contain', '&objkey=' + hashFirstElem)
      })
    })

    cy.get('tbody > :nth-child(1) > :nth-child(6) > .contents > .button').click()
    cy.contains('Delete Object / Objects')
    cy.get('.modal-card-foot > .is-danger').contains('Delete Objects').click()
    cy.contains('Objects deleted')

  })

})
