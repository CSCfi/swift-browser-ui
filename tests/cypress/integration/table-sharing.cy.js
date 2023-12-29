describe("User can share folder from the main page/table", function () {
    beforeEach(() => {
      cy.visit(Cypress.config().baseUrl);
      cy.login(Cypress.env("username"), Cypress.env("password"));
      cy.wait(3000);
    });

    it("User can share folder from the table on the main page", () => {
      cy.url().then((url) => {
        const copyId = url.split("/")[5];
        cy.log(copyId);

        //switch project
        cy.selectProject("service");

        //add folders to get a minimum of 2 pages
        let i = 0;
        while (i < 12) {
          cy.wait(5000);
          const folderName = Math.random().toString(36).substring(2, 7);
          cy.addFolder(folderName);
          i++;
          cy.wait(5000);
        }

        const randomName = Math.random().toString(36).substring(2, 7);

        const folderName = `x${randomName}`;
        cy.addFolder(folderName);
        findFolder(folderName);

        cy.contains(folderName)
          .parent()
          .parent()
          .parent()
          .find("td")
          .eq(6)
          .find("div")
          .eq(0)
          .children(".children")
          .eq(0)
          .children("c-button")
          .eq(1)
          .click({ force: true });

        //type in swift-project's shareID
        cy.get(":nth-child(1) > .tags-list > input").type(copyId, {
          force: true,
        });

        //choose copy and download permission
        cy.contains("Select permissions").click({ force: true });
        cy.wait(3000);
        // cy.contains("Copy and download").click({ force: true });
        cy.get(".c-input-menu__item-wrapper")
          .find("ul")
          .find("li")
          .contains("Copy and download")
          .click({ force: true });
        cy.wait(3000);

        //save sharing
        //save sharing
        cy.get("#share-btn").eq(0).click({ force: true });

        cy.contains("Folder was shared successfully").should("exist");
        cy.contains(copyId).should("exist");

        // TODO test upload-download
        //generate fixture
        // cy.generateFixture(fileName);
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
        .then((len) => {
          if (index >= len) return;

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
