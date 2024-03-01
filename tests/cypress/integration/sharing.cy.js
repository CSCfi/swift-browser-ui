describe("A folder is shared from project A to project B", function () {
  beforeEach(() => {
    cy.visit(Cypress.config().baseUrl);
    cy.login(Cypress.env("username"), Cypress.env("password"));
  });

  //Happy test cases
  it("the folder is shared successfully, when we switch project, shared folder is visible", function () {
    cy.wait(3000);

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

      //type in swift-project's shareID
      cy.get("[data-testid='share-id-input']>input").type(copyId, {
        force: true,
      });

      //choose read permission
      cy.get("[data-testid='select-permissions']").click({ force: true });
      cy.wait(3000);
      cy.get("[data-testid='read-perm']").click({ force: true });
      cy.wait(3000);

      //save sharing
      cy.get("[data-testid='submit-share']").click({ force: true });
      cy.wait(3000);

      cy.get("[data-testid='share-success-alert']").should("exist");

      //see if share id added to share table
      cy.get("[data-testid='share-modal-table']").contains(copyId);

      //Switch project and check the folder is visible

      //close share modal
      cy.get("[data-testid='close-share-modal']").click({ force: true });

      //switch project
      cy.switchProject();
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
  });

  it("switch project, try to share folder without share ID, fail", function () {
    cy.wait(3000);

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

      //choose read permission
      cy.get("[data-testid='select-permissions']").click({ force: true });
      cy.wait(3000);
      cy.get("[data-testid='read-perm']").click({ force: true });
      cy.wait(3000);

      //save sharing
      cy.get("[data-testid='submit-share']").click({ force: true });
      cy.wait(3000);

      //see error toast
      cy.get("[data-testid='shareModal-toasts']")
        .find("c-toast")
        .should("exist")
        .and("have.class", "error");
      cy.get("[data-testid='share-success-alert']").should("not.be.visible");
    });
  });

  it("copy shareID, switch project, try to share folder without selecting rights, fail", function () {
    cy.wait(3000);
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

      //type in service's shareID
      cy.get("[data-testid='share-id-input']>input").type(copyId, {
        force: true,
      });

      //save sharing
      cy.get("[data-testid='submit-share']").click({ force: true });
      cy.wait(3000);

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
  });

  it("switch project, try to share folder with the same ID twice, fail", function () {
    cy.wait(3000);

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

      //type in swift-project's shareID
      cy.get("[data-testid='share-id-input']>input").type(copyId, {
        force: true,
      });

      //choose read permission
      cy.get("[data-testid='select-permissions']").click({ force: true });
      cy.wait(3000);
      cy.get("[data-testid='read-perm']").click({ force: true });
      cy.wait(3000);

      //save sharing
      cy.get("[data-testid='submit-share']").click({ force: true });
      cy.wait(3000);

      //share should be successful
      cy.get("[data-testid='share-success-alert']").should("exist");

      //repeat sharing with same ID

      //type in swift-project's shareID
      cy.get("[data-testid='share-id-input']>input").type(copyId, {
        force: true,
      });

      //choose read permission
      cy.get("[data-testid='select-permissions']").click({ force: true });
      cy.wait(3000);
      cy.get("[data-testid='read-perm']").click({ force: true });
      cy.wait(3000);

      //save sharing
      cy.get("[data-testid='submit-share']").click({ force: true });
      cy.wait(3000);

      //see error toast
      cy.get("[data-testid='shareModal-toasts']")
        .find("c-toast")
        .should("exist")
        .and("have.class", "error");
      cy.get("[data-testid='share-success-alert']").should("not.be.visible");
    });
  });
});

describe("A folder cannot be shared with the invalid ID", function () {
  beforeEach(() => {
    cy.visit(Cypress.config().baseUrl);
    cy.login(Cypress.env("username"), Cypress.env("password"));
  });

  it("switch project, try to share folder with invalid share ID, fail", function () {
    cy.wait(3000);

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

    //type in invalid shareID
    const invalidId = Math.random().toString(36).substring(2, 7);
    cy.get("[data-testid='share-id-input']>input").type(invalidId, {
      force: true,
    });

    //choose read permission
    cy.get("[data-testid='select-permissions']").click({ force: true });
      cy.wait(3000);
      cy.get("[data-testid='read-perm']").click({ force: true });
      cy.wait(3000);

    //save sharing
    cy.get("[data-testid='submit-share']").click({ force: true });
    cy.wait(3000);

    //see error toast
    cy.get("[data-testid='shareModal-toasts']")
      .find("c-toast")
      .should("exist")
      .and("have.class", "error");
    cy.get("[data-testid='share-success-alert']").should("not.be.visible");
  });
});
