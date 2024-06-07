//commands

// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add("login", (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add("drag", { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add("dismiss", { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite("visit", (originalFn, url, options) => { ... })

import { faker } from "../../../swift_browser_ui_frontend/node_modules/@faker-js/faker";

/*NAV BAR COMMANDS */

Cypress.Commands.add("login", (username, password) => {
  cy.get("c-login-card-actions > c-button").click();
  cy.url().should("include", "/login/");
  if (username) {
    cy.get('#classicform > [type="text"]').type(username);
  }
  if (password) {
    cy.get('[type="password"]').type(password);
  }
  cy.get('#classicform > [type="submit"]').click();
});

Cypress.Commands.add("logout", () => {
  const buttonText =
    { en: "Log out",
      fi: "Kirjaudu ulos" };

  cy.getCookie("OBJ_UI_LANG")
    .should("have.property", "value")
    .then($key => {
      cy.get("[data-testid='user-menu']").click();
      cy.contains(buttonText[$key])
        .should("be.visible")
        .click();
      cy.visit(Cypress.config().baseUrl);
    })
});

Cypress.Commands.add("changeLang", (key) => {
  const langs =
    { en: "In English" ,
      fi: "Suomeksi" };

  cy.get("[data-testid='language-selector']")
    .click();
  cy.wait(1000);
  cy.get("c-menu-items")
    .find("ul>li")
    .contains(langs[key])
    .click();
  //verify
  cy.get("[data-testid='language-selector']")
    .should("contain", langs[key]);
});

Cypress.Commands.add("selectProject", (projectName) => {
  cy.get("[data-testid='project-selector']")
    .click()
    .find("li")
    .contains(projectName)
    .click();
});

Cypress.Commands.add("switchProject", () => {
  //confirm that there's 2 projects
  cy.get("[data-testid='project-selector']")
    .find("li")
    .should("have.length", 2);

  //get currently selected project
  cy.get("[data-testid='project-selector']")
    .find("input")
    .invoke("attr", "name")
    .then($value => {
      //click sibling of currently selected
      cy.get("[data-testid='project-selector']")
        .click()
        .find("li")
        .contains($value)
        .siblings()
        .click()
  })
});

/* CONTAINER ACTIONS */

Cypress.Commands.add("addFolder", (folderName) => {
  cy.get("[data-testid='create-folder']").click();
  cy.wait(1000);
  cy.get("[data-testid='folder-name']").type(folderName);
  cy.get("[data-testid='save-folder']").click();
});

Cypress.Commands.add("searchFolder", (folderName) => {
  cy.get("[data-testid='search-box']")
    .find("input")
    .eq(0)
    .type(folderName, { force: true });
  cy.wait(5000);
});

/* DELETE */

Cypress.Commands.add("deleteFolder", (folderName) => {
  cy.get("c-data-table")
      .contains(folderName)
      .parent() //div
      .parent() //td
      .parent() //tr
      .as("containerRow");

    //click on options
    cy.get("@containerRow")
      .find("c-menu")
      .click();

    cy.get("c-menu-items")
      .find("ul>li")
      .contains("delete", { matchCase: false })
      .click();
});

Cypress.Commands.add("deleteFile", (fileName) => {
  cy.contains(fileName)
    .parent()
    .parent()
    .find("[testid='delete-object']")
    .click();
  cy.wait(3000);
  //confirm on delete modal
  cy.get("[data-testid='confirm-delete-objects']").click();
});

Cypress.Commands.add("deleteFileCheckbox", (fileName) => {
  //delete the file by checkbox
  cy.contains(fileName)
    .parent()
    .parent()
    .find("c-checkbox")
    .click();
  //click delete
  cy.get("[data-testid='delete-checked-files']").click();
  cy.wait(3000);
  //confirm on delete modal
  cy.get("[data-testid='confirm-delete-objects']").click();
});

Cypress.Commands.add("deleteFilesOnPageCheckbox", () => {
  //delete all the files on the current page by checkbox
  cy.get("[data-testid='object-table']")
    .find("thead")
    .find("c-checkbox")
    .click();
  //click delete
  cy.get("[data-testid='delete-checked-files']").click();
  cy.wait(3000);
  //confirm on delete modal
  cy.get("[data-testid='confirm-delete-objects']").click();
});

