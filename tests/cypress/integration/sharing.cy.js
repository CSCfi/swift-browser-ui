describe("A folder is shared from project A to project B", function () {
  beforeEach(() => {
    cy.visit(Cypress.config().baseUrl);
    cy.login(Cypress.env("username"), Cypress.env("password"));
  });

  it("copy share id, switch project, share folder, switch project, check if shared folder is visible", function () {});
});
