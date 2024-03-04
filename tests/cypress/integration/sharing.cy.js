describe("A folder is shared from project A to project B", function () {
  beforeEach(() => {
    cy.visit(Cypress.config().baseUrl);
    cy.login(Cypress.env("username"), Cypress.env("password"));
    cy.wait(3000);
  });

  //Happy test cases
  it("the folder is shared successfully, when other user logs in, shared folder is visible", function () {
    //take the ID appearing as the last part of url
    cy.url().then((url) => {
      const copyId = url.split("/")[5];
      cy.log(copyId);

      //switch user
      cy.logout();
      cy.login(Cypress.env("username2"), Cypress.env("password2"));
      cy.wait(3000);

      //add folder
      const folderName = Math.random().toString(36).substring(2, 7);
      cy.addFolder(folderName);
      cy.wait(3000);

      //access folder
      cy.searchFolder(folderName);
      cy.get("[data-testid='search-result']")
        .contains(folderName)
        .click({ force: true });
      cy.wait(3000);

      //edit sharing
      cy.get("[data-testid='edit-sharing']").click({ force: true });
      cy.share(copyId, "read");
      cy.wait(2000);

      cy.get("[data-testid='share-success-alert']").should("exist");

      //see if share id added to share table
      cy.wait(2000);
      cy.get("[data-testid='share-modal-table']").contains(copyId);

      //close share modal
      cy.get("[data-testid='close-share-modal']").click({ force: true });

      //Switch user and check the folder is visible

      //switch user
      cy.logout();
      cy.login(Cypress.env("username"), Cypress.env("password"));
      cy.wait(3000);

      cy.get("[data-testid='container-table']")
        .contains(folderName)
        .should("exist");
    });
  });
});

//Unhappy test cases
describe("A folder cannot be shared without Share ID or if rights are not selected", function () {
  beforeEach(() => {
    cy.visit(Cypress.config().baseUrl);
    cy.login(Cypress.env("username"), Cypress.env("password"));
    cy.wait(3000);
  });

  it("switch project, try to share folder without share ID, fail", function () {
    //take the ID appearing as the last part of url
    cy.url().then((url) => {
      const copyId = url.split("/")[5];
      cy.log(copyId);

      //switch project
      cy.switchProject();

      //add folder
      const folderName = Math.random().toString(36).substring(2, 7);
      cy.addFolder(folderName);
      cy.wait(3000);

      //access folder
      cy.searchFolder(folderName);
      cy.get("[data-testid='search-result']")
        .contains(folderName)
        .click({ force: true });
      cy.wait(3000);

      //edit sharing
      cy.get("[data-testid='edit-sharing']").click({ force: true });
      cy.share("", "read");
      cy.wait(2000);

      //see error toast
      cy.get("[data-testid='shareModal-toasts']")
        .find("c-toast")
        .should("exist")
        .and("have.class", "error");
      cy.get("[data-testid='share-success-alert']").should("not.be.visible");
    });
  });

  it("copy shareID, switch project, try to share folder without selecting rights, fail", function () {
    //take the ID appearing as the last part of url
    cy.url().then((url) => {
      const copyId = url.split("/")[5];
      cy.log(copyId);

      //switch project
      cy.switchProject();

      //add folder
      const folderName = Math.random().toString(36).substring(2, 7);
      cy.addFolder(folderName);
      cy.wait(3000);

      //access folder
      cy.searchFolder(folderName);
      cy.get("[data-testid='search-result']")
        .contains(folderName)
        .click({ force: true });
      cy.wait(3000);

      //edit sharing
      cy.get("[data-testid='edit-sharing']").click({ force: true });
      cy.share(copyId, "");
      cy.wait(2000);

      //see error toast
      cy.get("[data-testid='shareModal-toasts']")
        .find("c-toast")
        .should("exist")
        .and("have.class", "error");
      cy.get("[data-testid='share-success-alert']").should("not.be.visible");
    });
  });
});

describe("A folder cannot be shared with the same Share ID twice", function () {
  beforeEach(() => {
    cy.visit(Cypress.config().baseUrl);
    cy.login(Cypress.env("username"), Cypress.env("password"));
    cy.wait(3000);
  });

  it("switch project, try to share folder with the same ID twice, fail", function () {
    //take the ID appearing as the last part of url
    cy.url().then((url) => {
      const copyId = url.split("/")[5];
      cy.log(copyId);

      //switch project
      cy.switchProject();

      //add folder
      const folderName = Math.random().toString(36).substring(2, 7);
      cy.addFolder(folderName);
      cy.wait(3000);

      //access folder
      cy.searchFolder(folderName);
      cy.get("[data-testid='search-result']")
        .contains(folderName)
        .click({ force: true });
      cy.wait(3000);

      //edit sharing
      cy.get("[data-testid='edit-sharing']").click({ force: true });
      cy.share(copyId, "read");
      cy.wait(2000);

      //share should be successful
      cy.get("[data-testid='share-success-alert']").should("exist");

      //repeat sharing with same ID
      cy.share(copyId, "read");
      cy.wait(2000);

      //see error toast
      cy.get("[data-testid='shareModal-toasts']")
        .find("c-toast")
        .should("exist")
        .and("have.class", "error");
      cy.get("[data-testid='share-success-alert']").should("not.be.visible");
    });
  });
});

describe("A folder cannot be shared with an invalid ID", function () {
  beforeEach(() => {
    cy.visit(Cypress.config().baseUrl);
    cy.login(Cypress.env("username"), Cypress.env("password"));
    cy.wait(3000);
  });

  it("switch project, try to share folder with invalid share ID, fail", function () {
    //switch project
    cy.switchProject();

    //add folder
    const folderName = Math.random().toString(36).substring(2, 7);
    cy.addFolder(folderName);
    cy.wait(3000);

    //access folder
    cy.searchFolder(folderName);
    cy.get("[data-testid='search-result']")
      .contains(folderName)
      .click({ force: true });
    cy.wait(3000);

    //edit sharing
    cy.get("[data-testid='edit-sharing']").click({ force: true });

    //get invalid shareID and share
    const invalidId = Math.random().toString(36).substring(2, 7);
    cy.share(invalidId, "read");
    cy.wait(2000);

    //see error toast
    cy.get("[data-testid='shareModal-toasts']")
      .find("c-toast")
      .should("exist")
      .and("have.class", "error");
    cy.get("[data-testid='share-success-alert']").should("not.be.visible");
  });
});
