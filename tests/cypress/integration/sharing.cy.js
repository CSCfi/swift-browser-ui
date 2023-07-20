describe("A folder is shared from project A to project B", function () {
  beforeEach(() => {
    cy.visit(Cypress.config().baseUrl);
    cy.login(Cypress.env("username"), Cypress.env("password"));
  });

  it("copy share id, switch project, share folder, switch project, check if shared folder is visible", function () {
    //click to copy sharing ID
    cy.get('[data-testid="copy-projectId"]').click({ force: true });
    cy.wait(9000);
    //take the ID appearing as the last part of url
    cy.url().then((url) => {
      const copyId = url.split("/")[5];
      cy.log(copyId);
      //switch project
      cy.selectProject("service");
      //add folder
      const randomName = Math.random().toString(36).substring(2, 7);
      cy.addFolder(randomName);
      cy.wait(12000);
      //access folder
      cy.searchFolder(randomName);
      cy.get(".media-content").contains(randomName).click({ force: true });
      cy.wait(5000);
      cy.contains("Edit sharing").click({ force: true });

      //type in swift-project's shareID
      cy.get(":nth-child(1) > .tags-list > input").type(copyId, {
        force: true,
      });

      //choose permission
      cy.get(":nth-child(4) > c-select.hydrated")
        .click({ force: true })
        .find("li")
        .eq(0)
        .click({ force: true });
      //save sharing
      cy.get(
        "#share-card-modal-content > :nth-child(1) > :nth-child(4) > c-button.hydrated"
      ).click({ force: true });

      cy.contains("Folder was shared successfully").should("exist");
      cy.contains(copyId).should("exist");
    });
  });
});

describe("A folder cannot be shared without Share ID or if rights are not selected", function () {
  beforeEach(() => {
    cy.visit(Cypress.config().baseUrl);
    cy.login(Cypress.env("username"), Cypress.env("password"));
  });

  it("switch project, try to share folder without share ID, fail", function () {
    //click to copy sharing ID
    cy.get('[data-testid="copy-projectId"]').click({ force: true });
    cy.wait(7000);
    //take the ID appearing as the last part of url
    cy.url().then((url) => {
      const copyId = url.split("/")[5];
      cy.log(copyId);
      //switch project
      cy.selectProject("service");
      //add folder
      const randomName = Math.random().toString(36).substring(2, 7);
      cy.addFolder(randomName);
      cy.wait(9000);
      //access folder
      cy.searchFolder(randomName);
      cy.get(".media-content").contains(randomName).click({ force: true });
      cy.wait(5000);
      cy.contains("Edit sharing").click({ force: true });

      //choose permission
      cy.get(":nth-child(4) > c-select.hydrated")
        .click({ force: true })
        .find("li")
        .eq(0)
        .click({ force: true });
      //save sharing
      cy.get(
        "#share-card-modal-content > :nth-child(1) > :nth-child(4) > c-button.hydrated"
      ).click({ force: true });

      cy.contains("Please enter at least one Share ID").should("exist");
      cy.contains(copyId).should("not.exist");
    });
  });

  it("copy shareID, switch project, try to share folder without selecting rights, fail", function () {
    //click to copy sharing ID
    cy.get('[data-testid="copy-projectId"]').click({ force: true });
    cy.wait(7000);
    //take the ID appearing as the last part of url
    cy.url().then((url) => {
      const copyId = url.split("/")[5];
      cy.log(copyId);
      //switch project
      cy.selectProject("service");
      //add folder
      const randomName = Math.random().toString(36).substring(2, 7);
      cy.addFolder(randomName);
      cy.wait(9000);
      //access folder
      cy.searchFolder(randomName);
      cy.get(".media-content").contains(randomName).click({ force: true });
      cy.wait(5000);
      cy.contains("Edit sharing").click({ force: true });

      //type in swift-project's shareID
      cy.get(":nth-child(1) > .tags-list > input").type(copyId, {
        force: true,
      });

      //save sharing
      cy.get(
        "#share-card-modal-content > :nth-child(1) > :nth-child(4) > c-button.hydrated"
      ).click({ force: true });

      cy.contains("Please select permissions to grant").should("exist");
    });
  });
});
