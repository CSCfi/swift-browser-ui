describe("User can share folder from container table", function () {
  beforeEach(() => {
    cy.visit(Cypress.config().baseUrl);
    cy.login(Cypress.env("username"), Cypress.env("password"));
    cy.wait(3000);
  });

  it("User can share folder with read and write, the receiver can upload files to it", () => {
    cy.url().then((url) => {
      const copyId = url.split("/")[5];
      cy.log(copyId);

      //switch user
      cy.logout();
      cy.login(Cypress.env("username2"), Cypress.env("password2"));

      //add folders to get a minimum of 2 pages
      let i = 0;
      while (i < 12) {
        const folderName = Math.random().toString(36).substring(2, 7);
        cy.addFolder(folderName);
        i++;
        cy.wait(1000);
      }

      const randomName = Math.random().toString(36).substring(2, 7);

      const folderName = `x${randomName}`;
      cy.addFolder(folderName);
      findFolder(folderName);

      cy.contains(folderName)
        .parent()
        .parent()
        .parent()
        .find("[testid='share-container']")
        .click({ force: true });

      //share
      cy.share(copyId, "read and write");
      cy.wait(2000);
      cy.get("[data-testid='share-success-alert']").should("exist");

      //close share modal
      cy.get("[data-testid='close-share-modal']").click();

      //switch user
      cy.logout();
      cy.login(Cypress.env("username"), Cypress.env("password"));
      cy.wait(5000);

      //access folder
      findFolder(folderName)
      cy.contains(folderName)
        .click({ force: true });

      //generate fixture
      const file = "text-file";
      cy.generateFixture(file);

      //upload file from destination folder
      cy.uploadFileFromFolder(file);

      //upload modal closes when upload starts successfully
      cy.get("[data-testid='upload-modal']")
        .should("not.be.visible");

      //check if the file name is in the table
      cy.contains(file).should("exist");
    });
  });
});

const findFolder = (fname) => {
  const findInPage = (index) => {
    let found = false;

    cy.get(
      `nav.c-pagination ul li c-icon-button:not([aria-label="Next page"]):not([aria-label="Previous page"])`
    ).as("pages");

    cy.get("@pages")
      .its("length")
      .then(($len) => {
        if (index >= $len) return;

        cy.get("@pages").eq(index).click();
        cy.wait(3000);

        cy.get("c-link.hydrated")
          .each((link) => {
            const searchName = link[0].innerText;

            cy.log(searchName);

            if (fname === searchName) {
              found = true;
              return false;
            }
          })
          .then(() => {
            if (!found) findInPage(++index);
          });
      });
  };

  findInPage(0);
};
