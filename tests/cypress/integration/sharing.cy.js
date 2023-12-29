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
      cy.selectProject("service");

      //add folder
      const folderName = Math.random().toString(36).substring(2, 7);
      cy.addFolder(folderName);
      cy.wait(3000);

      //access folder
      cy.searchFolder(folderName);
      cy.get(".media-content").contains(folderName).click({ force: true });
      cy.wait(3000);

      //edit sharing
      cy.contains("Edit sharing").click({ force: true });

      //type in swift-project's shareID
      cy.get(":nth-child(1) > .tags-list > input").type(copyId, {
        force: true,
      });

      //choose copy and download permission
      cy.contains("Select permissions").click({ force: true });
      cy.wait(3000);
      cy.get(".c-input-menu__item-wrapper")
        .find("ul")
        .find("li")
        .contains("Copy and download")
        .click({ force: true });
      cy.wait(3000);

      //save sharing
      cy.get("#share-btn").eq(0).click({ force: true });

      cy.contains("Folder was shared successfully").should("exist");
      cy.contains(copyId).should("exist");

      //TODO switch project and check the folder is visible
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
      cy.selectProject("service");

      //add folder
      const folderName = Math.random().toString(36).substring(2, 7);
      cy.addFolder(folderName);
      cy.wait(3000);

      //access folder
      cy.searchFolder(folderName);
      cy.get(".media-content").contains(folderName).click({ force: true });
      cy.wait(3000);

      //edit sharing
      cy.contains("Edit sharing").click({ force: true });

      //choose copy and download permission
      cy.contains("Select permissions").click({ force: true });
      cy.wait(3000);
      cy.get(".c-input-menu__item-wrapper")
        .find("ul")
        .find("li")
        .contains("Copy and download")
        .click({ force: true });
      cy.wait(3000);

      //save sharing
      cy.get("#share-btn").eq(0).click({ force: true });

      cy.contains("Please enter at least one Share ID").should("exist");
      cy.contains(copyId).should("not.exist");
    });
  });

  it("copy shareID, switch project, try to share folder without selecting rights, fail", function () {
    cy.wait(3000);
    //take the ID appearing as the last part of url
    cy.url().then((url) => {
      const copyId = url.split("/")[5];
      cy.log(copyId);

      //switch project
      cy.selectProject("service");

      //add folder
      const folderName = Math.random().toString(36).substring(2, 7);
      cy.addFolder(folderName);
      cy.wait(3000);

      //access folder
      cy.searchFolder(folderName);
      cy.get(".media-content").contains(folderName).click({ force: true });
      cy.wait(3000);

      //edit sharing
      cy.contains("Edit sharing").click({ force: true });

      //type in swift-project's shareID
      cy.get(":nth-child(1) > .tags-list > input").type(copyId, {
        force: true,
      });

      //save sharing
      cy.get("#share-btn").eq(0).click({ force: true });

      cy.contains("Please select permissions to grant").should("exist");
    });
  });
});

describe("A folder cannot be shared with the same Share ID twice", function () {
  beforeEach(() => {
    cy.visit(Cypress.config().baseUrl);
    cy.login(Cypress.env("username"), Cypress.env("password"));
  });

  it("switch project, try to share folder without the same ID twice, fail", function () {
    cy.wait(3000);

    //take the ID appearing as the last part of url
    cy.url().then((url) => {
      const copyId = url.split("/")[5];
      cy.log(copyId);

      //switch project
      cy.selectProject("service");

      //add folder
      const folderName = Math.random().toString(36).substring(2, 7);
      cy.addFolder(folderName);
      cy.wait(3000);

      //access folder
      cy.searchFolder(folderName);
      cy.get(".media-content").contains(folderName).click({ force: true });
      cy.wait(3000);

      //edit sharing
      cy.contains("Edit sharing").click({ force: true });

      //type in swift-project's shareID
      cy.get(":nth-child(1) > .tags-list > input").type(copyId, {
        force: true,
      });

      //choose copy and download permission
      cy.contains("Select permissions").click({ force: true });
      cy.wait(3000);
      cy.get(".c-input-menu__item-wrapper")
        .find("ul")
        .find("li")
        .contains("Copy and download")
        .click({ force: true });
      cy.wait(3000);

      //save sharing
      cy.get("#share-btn").eq(0).click({ force: true });

      //repeat sharing with same ID
      cy.wait(3000);

      //edit sharing
      cy.contains("Edit sharing").click({ force: true });

      //type in swift-project's shareID
      cy.get(":nth-child(1) > .tags-list > input").type(copyId, {
        force: true,
      });

      //choose copy and download permission
      cy.contains("Select permissions").click({ force: true });
      cy.wait(3000);
      cy.get(".c-input-menu__item-wrapper")
        .find("ul")
        .find("li")
        .contains("Copy and download")
        .click({ force: true });
      cy.wait(3000);

      //save sharing
      cy.get("#share-btn").eq(0).click({ force: true });

      // cy.contains("already has access").should("exist");
      cy.contains("Folder was shared successfully").should("not.exist");
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
    cy.selectProject("service");

    //add folder
    const folderName = Math.random().toString(36).substring(2, 7);
    cy.addFolder(folderName);
    cy.wait(3000);

    //access folder
    cy.searchFolder(folderName);
    cy.get(".media-content").contains(folderName).click({ force: true });
    cy.wait(3000);

    //edit sharing
    cy.contains("Edit sharing").click({ force: true });

    //type in invalid shareID
    const copyId = Math.random().toString(36).substring(2, 7);
    cy.get(":nth-child(1) > .tags-list > input").type(copyId, {
      force: true,
    });

    //choose copy and download permission
    cy.contains("Select permissions").click({ force: true });
    cy.wait(3000);
    cy.get(".c-input-menu__item-wrapper")
      .find("ul")
      .find("li")
      .contains("Copy and download")
      .click({ force: true });
    cy.wait(3000);

    //save sharing
    cy.get("#share-btn").eq(0).click({ force: true });

    //cy.contains("already has access").should("exist");
    cy.contains("Folder was shared successfully").should("not.exist");
  });
});
