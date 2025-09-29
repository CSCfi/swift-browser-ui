describe("Browse containers and test operations", function () {
  beforeEach(function () {
    cy.task("resetDB");
    cy.deleteDB();
    cy.visit(Cypress.config().baseUrl);
    cy.login(Cypress.env("username"), Cypress.env("password"));
    cy.wait(3000);
  });

  afterEach(function () {
    cy.logout();
  });

  it("should be able to adjust the number of containers per page and remove pagination", () => {

    //open pagination menu
    cy.get("c-pagination")
      .find("c-menu")
      .as("itemsPerPage")
      .click();
    cy.wait(1000);

    //get text of first option
    cy.get("c-menu-items")
      .find("ul>li")
      .first()
      .as("firstOption")
      .invoke("text")
      .then($value => {
        //click the first option
        cy.get("@firstOption")
          .click()
          .wait(3000);

        //see row count
        cy.get("[data-testid='container-table']")
          .find("tbody>tr")
          .its("length")
          //one row added for loader
          .should("be.lte", parseInt($value+1));
      });

    //click on display options
    cy.get("[data-testid='table-options-selector']")
      .click();
    cy.wait(1000);

    //click option to remove pagination
    cy.get("c-menu-items")
      .find("ul>li")
      .contains("pagination")
      .click();
    cy.wait(3000);

    cy.get("c-pagination")
      .should("not.be.visible");
  });

  it("should be able to create a new bucket with tags", () => {

    const bucketName = Math.random().toString(36).substring(2, 7);
    const tags = ["tag1", "tag2", "tag3"];

    //create bucket with tags
    cy.get("[data-testid='create-bucket']").click();
    cy.get("[data-testid='bucket-name']").type(bucketName);
    cy.get("[data-testid='bucket-tag']").type(tags.join("{enter} "));
    cy.get("[data-testid='save-bucket']")
      .should("be.visible")
      .click();
    cy.wait(3000);

    //check that modal closed, bucket name and tags exist
    cy.get("[data-testid='create-bucket-modal']")
      .should("not.be.visible");
    cy.contains(bucketName).should("exist");

    tags.forEach(tag => {
      cy.contains(tag).should("exist");
    });
  });

  it("should be able to add and remove container tags", () => {

    const bucketName = Math.random().toString(36).substring(2, 7);
    const tags = ["tag_1", "tag_2"];

    //create a new bucket
    cy.addBucket(bucketName);
    cy.wait(3000);

    //check that modal closed, bucket name exists
    cy.get("[data-testid='create-bucket-modal']")
      .should("not.be.visible");
    cy.contains(bucketName).should("exist");

    //get the right table row
    cy.get("c-data-table")
      .contains(bucketName)
      .parent() //div
      .parent() //td
      .parent() //tr
      .as("containerRow");

    //click on options to open edit tags modal
    cy.get("@containerRow")
      .find("c-menu")
      .click();
    cy.wait(1000);

    cy.get("c-menu-items")
      .find("ul>li")
      .contains("tag")
      .click();
    cy.wait(1000);

    cy.addTags(tags);
    cy.wait(3000);

    //see that modal closed and tags are visible
    cy.get("[data-testid='edit-tags-modal']").should("not.be.visible");

    tags.forEach(tag => {
      cy.get("@containerRow")
        .contains(tag)
        .should("exist");
    });

    //click on options to open edit tags modal
    cy.get("@containerRow")
      .find("c-menu")
      .click();
    cy.wait(1000);

    cy.get("c-menu-items")
      .find("ul>li")
      .contains("tag")
      .click();
    cy.wait(1000);

    cy.removeAllTags();
    cy.wait(3000);

    //see that modal closed and tags are gone
    cy.get("[data-testid='edit-tags-modal']").should("not.be.visible");

    tags.forEach(tag => {
      cy.get("@containerRow")
        .contains(tag)
        .should("not.exist");
    });
  });

  it("should display, add, remove object tags", () => {

    const bucketName = Math.random().toString(36).substring(2, 7);
    const file = "text-file";
    const tags = ["obj_tag1", "obj_tag2", "obj_tag3"];

    //upload file and create a bucket at the same time
    cy.generateFixture(file);
    cy.uploadFileFromMain(bucketName, file);
    cy.wait(5000);

    //close upload toast
    cy.get("[data-testid='close-upload-toast']")
      .should("exist")
      .click();
    cy.wait(3000);

    //go to bucket, check that file exists
    cy.searchBucket(bucketName);
    cy.get("[data-testid='search-result']")
      .contains(bucketName)
      .click();
    cy.wait(5000);

    cy.contains(file)
      .parent() //div
      .parent() //td
      .parent() //tr
      .as("fileRow")
      .should("exist");

    //open edit tags modal
    cy.get("[testid='edit-object-tags']").click();
    cy.wait(1000);

    //add object tags and save
    cy.addTags(tags);
    cy.wait(3000);

    //tags should be visible
    tags.forEach(tag => {
      cy.get("@fileRow")
        .contains(tag)
        .should("exist");
    });

    //open edit tags modal
    cy.get("[testid='edit-object-tags']").click();
    cy.wait(1000);

    //remove tags and save
    cy.removeAllTags();
    cy.wait(3000);

    //tags should not exist
    tags.forEach(tag => {
      cy.get("@fileRow")
        .contains(tag)
        .should("not.exist");
    });
  });

  it("should navigate between all and shared buckets with tab selectors", () => {
    const testTabChange = (id, routeEnd) => {
      cy.get("[data-testid='bucket-tabs']")
        .get(`[data-testid='${id}']`)
        .click();
      cy.wait(3000);
      cy.url().should("contain", routeEnd);
    }
    testTabChange("SharedFrom", "/shared/from")
    testTabChange("SharedTo", "/shared/to")
  });

  it("should copy the current project shareID successfully ", () => {

    //clipboard access in testing is inconsistent with chrome, doesn't work on firefox
    //https://github.com/cypress-io/cypress/issues/2752

    //get shareId
    cy.url().then(($url) => {
      const shareId = $url.split("/")[5];

      cy.window().then(($win) => {
        //use spy to check if correct arg used when
        //writing to clipboard
        cy.spy($win.navigator.clipboard, "writeText").as("writeText");
      });

      //click to copy
      cy.get("[data-testid='copy-projectId']").click();
      cy.wait(500);

      //most likely error toast will be shown in tests
      //so not checking for success/error class
      cy.get("[data-testid='copy-toasts']")
        .find("c-toast")
        .should("be.visible");

      cy.get("@writeText")
        .should("have.been.calledOnce")
        .and("have.been.calledWithExactly", shareId);
    });
  });
})
