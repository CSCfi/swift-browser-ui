describe("Browse containers and test operations", function () {
  beforeEach(function () {
    cy.task("resetDB");
    cy.deleteDB();
    cy.login(" Log In with SSO ");
  });

  afterEach(function () {
    cy.logout();
  });

  xit("should be able to filter table, adjust display containers per page and pagination", () => {
    cy.location("pathname").should("match", /browse\/swift\/[0-9a-f]{32}/);
    cy.selectProject("service");

    cy.get('[data-testid="containersPerPage"]').select("5 per page");
    cy.contains("1-5 / 15");
    cy.get('[data-testid="paginationSwitch"]').click();
    cy.get('[data-testid="containersPerPage"]').should("be.disabled");
    cy.get("#searchbox").type("dolor");
  });

  xit("should browse table, check download and delete buttons", () => {
    // we take the first container that is not empty
    cy.get("table")
      .contains("td", "KiB")
      .then($elem => {
        cy.get($elem)
          .parent("tr")
          .within(() => {
            cy.get("td")
              .eq(0)
              .then($elem => {
                cy.get($elem).dblclick();
                cy.location("pathname").should(
                  "match",
                  /browse\/swift\/[0-9a-f]{32}\/.*/,
                );
              });
          });
      });

    // we check the new table
    cy.get("table")
      .contains("td", "B")
      .then($elem => {
        cy.get($elem)
          .parent("tr")
          .within(() => {
            cy.get("td").eq(0).click();
            cy.get('td[data-label="Name"] span')
              .first()
              .invoke("text")
              .then(text => {
                expect(text.trim()).to.match(/.*\.txt$/);
              });
          });
      });

    // check the table info was properly open
    // we check the hash is in table as td and as a li in table info
    cy.contains("File Download");
    cy.contains("Hash: ").then($elem => {
      cy.get($elem)
        .parent()
        .then($hashElem => {
          const hashFirstElem = $hashElem
            .get(0)
            .innerText.replace("Hash: ", "");
          cy.get("td").contains(hashFirstElem).should("have.length", 1);
          cy.get("li").contains(hashFirstElem).should("have.length", 1);
        });
    });

    cy.get(
      "tbody > :nth-child(1) > :nth-child(6) > .contents > .button",
    ).click();
    cy.contains("Delete Object / Objects");
    cy.get(".modal-card-foot > .is-danger").contains("Delete Objects").click();
    cy.contains("Objects deleted");
  });

  xit("should be able to add a new folder with tags", () => {
    cy.location("pathname").should("match", /browse\/swift\/[0-9a-f]{32}/);
    cy.get("[data-testid='create-folder']").click();
    cy.get("input[data-testid='folder-name']").type("Test folder name");
    cy.get("input[data-testid='folder-tag']").type(
      "tag1{enter} tag2{enter} tag3{enter}",
    );
    cy.get("[data-testid='save-folder']").should("be.visible").click();
  });

  xit("should display, add, remove container tags", () => {
    cy.location("pathname").should("match", /browse\/swift\/[0-9a-f]{32}/);
    cy.selectProject("service");

    // container list loads with tags
    cy.get("tbody .tags .tag", { timeout: 30000 }).should("have.length", 45);
    cy.get("tbody tr .tags", { timeout: 10000 })
      .first()
      .children(".tag")
      .should("have.length", 3);

    // remove one tag
    cy.navigateTableRowMenu(0, "Edit")
    cy.get("h2").should("contain", "Editing bucket");
    cy.get(".delete").first().click();
    cy.get("[data-testid='save-folder']").should("be.visible").click();
    cy.get("tbody tr .tags").first().children(".tag").should("have.length", 2);

    // add few tags
    cy.navigateTableRowMenu(0, "Edit")
    cy.get(".taginput-container").children("span").should("have.length", 2);
    cy.get(".taginput input").type("adding.couple more,");
    cy.get("[data-testid='save-folder']").should("be.visible").click();
    cy.get("tbody tr .tags").first().children(".tag").should("have.length", 5);

    // remove all tags from a container
    cy.navigateTableRowMenu(0, "Edit")
    cy.get(".taginput-container").children("span").should("have.length", 5);
    cy.get(".delete").each(el => {
      cy.get(".delete").first().click();
    });
    cy.get(".taginput-container").children("span").should("have.length", 0);
    cy.get("[data-testid='save-folder']").should("be.visible").click();
    cy.get("tbody tr .tags").first().children(".tag").should("have.length", 0);
  });

  xit("should display, add, remove object tags", () => {
    cy.location("pathname").should("match", /browse\/swift\/[0-9a-f]{32}/);
    cy.selectProject("service");

    cy.get("tbody tr td[data-label=Name]").first().dblclick();

    // object list loads with tags
    cy.get("tbody tr .tags").first().children(".tag").should("have.length", 4);
    cy.get("tbody tr .tags").first().children(".tag");

    // remove one tag
    cy.get("span").contains("Edit").first().click();
    cy.get("h1").should("contain", "Editing object");
    cy.get(".delete").first().click();
    cy.get("button").contains("Save").click();
    cy.get("tbody tr .tags").first().children(".tag").should("have.length", 3);

    // add few tags
   cy.get("span").contains("Edit").first().click();
    cy.get(".taginput-container").children("span").should("have.length", 3);
    cy.get(".taginput input").type("adding.couple more,");
    cy.get("button").contains("Save").click();
    cy.get("tbody tr .tags").first().children(".tag").should("have.length", 6);

    // remove all tags from an object
    cy.get("span").contains("Edit").first().click();
    cy.get(".taginput-container").children("span").should("have.length", 6);
    cy.get(".delete").each(el => {
      cy.get(".delete").first().click();
    });
    cy.get('.taginput-container').children('span').should('have.length', 0)
    cy.get('button').contains('Save').click()
    cy.get('tbody tr .tags').first().children('.tag').should('have.length', 0)
  });

  xit("should navigate between all and shared folders with tab selectors", () => {
    const testTabChange = (label, id) => {
      cy.get('[data-testid="folder-tabs"]').find("c-button").contains(label).click()
      cy.get(`#${id}`).should("be.visible")
    }

    testTabChange("Folders shared with you", "shared-table")
    testTabChange("Folders you have shared", "shared-out-table")
    testTabChange("All folders", "container-table")
  });

  xit("should copy the current project Id successfully ", () => {
    cy.location("pathname").should("match", /browse\/swift\/[0-9a-f]{32}/);
    cy.changeLang("en");
    cy.get("[data-testid='copy-projectId']").click();
    cy.get("[data-testid='copy-toasts']").should("be.visible");
    cy.contains("Copied!");
    // The copied text is read from clipboard
    cy.window().then(win => {
       win.navigator.clipboard.readText().then(text => {
        expect(text).to.exist;
       });
    });
  });
})