/* UPLOAD */

Cypress.Commands.add("uploadFileFromFolder", (fileName) => {
  //open upload modal
  cy.get("[data-testid='upload-file']").click({ force: true });
  cy.wait(3000);

  //check that modal opened
  cy.get("[data-testid='upload-modal']").should("be.visible");

  //add the file
  cy.get("[data-testid='select-files-input']")
    .invoke("show")
    .selectFile(Cypress.config("textFileLocation") + fileName + ".txt");
  cy.wait(3000);

  //start upload
  cy.get("[data-testid='start-upload']")
    .should("not.have.class", "disabled")
    .click();
  cy.wait(5000);
});

Cypress.Commands.add("uploadFileFromMain", (folderName, fileName) => {
  //open upload modal
  cy.get("[data-testid='upload-file']").click();
  cy.wait(3000);

  //check that modal opened
  cy.get("[data-testid='upload-modal']").should("be.visible");

  //insert folder name
  cy.get("[data-testid='upload-folder-input']")
    .find("input")
    .type(folderName);

  //add the file
  cy.get("[data-testid='select-files-input']")
    .invoke("show")
    .selectFile(Cypress.config("textFileLocation") + fileName + ".txt");
  cy.wait(3000);

  //start upload
  cy.get("[data-testid='start-upload']")
    .should("not.have.class", "disabled")
    .click();
  cy.wait(5000);
});

/* SHARING */

Cypress.Commands.add("share", (shareId, perm) => {
  //type in shareID, choose permission, save sharing
  //perms: read, read and write, view
  if (shareId) {
    cy.get("[data-testid='share-id-input']>input").type(shareId, {
      force: true,
    });
  }

  if (perm) {
    cy.get("[data-testid='select-permissions']").click({ force: true });
    cy.wait(2000);
    cy.get(`[data-testid='${perm}-perm']`).click({ force: true });
    cy.wait(2000);
  }

  cy.get("[data-testid='submit-share']").click({ force: true });
});

/*EDIT TAGS */

Cypress.Commands.add("addTags", (tags) => {
  //modal should be open
  cy.get("[data-testid='edit-tags-modal']").should("be.visible");

  //input tags and save
  cy.get("[data-testid='edit-tags-input']").type(tags.join("{enter} "));
  cy.get("[data-testid='save-edit-tags']").click();
});

Cypress.Commands.add("removeAllTags", () => {
  //modal should be open
  cy.get("[data-testid='edit-tags-modal']").should("be.visible");

  //remove tags and save
  cy.get("[data-testid='edit-tags-input']")
    .find("c-icon")
    .as("icons")

  cy.get("@icons")
    .its("length")
    .then(($length) => {
      for(let i = $length - 1; i >= 0; i--) {
        //start from highest: index changes when items are deleted
        cy.get("@icons")
          .eq(i)
          .click();
      }
    });

  cy.get("[data-testid='save-edit-tags']").click();
});

/* FIXTURES */

Cypress.Commands.add("generateFixture", (name) => {
  cy.writeFile(Cypress.config("textFileLocation") + name + ".txt", {
    hits: Cypress._.times(10, () => {
      return faker.lorem.paragraphs(50);
    }),
  });
});

Cypress.Commands.add("deleteFixtures", () => {
  //add command because config allows assets to be trashed with "cypress run"
  //but not "cypress open"
  const downloaded = Cypress.config("downloadsFolder");
  const generated = Cypress.config("textFileLocation");
  cy.task("deleteFolder", downloaded);
  cy.task("deleteFolder", generated);
})

/*OTHER */

Cypress.Commands.add("getFileContentFromOPFS", async (fileName) => {
  //retrieves file content from OPFS
  const testDirHandle = await navigator.storage.getDirectory();
  const fileHandle = await testDirHandle.getFileHandle(fileName);
  const file = await fileHandle.getFile();
  return file.text();
})

Cypress.Commands.add("deleteDB", () => {
  indexedDB.deleteDatabase("sd-connect");
});

// some exceptions like API reponse from delete we are not catching
// and we don't need to, thus we ignore
Cypress.on("uncaught:exception", () => {
  return false;
});
