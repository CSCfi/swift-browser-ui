// Ready translated locale messages

import lang_overrides from "@/assets/lang_overrides";

let default_translations = {
  en: {
    message: {
      indexOIDC: {
        logIn: "Log in",
        href: "/login/oidc",
      },
      index: {
        logIn: "Log in",
        loginmethods: [
          {
            msg: "Log in with SSO",
            href: "/login/oidc_front",
          },
        ],
      },
      error: {
        prevPage: "Go to previous page",
        login: "Go to login",
        BadRequest: "400 – Bad Request",
        BadRequest_text:
          "Something was wrong with the request. This can " +
          "be for example due to missing password and/or " +
          "username.",
        UIdown: "500 – Service Unavailable",
        UIdown_text1:
          "You are seeing this page because " +
          "the service is currently unavailable. Please check back later.",
        UIdown_text2: "You can find more information about service breaks ",
        UIdown_link_text: "here",
        UIdown_link: "#",
        Unauthorized: "401 – Not Logged In",
        Unauthorized_text:
          "You are seeing this page because your login " +
          "information was incorrect, your session expired, " +
          "or you haven’t logged in yet.",
        Notfound: "404 – Page Not Found",
        Notfound_text: "The page you were looking for was not found.",
        Forbidden: "403 – Forbidden",
        Forbidden_text:
          "You are seeing this page because you were " +
          "trying to perform an action that you are not allowed to.",
        inUseOtherPrj: "Bucket name is already in use by another project.",
        invalidName: "Bucket name is invalid.",
        createFail: "Bucket creation failed.",
        idb: "Firefox in private mode is not supported.",
        idb_text:
          "Firefox is not supported in private mode. " +
          "To continue, please turn off Firefox's private browsing or " +
          "switch to another browser.",
      },
      dropFiles: "Drag and drop folders here or ",
      support: "Support",
      program_name: "Swift browser",
      program_description:
        "Web UI for browsing contents in Swift object " + "storage systems.",
      currentProj: "Project",
      selectProj: "Select project",
      createBucket: "Create bucket",
      uploadSecondaryNav: "Upload",
      logOut: "Log out",
      bucketTabs: {
        all: "All buckets",
        sharedFrom: "Buckets you have shared",
        sharedTo: "Buckets shared with you",
      },
      bucketDetails: {
        size: "Bucket size",
        created: "Created",
        notShared: "This bucket isn't shared with other projects.",
        sharing_to_one_project: "This bucket is shared to one project.",
        sharing_to_many_projects: "This bucket is shared to multiple projects.",
        shared_with_view:
          "You can browse this bucket. (@:message.share.view_perm)",
        shared_with_read:
          "You can copy this bucket and download files in decrypted format. " +
          "(@:message.share.read_perm)",
        shared_with_read_write:
          "You can copy this bucket and download files in decrypted format. " +
          "You can upload new files or delete existing files from this " +
          "bucket. (@:message.share.write_perm)",
      },
      table: {
        name: "Name",
        objects: "Objects",
        size: "Size",
        modified: "Last modified",
        paginated: "Paginated",
        pageNb: "per page",
        tags: "Tags",
        editTags: "Edit tags",
        deleteSelected: "Delete",
        clearSelected: "Clear",
        itemSelected: "item selected",
        itemsSelected: "items selected",
        item: "item",
        items: "Items",
        itemsPerPage: "Items per page: ",
        nextPage: "Next page",
        prevPage: "Previous page",
        page: "Page",
        shared_status: "Shared status",
        sharing: "You have shared",
        shared: "Shared with you",
        edit_sharing: " Edit sharing",
        source_project_id: "Share ID of this bucket",
        date_of_sharing: "Date of sharing",
        unknown_date: "Unknown",
        back_to_all_buckets: "Back to all buckets",
        back_to_sharing_buckets: "Back to buckets you have shared",
        back_to_shared_buckets: "Back to buckets shared with you",
      },
      tableOptions: {
        displayOptions: "Display options",
        render: "Display as folders",
        text: "Display as file paths",
        timestamp: "Display time of last activity",
        fromNow: "Display time since last activity",
        hideTags: "Hide tags",
        showTags: "Display tags",
        hidePagination: "Hide pagination",
        showPagination: "Display pagination",
      },
      share: {
        share: "Share",
        share_id: "Share ID",
        share_id_copy: "Copy Share ID",
        share_id_tooltipb: "currently selected",
        share_id_tooltip:
          "With this action, you can copy the Share ID: " +
          "a unique 32-digit code associated with your {tooltipb} " +
          "project. Provide the Share ID to members " +
          "of other projects (e.g., via email) so that they can " +
          "share buckets with you.",
        close: "Close",
        instructions: "How to share a bucket",
        close_instructions: "Hide",
        share_title: "Share bucket",
        share_other_projects: "Share with other projects",
        share_guide_intro:
          "To share a bucket with another project you need to:",
        share_guide_step1b: "1. Enter the Share ID. ",
        share_guide_step1:
          "You need to know in advance " +
          "the Share ID (a 32-digit code) associated " +
          "with the project you want to share a bucket with. The " +
          "recipient can copy the Share ID from the user " +
          "interface and provide it to you via email. You can share " +
          "a bucket with multiple projects.",
        share_guide_step2: "2. Select the permission rights:",
        permissions: "Permissions",
        view_perm: "View",
        view_perm_desc:
          ": The recipient project's members can only " +
          "view the bucket content. Use this when you " +
          "need maximum certainty that your files are not distributed " +
          "further. Note that you have to be also the project manager of " +
          "the recipient project.",
        read_perm: "Transfer data",
        read_perm_desc:
          ": The recipient project's members can copy your bucket " +
          "and download files in decrypted format. Use this when you want to " +
          "transfer your data to another project.",
        write_perm: "Collaborate",
        write_perm_desc:
          ": In addition to @:message.share.read_perm permission, " +
          "the recipient project's members can upload new files or delete " +
          "existing files from your bucket. Use this when " +
          "you want the bucket to be your shared workspace.",
        shared_successfully: "Bucket was shared successfully!",
        remove_permission: "Permissions were removed successfully!",
        update_permission: "Permissions were changed successfully.",
        shared_table_title: "This bucket is shared with",
        field_placeholder: "Add Share IDs",
        cancel: "Cancel",
        confirm: "Share",
        fail_noperm: "Please select permissions to grant.",
        fail_noid: "Please enter at least one Share ID.",
        fail_duplicate: "The project already has access to the bucket.",
        fail_generic: "Sharing has failed. Please try again.",
        invalid_share_id: " is not a valid Share ID. Please remove it.",
        invalid_share_ids: " are not valid Share IDs. Please remove them.",
        perm_change_confirm: "Change permissions",
        share_delete_text:
          "Are you sure you want to " +
          "delete the sharing permissions?",
        share_delete_confirm: "Delete permissions",
      },
      emptyContainer: "This bucket has no content.",
      emptyProject: {
        all: "There are no buckets in this project.",
        sharedFrom: "You haven't shared any buckets.",
        sharedTo: "No buckets have been shared with you.",
      },
      sharing: "Sharing - ",
      containers: "Buckets - ",
      download: {
        download: " Download",
        files: "Files can only be downloaded " +
          "individually because there are file or folder names longer " +
          "than 99 characters.",
        inProgress: "Download in progress",
        complete: "Download completed",
        gathering: "Gathering a list of files",
        warnWait: "Please wait for the download to finish.",
        warnTempFiles: "Opening temporary files or folders " +
          "(.crdownload, .crswap) may interrupt the process.",
        error: "Download has failed. Please try again.",
        noRetain: "Error establishing bucket ownership. Please contact servicedesk@csc.fi " +
          "(subject: Sensitive data).",
        cancel: "Download cancelled",
      },
      upload: {
        duplicate: "Files with the same paths are not allowed.",
        sizeZero: "Empty files cannot be uploaded.",
        hasStarted: "Uploading has started",
        inProgress: "Upload in progress",
        viewDestinationBucket: "View destination bucket",
        maximize: "Maximize",
        minimize: "Minimize",
        estimate: "It may take few minutes.",
        progressLabel: "complete",
        complete: "Uploading completed",
        cancelled: "Uploading cancelled",
        uploadedItems: "Uploaded items will be displayed soon",
        addFiles: "Please add files to upload.",
        error: "Upload couldn't start. Please try again.",
        accessFail: "Bucket could not be accessed.",
        remove: "Remove from list",
      },
      close: "Close",
      copy: " Copy",
      copied: "Share ID copied to clipboard",
      copy_failed: "Copying failed",
      delete: "Delete",
      remove: "Remove",
      editTags: "Edit tags",
      cancel: "Cancel",
      save: "Save",
      options: "Options",
      copysuccess: "Copying in progress",
      copytime: "It may take few seconds",
      copyfail: "Failed to copy the bucket",
      notDecryptable: "Some downloaded files need manual decryption.",
      tagName: "Tags (optional)",
      tagPlaceholder: "# Add a tag and press enter",
      container_ops: {
        addContainer: "Create a new bucket",
        createdBucket:
          "Created bucket will be shared with all project members in ",
        viewProjectMembers: "View project members",
        downloadNotEmpty: "An empty bucket cannot be downloaded.",
        copyNotEmpty: "An empty bucket cannot be copied.",
        deleteEmpty: "Bucket must be empty before it can be deleted.",
        deleteSuccess: "Bucket was deleted.",
        bucketName: "Bucket name",
      },
      nameValidation: {
        lowerCaseOrNum:
          "Bucket name should start and end with a lowercase letter or a " +
          "number.",
        inputLength:
          "Bucket name should be between 3 and 63 characters long.",
        alphaNumHyphen1:
          "Use only lowercase Latin letters (a-z), numbers (0-9), and " +
          "hyphens (-).",
        alphaNumHyphen2: "Uppercase letters, underscore (_) and accent " +
        "letters with diacritics or special marks (åäöé) are not allowed.",
        ownable: "Bucket names must be unique across all existing buckets " +
        "in all projects.",
      },
      folders: {
        deleteNote:
          "Folders are deleted by deleting all items in them.",
        deleteOneSuccess: "Folder was deleted.",
        deleteManySuccess: "Folders were deleted.",
      },
      objects: {
        file: "File ",
        files: "Files ",
        overwriteConfirm: " already exists. Do you want to replace " +
        "this file? (Previous file will be lost.)",
        overwriteConfirmMany:
          " already exist. Do you want to replace these files? " +
          "(Previous files will be lost.)",
        overwrite: "Replace",
        filterBy: "Filter by name or tag",
        deleteConfirm: "Delete items",
        deleteObjects: "Delete items",
        deleteInProgress: "Deletion in progress",
        deleteManySuccess: " items deleted",
        deleteOneSuccess: " item deleted",
        deleteSharedObjects:
          "This action will permanently delete " +
          "items from a shared bucket. " +
          "Are you sure you want to proceed?",
        deleteObjectsMessage:
          "Items can't be restored after being deleted. " +
          "Are you sure you want to proceed?",
      },
      replicate: {
        copy: "Copy bucket: ",
        name: "Name new bucket",
      },
      apiKeys: {
        empty: "There are no API keys in this project.",
        title: "Create API keys",
        identifier: "Active keys for this project",
        identLabel: "Key name",
        identHint:
          "Give a name to your API key. Name needs to be unique.",
        create: "Create key",
        latest: "Latest key: ",
        copy: "Copy key",
        copyWarning:
          "API key will be displayed just this once " +
          "and recovering it is not be possible. " +
          "Please store the key somewhere " +
          "safe before closing this modal. " +
          "The key will be valid for 24 hours, and " +
          "will be deleted after this time period.",
        copied: "API key copied.",
        removed: "API key removed.",
        inUse: "API key name already in use",
        required: "API key name is required",
        creationFailed: "API key creation failed.",
      },
      encrypt: {
        uploadFiles: "Upload files",
        uploadDestination: "Destination bucket: ",
        uploadStep1: {
          title: "Create a new bucket",
          createAtRoot: "Bucket is created at the root level of your project.",
          nonModifiable:
            "Bucket names cannot be changed after " +
            "creation or upload. Remember, all bucket names are public; " +
            "please do not include any confidential information.",
        },
        uploadStep2: "Files to be uploaded",
        multipleReceivers: "Additional encryption keys (public keys only)",
        pubkey: "Paste public key",
        pubkeyLabel: "Public keys (SHA-256)",
        pubkeyError: "Please enter a valid ssh-ed25519 or Crypt4GH public key",
        noRecipients: "No public keys added",
        addkey: "Add key",
        dropMsg: "Select files",
        normup: "Upload",
        empty: "No files selected",
        cancel: "Cancel",
        table: {
          name: "Name",
          path: "Path",
          size: "Size",
          type: "Type",
        },
        uploadedFiles:
          "Uploaded files will be shared with all project members in ",
        uploadedToShared:
          "and all members in other projects which " +
          "have access to this shared bucket.",
        advancedOptions: "Advanced encryption options",
      },
      route: {
        title: "Switch project",
        text: "Switching to another project will interrupt ongoing " +
        "uploads and downloads. Are you sure you want to proceed?",
        confirm: "Switch project",
        cancel: "Cancel",
      },
      search: {
        container: "Bucket",
        object: "Item",
        folder: "Folder",
        tags: "Tags",
        objects: "Items",
        size: "Size",
        empty: "No results found",
        searchBy: "Search by name or tag",
        buildingIndex:
          "This project has a large number of files. Please " +
          "wait a moment and try again.",
      },
      select: {
        heading: "Select project for logging in",
        description:
          "The user account used for logging in contains " +
          "projects flagged as restricted. The interface scope is limited " +
          "when a restricted project is opened, i.e. only the restricted " +
          "project is visible during a restricted session. This means you " +
          "cannot copy or move items across projects or view items in " +
          "other projects available to you. Select a project you want to " +
          "use from the following listing, after selection you will not be " +
          "able to change the project without logging out. If you want to " +
          "browse unrestricted projects, use the unrestricted projects " +
          "button below.",
        unrestricted: "All unrestricted projects",
      },
      pwdlogin: {
        header: "Credential login",
        description: "Log in with your user credentials.",
        uname: "Username",
        pwd: "Password",
      },
      supportMenu: {
        userGuide: "User guide",
        userGuideLink: "#",
        projectInfo: "Project information",
        projectInfoBaseLink: "#",
        createAPIKeys: "Create API keys",
      },
      footerMenu: {
        title: "Swift browser",
        serviceProvider: "Service provider",
        serviceProviderLink: "#",
        menuItems: [
          { item: "Item 1", link: "#" },
          { item: "Item 2", link: "/accessibility" },
          { item: "Item 3", link: "#" },
          { item: "Item 4", link: "#" },
          { item: "Item 5", link: "#" },
        ],
      },
    },
    label: {
      logo: "link to main page",
      language_menu: "select language",
      support_menu: "user support",
      user_menu: "log out",
      copyshareid: "copy share id",
      shareid_tooltip: "tooltip for share id",
      shareid_instructions: "instructions for share id",
      list_of_shareids: "list of share ids",
      bucket_tabs: "different types of buckets",
      searchbox: "search for buckets",
      tagsList: "list of tags",
      edit_tag: "edit tags",
      delete_tag: "delete tag",
      footer: "copyright information",
    },
    accessibilityPage: {
      service: "Service",
      date: "dd.mm.yy",
      title: "@:accessibilityPage.service – Accessibility statement",
      intro1: "This accessibility statement applies to the" +
            " @:accessibilityPage.service service and was made on" +
            " @:accessibilityPage.date{'.'} The service is subject to the Act" +
            " on the Provision of Digital Services (306/2019), which requires"+
            " that public online services must be accessible.",
      intro2: "The accessibility of the service has been evaluated by" +
                  " an external organization.",
      part1: {
        heading: "Compliance status" ,
        text: "The website is partially compliant with the requirements of" +
            " the Web Content Accessibility Guidelines (WCAG) 2.1 level AA.",
      },
      part2: {
        heading: "Non-accessible content",
        text: "Despite our best efforts to ensure accessibility of" +
            " @:accessibilityPage.service{','} the website is not yet fully" +
            " compliant with the requirements (WCAG 2.1) and there may be" +
            " some limitations.",
        subheading1: "Non-accessible content and its shortcomings",
        subheading2: "Accessibility requirements that are not met",
        subparts: [
          {
            heading: "Perceivable: Some structural deficiencies",
            text1: "The page has content that is not accessible with" +
                " assistive technology devices. ",
            text2: "1.3.1 Info and Relationships",
          },
          {
            heading: "Perceivable: Contrast issues",
            text1: "A few elements have a few contrast issues.",
            text2: "1.4.3 Contrast (Minimum)",
          },
          {
            heading: "Perceivable: Problems with small screens and" +
                    " in mobile use",
            text1: "The site is not responsive, and it is partially" +
                    " impossible to use with mobile devices and assistive" +
                    " technology. Some of the content and functions are not" +
                    " available for mobile users. ",
            text2: "1.4.10 Reflow",
          },
          {
            heading: "Perceivable: Deficiencies in focus and hover functions",
            text1: "There are parts of the service where the cursor does" +
                    " not work correctly and pointing functions automatically" +
                    " trigger a transition to another page automatically. " +
                    "This is a disadvantage for users of assistive technology.",
            text2: "1.4.13 Content on Hover or Focus",
          },
          {
            heading: "Operable: Problems with focus order",
            text1: "When navigating with a keyboard or on a mobile device in"+
                  " assistive mode, the cursor does not always move logically.",
            text2: "2.4.3 Focus Order",
          },
          {
            heading: "Operable: Problems with focus visibility",
            text1: "When navigating the website with a keyboard, the cursor" +
                  " sometimes disappears completely.",
            text2: "2.4.7 Focus Visible",
          },
          {
            heading: "Understandable: Problems with focus functions",
            text1: "In some drop-down menus, hovering over a selection" +
                    " automatically triggers an action that opens new content" +
                    " without the user consciously making a selection.",
            text2: "3.2.1 On Focus",
          },
        ],
      },
      part3: {
        heading: "Did you notice an accessibility issue in our" +
                " digital service? Let us know and we will do our best to" +
                " correct the shortcoming",
        subheading: "Reporting issues",
        text1: "To report any issues, reach out to CSC's service desk:",
        text2: [
          { list: "Email" },
          { list: "Phone" },
        ],
      },
      part4: {
        heading: "Supervisory authority",
        authorityLink: "#",
        authorityName: "Authority name",
        text: "If you notice accessibility problems on the website," +
              " start by giving feedback to us, that is, the website" +
              " administrator. Receiving a response may take 14 days. If you" +
              " are not satisfied with the response from us or if you do not" +
              " receive any response within two weeks, you may file a report" +
              " with the { authorityName }. The agency website has detailed" +
              " instructions (in Finnish and Swedish only) on how to file a" +
              " complaint and how the issue will be processed.",
      },
      part5: {
        heading: "Supervisory authority's contact information",
        text: [
          { list: "Name" },
          { list: "Unit" },
          { list: "Website" },
          { list: "Email" },
          { list: "Phone number"},
        ],
      },
      part6: {
        heading: "We are constantly working to improve accessibility",
        subheading: "We are committed to improving the accessibility of our" +
                  " digital services",
        text1: "We will update this statement as we correct the" +
                " deficiencies. We are committed to improving the" +
                " accessibility of online services. We ensure accessibility" +
                " with, among other things, the following measures: ",
        text2: [
          { list: "We take accessibility requirements into account when we" +
                " develop services.",
          },
          { list: "We already take accessibility requirements into account" +
                " when we make purchases.",
          },
          { list : "We support our staff in producing accessible content." },
        ],
      },
    },
  },
  fi: {
    message: {
      indexOIDC: {
        logIn: "Kirjaudu",
        href: "/login/oidc",
      },
      index: {
        logIn: "Kirjaudu sisään",
        loginmethods: [
          {
            msg: "Kirjaudu SSO:ta käyttäen",
            href: "/login/oidc_front",
          },
        ],
      },
      error: {
        prevPage: "Siirry edelliselle sivulle",
        login: "Siirry kirjautumissivulle",
        BadRequest: "400 – Virheellinen pyyntö",
        BadRequest_text:
          "Virhe sivupyynnössä. Tämä voi johtua esimerkiksi " +
          "puuttuvasta salasanasta ja/tai käyttäjänimestä ",
        UIdown: "500 – Palvelu ei ole saatavilla",
        UIdown_text1:
          "Näet tämän sivun, koska palvelu " +
          "ei ole tällä hetkellä saatavilla.",
        UIdown_text2: "Löydät tietoa huoltokatkoistamme ",
        UIdown_link_text: "täältä",
        UIdown_link: "#",
        Unauthorized: "401 – Et ole kirjautunut sisään",
        Unauthorized_text:
          "Näet tämän sivun, koska kirjautumistiedoissasi " +
          "oli virhe, sessiosi umpeutui tai et ole kirjautunut sisään.",
        Notfound: "404 – Sivua ei löydy",
        Notfound_text: "Etsimääsi sivua ei löydy.",
        Forbidden: "403 – Kielletty toiminto",
        Forbidden_text:
          "Näet tämän sivun, koska yritit suorittaa " +
          "kielletyn toiminnon.",
        inUseOtherPrj: "Ämpärin nimi on jo käytössä toisessa projektissa.",
        invalidName: "Ämpärin nimi ei kelpaa.",
        createFail: "Ämpärin luonti epäonnistui.",
        idb: "Firefoxin yksityinen selaus ei ole tuettu.",
        idb_text:
          "Firefoxin yksityinen selaustila ei ole tuettu." +
          "Voidaksesi kirjautua vaihda pois yksityisestä selaustilasta " +
          "tai käytä toista selainta.",
      },
      dropFiles: "Vedä ja pudota kansiot tähän tai ",
      support: "Tuki",
      program_name: "Swift browser",
      program_description:
        "Web-käyttöliittymä tallennettujen tiedostojen " +
        "selaamiseen Swift-objektitietojärjestelmissä.",
      currentProj: "Projekti",
      selectProj: "Valitse projekti",
      createBucket: "Luo ämpäri",
      uploadSecondaryNav: "Lähetä",
      logOut: "Kirjaudu ulos",
      bucketTabs: {
        all: "Kaikki ämpärit",
        sharedFrom: "Jakamasi ämpärit",
        sharedTo: "Sinulle jaetut ämpärit",
      },
      bucketDetails: {
        size: "Ämpärin koko",
        created: "Luotu",
        notShared: "Tätä ämpäriä ei ole jaettu toiselle projektille.",
        sharing_to_one_project: "Tämä ämpäri on jaettu yhdelle projektille.",
        sharing_to_many_projects: "Tämä ämpäri on jaettu useille projekteille.",
        shared_with_view:
          "Voit selata tätä ämpäriä. (@:message.share.view_perm)",
        shared_with_read:
          "Voit kopioida ämpärin, ladata " +
          "tiedostoja tässä ämpärissä ja purkaa ämpärin sisällön " +
          "salauksen. (@:message.share.read_perm)",
        shared_with_read_write:
          "Voit kopioida ja ladata " +
          "tiedostoja, sekä purkaa ämpärin sisällön salauksen. " +
          "Voit lähettää uusia tai poistaa jo ämpärissä olevia tiedostoja. " +
          "(@:message.share.write_perm)",
      },
      table: {
        name: "Nimi",
        objects: "Objekteja",
        size: "Koko",
        modified: "Muokattu viimeksi",
        paginated: "Sivutus",
        pageNb: "sivulla",
        fileHash: "Tarkistussumma",
        fileType: "Tyyppi",
        fileDown: "Tiedoston lataus",
        bucketDetails: "Ei yksityiskohtia ämpäreille",
        clearChecked: "Poista valinnat",
        tags: "Asiasanat",
        editTags: "Muokkaa asiasanoja",
        deleteSelected: "Poista",
        clearSelected: "Tyhjennä",
        itemSelected: "kohde valittu",
        itemsSelected: "kohdetta valittu",
        item: "tiedosto",
        items: "Tiedostot",
        itemsPerPage: "Tiedostoja sivulla: ",
        nextPage: "Seuraava sivu",
        prevPage: "Edellinen sivu",
        page: "Sivu",
        shared_status: "Jakaminen",
        sharing: "Olet jakanut",
        shared: "Jaettu kanssasi",
        edit_sharing: " Muokkaa jakamista",
        source_project_id: "Jakamistunnus",
        date_of_sharing: "Jakamispäivämäärä",
        unknown_date: "Tuntematon",
        back_to_all_buckets: "Takaisin",
        back_to_sharing_buckets: "Takaisin",
        back_to_shared_buckets: "Takaisin",
      },
      tableOptions: {
        displayOptions: "Näyttöasetukset",
        render: "Näytä tiedostot kansioina",
        text: "Näytä tiedostot polkuina",
        timestamp: "Näytä viimeisimmän toiminnan aika",
        fromNow: "Näytä aika viimeisimmästä toiminnasta",
        hideTags: "Piilota asiasanat",
        showTags: "Näytä asiasanat",
        hidePagination: "Piilota sivutus",
        showPagination: "Näytä sivutus",
      },
      share: {
        share: "Jaa",
        share_id: "Jakamistunnus",
        share_id_copy: "Kopioi jakamistunnus",
        share_id_tooltipb: "valitsemaasi",
        share_id_tooltip:
          "Tällä toiminnolla voit kopioida jakamistunnuksen: uniikin " +
          "32-numeroisen koodin, joka on yhdistetty {tooltipb} " +
          "projektiin. Lähetä tunnus (esim. sähköpostilla) muiden projektien " +
          "jäsenille, niin he voivat jakaa ämpäreitä sinulle.",
        close: "Sulje",
        instructions: "Kuinka jaan ämpärin",
        close_instructions: "Sulje ohjeet",
        share_title: "Jaa ämpäri ",
        share_other_projects: "Jaa toisen projektin kanssa",
        share_guide_intro: "Kun haluat jakaa ämpärin toisen projektin kanssa: ",
        share_guide_step1b: "1. Syötä jakamistunnus. ",
        share_guide_step1:
          "Sinun tulee tietää " +
          "vastaanottavan projektin jakamistunnus (32-numeroinen " +
          "koodi). Vastaanottaja voi kopioida " +
          "jakamistunnuksen Kopioi jakamistunnus -napilla " +
          "ja lähettää sen sinulle esim. sähköpostilla. " +
          "Voit jakaa ämpärin useiden projektien kanssa.",
        share_guide_step2: "2. Valitse käyttöoikeudet: ",
        permissions: "Käyttöoikeudet",
        view_perm: "Katsele",
        view_perm_desc:
          ": Vastaanottavan projektin jäsenet voivat tarkastella ämpärin " +
          "sisältöä. Käytä tätä, kun tarvitset varmuuden, ettei " +
          "tiedostojasi jaeta eteenpäin. Huomaa, että " +
          "sinun tulee olla myös vastaanottavan projektin omistaja.",
        read_perm: "Siirrä tiedostot",
        read_perm_desc:
          ": Vastaanottavan projektin jäsenet voivat kopioida ämpärisi " +
          ", ladata tiedostot sekä purkaa ämpärin sisällön salauksen. " +
          "Käytä tätä, kun haluat siirtää tiedostosi toiselle projektille.",
        write_perm: "Yhteiskäyttö",
        write_perm_desc:
          ": @:message.share.read_perm -oikeuksien lisäksi vastaanottavan " +
          "projektin jäsenet voivat lähettää uusia tai poistaa jo ämpärissä " +
          "olevia tiedostoja. Käytä tätä, kun haluat käyttää " +
          "ämpäriä jaettuna työtilana.",
        shared_successfully: "Ämpärin jakaminen onnistui.",
        remove_permission: "Käyttöoikeus poistettiin onnistuneesti.",
        update_permission: "Käyttöoikeus muutettiin onnistuneesti.",
        shared_table_title: "Tämä ämpäri on jaettu",
        field_placeholder: "Lisää jakamistunnus",
        cancel: "Peru",
        confirm: "Jaa",
        fail_noperm: "Valitse käyttöoikeudet.",
        fail_noid: "Anna vähintään yhden projektin jakamistunnus.",
        fail_duplicate: "Ämpäri on jo jaettu kyseiselle projektille.",
        fail_generic: "Jakaminen epäonnistui. Yritä uudelleen.",
        invalid_share_id: " ei ole kelvollinen jakamistunnus. Poistakaa se.",
        invalid_share_ids:
          " eivät ole kelvollisia jakamistunnuksia. Poistakaa ne.",
        perm_change_confirm: "Muuta käyttöoikeus",
        share_delete_text: "Haluatko varmasti poistaa käyttöoikeuden?",
        share_delete_confirm: "Poista käyttöoikeus",
      },
      emptyContainer: "Tämä ämpäri on tyhjä.",
      emptyProject: {
        all: "Tässä projektissa ei ole ämpäreitä.",
        sharedFrom: "Et ole jakanut yhtään ämpäriä.",
        sharedTo: "Sinulle ei ole jaettu ämpäreitä.",
      },
      sharing: "Jako - ",
      containers: "Ämpärit - ",
      download: {
        download: " Lataa",
        files: "Tiedostot voidaan ladata vain " +
          "erikseen, koska tiedostojen tai kansioiden nimet ovat " +
          "yli 99 merkkiä pitkiä.",
        inProgress: "Lataus käynnissä",
        gathering: "Haetaan listaa tiedostoista",
        complete: "Lataus on valmis",
        warnWait: "Odota, kunnes lataus on valmis. ",
        warnTempFiles: "Väliaikaisten tiedostojen tai kansioiden " +
        "(.crdownload, .crswap) avaaminen voi keskeyttää latauksen.",
        error: "Lataus epäonnistui. Yritä uudelleen.",
        noRetain: "Ämpärin omistusoikeuden varmennus epäonnistui. Ota yhteyttä " +
          "servicedesk@csc.fi (aihe: sensitive data).",
        cancel: "Lataus peruutettu",
      },
      upload: {
        duplicate: "Tiedostot, joilla on samat polut, eivät ole sallittuja.",
        sizeZero: "Tyhjiä tiedostoja ei voi lähettää.",
        hasStarted: "Lähetys aloitettu",
        inProgress: "Lähetys käynnissä",
        viewDestinationBucket: "Näytä kohdeämpäri",
        maximize: "Suurenna",
        minimize: "Pienennä",
        estimate: "Toiminto voi kestää muutamia minuutteja.",
        progressLabel: "valmis",
        complete: "Lähetys on valmis",
        cancelled: "Lähetys peruutettu",
        uploadedItems: "Lähetetyt tiedostot näytetään pian",
        addFiles: "Lisää ladattavat tiedostot.",
        error: "Lataus ei alkanut. Yritä uudelleen.",
        accessFail: "Ämpäriin ei ole pääsyä.",
        remove: "Poista listalta",
      },
      close: "Sulje",
      copy: " Kopioi",
      copied: "Jakamistunnus kopioitu leikepöydälle.",
      copy_failed: "Kopiointi epäonnistui.",
      delete: "Poista",
      remove: "Poista",
      editTags: "Muokkaa asiasanoja",
      cancel: "Peruuta",
      save: "Tallenna",
      options: "Valinnat",
      copysuccess: "Ämpäriä kopioidaan",
      copytime: "Se voi kestää muutaman sekunnin",
      copyfail: "Ämpärin kopiointi epäonnistui",
      notDecryptable:
        "Joidenkin tiedostojen salaus on purettava erikseen latauksen " +
        "jälkeen.",
      tagName: "Asiasanat",
      tagPlaceholder: "# Lisää asiasana ja paina rivinvaihtoa",
      container_ops: {
        addContainer: "Luo uusi ämpäri",
        createdBucket: "Luotu ämpäri jaetaan kaikille jäsenille projektissa ",
        viewProjectMembers: "Näytä projektin jäsenet",
        downloadNotEmpty: "Tyhjää ämpäriä ei voi ladata.",
        copyNotEmpty: "Tyhjää ämpäriä ei voi kopioida.",
        deleteEmpty:
          "Ämpärin poistaminen edellyttää kaikkien " +
          "tiedostojen poistamista ensin.",
        deleteSuccess: "Ämpäri poistettu",
        bucketName: "Ämpärin nimi",
      },
      nameValidation: {
        lowerCaseOrNum:
          "Ämpärin nimi alkaa ja päättyy pienellä kirjaimella tai numerolla.",
        inputLength: "Ämpärin nimi on 3-63 merkkiä pitkä.",
        alphaNumHyphen1: "Käytä vain latinalaisia pieniä aakkosia (a-z), " +
        "numeroita (0-9) ja väliviivaa (-).",
        alphaNumHyphen2: "Isot kirjaimet, alaviiva (_) ja kirjaimet, " +
        "joissa on aksenttimerkkejä tai erikoismerkkejä (åäöé) eivät " +
        "ole sallittuja.",
        ownable: "Ämpärin nimen tulee olla uniikki kaikkien ämpäreiden " +
        "kesken kaikissa projekteissa.",
      },
      folders: {
        deleteNote:
          "Kansion poistaminen edellyttää sen kaikkien " +
          "tiedostojen poistamista.",
        deleteOneSuccess: "Kansio poistettu.",
        deleteManySuccess: "Kansiot poistettu.",
      },
      objects: {
        file: "Tiedosto ",
        files: "Tiedostot ",
        overwriteConfirm:
          " on jo olemassa. Haluatko korvata tiedoston? " +
          "(Edellinen tiedosto poistetaan.)",
        overwriteConfirmMany:
          " ovat jo olemassa. Haluatko korvata tiedostot? " +
          "(Edelliset tiedostot poistetaan.)",
        overwrite: "Korvaa",
        filterBy: "Suodata nimellä tai asiasanalla",
        deleteConfirm: "Poista tiedostot",
        deleteObjects: "Poista tiedostot",
        deleteInProgress: "Poisto käynnissä",
        deleteManySuccess: " tiedostoa poistettu",
        deleteOneSuccess: " tiedosto poistettu",
        deleteSharedObjects:
         "Tällä toiminnolla poistat " +
         "tiedostot jaetusta ämpäristä pysyvästi. " +
         "Haluatko varmasti poistaa nämä tiedostot?",
        deleteObjectsMessage:
          "Tiedostoja ei voi palauttaa poistamisen jälkeen. " +
          "Haluatko varmasti poistaa nämä tiedostot?",
      },
      replicate: {
        copy: "Kopioi ämpäri: ",
        name: "Nimeä uusi ämpäri",
      },
      apiKeys: {
        empty: "Tälle projektille ei ole luotu API-avaimia",
        title: "Luo API-avaimia",
        identifier: "Tämän projektin aktiiviset API-avaimet",
        identLabel: "Avaimen nimi",
        identHint:
          "Anna avaimelle nimi. Avaimen nimen on oltava yksilöllinen.",
        create: "Luo avain",
        latest: "Viimeisin avain: ",
        copy: "Kopioi avain",
        copyWarning:
          "Avain näytetään vain tämän kerran, " +
          "eikä sen kopiointi tai palautus ole mahdollista jälkeenpäin. " +
          "Tallenna avain turvalliseen paikkaan " +
          "ennen kuin suljet tämän ikkunan. " +
          "Avain on luomisen jälkeen voimassa 24 tuntia, jonka jälkeen " +
          "se poistetaan automaattisesti.",
        copied: "Avain kopioitu.",
        removed: "Avain poistettu.",
        creationFailed: "Avaimen luonti epäonnistui.",
        inUse: "Avaimen nimi on jo käytössä",
        required: "Avaimen nimi on pakollinen",
      },
      encrypt: {
        uploadFiles: "Lataa tiedostoja",
        uploadDestination: "Kohdeämpäri: ",
        uploadStep1: {
          title: "Luo uusi ämpäri",
          createAtRoot: "Ämpäri luodaan projektin päätasolle.",
          nonModifiable: "Ämpärin nimiä ei voi " +
          "muokata luomisen tai lataamisen jälkeen. Ämpäreiden nimet ovat " +
          "julkisia ja niissä ei tulisi käyttää luottamuksellisia tietoja.",
        },
        uploadStep2: "Ladattavat tiedostot",
        multipleReceivers: "Lisää salausavaimia (vain julkiset avaimet)",
        addkey: "Lisää avain",
        pubkey: "Liitä julkinen avain",
        pubkeyLabel: "Julkiset avaimet (SHA-256)",
        pubkeyError: "Anna kelvollinen ssh-ed25519 tai Crypt4GH julkinen avain",
        noRecipients: "Ei lisättyjä julkisia avaimia",
        dropMsg: "Valitse tiedostot",
        normup: "Lähetä",
        empty: "Ei valittuja tiedostoja",
        cancel: "Peruuta",
        table: {
          name: "Nimi",
          path: "Polku",
          size: "Koko",
          type: "Tyyppi",
        },
        uploadedFiles:
          "Lähetetyt tiedostot jaetaan kaikille jäsenille projektissa ",
        uploadedToShared:
          "ja myös kaikille jäsenille muissa projekteissa, " +
          "joilla on pääsy tähän jaettuun ämpäriin.",
        advancedOptions: "Edistyneitä salausvaihtoehtoja",
      },
      route: {
        title: "Vaihda projektia",
        text: "Tämä toiminto keskeyttää käynnissä olevat " +
        "lataukset. Haluatko varmasti vaihtaa projektia?",
        confirm: "Vaihda projektia",
        cancel: "Peruuta",
      },
      search: {
        container: "Ämpäri",
        object: "Tiedosto",
        folder: "Kansio",
        tags: "Asiasanat",
        objects: "Tiedostoa",
        size: "Koko",
        empty: "Tuloksia ei löytynyt",
        searchBy: "Etsi nimellä tai asiasanalla",
        buildingIndex:
          "Tässä projektissa on paljon tiedostoja. Odota " +
          "hetki ja yritä uudelleen.",
      },
      select: {
        heading: "Valitse projekti kirjautuaksesi sisään",
        description:
          "Käyttäjällä on pääsy rajoitettuihin projekteihin. " +
          "Selatessa rajoitettua projektia käyttöliittymän pääsy on " +
          "rajattu, eli vain rajatun projektin sisältö on näkyvissä. " +
          "Tiedostojen kopiointi ja siirto projektista toiseen, ja " +
          "muiden projektien sisällön selailu on estetty. Valitse " +
          "projekti, jota haluat käyttää. Valinnan jälkeen projektin " +
          "vaihto onnistuu vain kirjautumalla ulos. Mikäli haluat " +
          "selailla vain rajoittamattomia projekteja, paina " +
          "rajoittamattomien projektien nappia alla.",
        unrestricted: "Kaikki rajoittamattomat projektit",
      },
      pwdlogin: {
        header: "Käyttäjätunnuksella kirjautuminen",
        description: "Kirjaudu käyttäen käyttäjätunnustasi.",
        uname: "Käyttäjänimi",
        pwd: "Salasana",
      },
      supportMenu: {
        userGuide: "Käyttöohje",
        userGuideLink: "#",
        projectInfo: "Projektin tiedot",
        projectInfoBaseLink: "#",
        createAPIKeys: "Luo API-avaimia",
      },
      footerMenu: {
        title: "Swift browser",
        serviceProvider: "Palveluntarjoaja",
        serviceProviderLink: "#",
        menuItems: [
          { item: "Menu 1", link: "#" },
          { item: "Menu 2", link: "/accessibility" },
          { item: "Menu 3", link: "#" },
          { item: "Menu 4", link: "#" },
          { item: "Menu 5", link: "#" },
        ],
      },
    },
    label: {
      logo: "linkki etusivulle",
      language_menu: "kieli",
      support_menu: "käyttäjätuki",
      user_menu: "kirjaudu ulos",
      copyshareid: "kopioi jakotunnus",
      shareid_tooltip: "työkaluvinkki jaa tunnukselle",
      shareid_instructions: "ohjeita varten jaa tunnukselle",
      list_of_shareids: "lista jaa tunnuksista",
      bucket_tabs: "erityyppisiä ämpäreitä",
      searchbox: "etsi ämpäreitä",
      tagsList: "luettelo tunnisteista",
      edit_tag: "muokata nykyisiä tunnisteita",
      delete_tag: "poista tunniste",
      footer: "tekijänoikeustiedot",
    },
    accessibilityPage: {
      service: "Service",
      date: "dd.mm.yy",
      title: "@:accessibilityPage.service – Saavutettavuusseloste",
      intro1: "Tämä saavutettavuusseloste koskee" +
            " @:accessibilityPage.service{'-'}palvelua ja se on päivätty" +
            " @:accessibilityPage.date{'.'} Palveluun sovelletaan lakia" +
            " digitaalisten palvelujen tarjoamisesta (306/2019), jonka mukaan" +
            " julkisten verkkopalveluiden on oltava saavutettavia.",
      intro2: "Palvelun saavutettavuuden on arvioinut ulkopuolinen" +
              " organisaatio.",
      part1: {
        heading: "Verkkosivuston saavutettavuuden tila" ,
        text: "Sivusto on osittain Verkkosisällön saavutettavuusohjeet" +
              " (WCAG) 2.1 -tason AA vaatimusten mukainen.",
      },
      part2: {
        heading: "Ei-saavutettava osio",
        text: "Huolimatta pyrkimyksistämme varmistaa" +
            " @:accessibilityPage.service{'-'}verkkosivuston saavutettavuus," +
            " sivusto ei ole vielä täysin vaatimusten (WCAG 2.1) mukainen ja" +
            " joidenkin osioiden saavutettavuudessa voi olla ongelmia.",
        subheading1: "Ei-saavutettava osio ja sen puutteet",
        subheading2: "Esteettömyysvaatimukset, jotka eivät täyty",
        subparts: [
          {
            heading: "Havaittavuus: Rakenteelliset puutteet",
            text1: "Verkkosivustolla on osioita, jotka eivät ole" +
                  " yhteensopivia avustavan teknologian kanssa.",
            text2: "1.3.1 Informaatio ja suhteet",
          },
          {
            heading: "Havaittavuus: Kontrastiongelmat",
            text1: "Joissakin elementeissä on ongelmia kontrastin kanssa.",
            text2: "1.4.3 Kontrasti (Minimi)",
          },
          {
            heading: "Havaittavuus: Ongelmat pienillä näytöillä ja" +
                    " mobiilikäytössä",
            text1: "Sivusto ei ole responsiivinen, ja osia siitä on" +
                  " mahdotonta käyttää mobiililaitteilla ja avustavan" +
                  " teknologian kanssa. Osa sisällöstä ja toiminnoista eivät" +
                  " ole käytettävissä mobiililaitteilla.",
            text2: "1.4.10 Responsiivisuus",
          },
          {
            heading: "Havaittavuus: Puutteet osoitin- ja kohdistustoiminnoissa",
            text1: "Palvelussa on osia, joissa kohdistin ei toimi oikein ja" +
                  " osoitintoiminnot käynnistävät siirtymisen toiselle" +
                  " sivulle automaattisesti. Tämä on haitta avustavan" +
                  " teknologian käyttäjille.",
            text2: "1.4.13 Sisältö osoitettaessa tai kohdistettaessa",
          },
          {
            heading: "Hallittavuus: Ongelmat kohdistusjärjestyksessä",
            text1: "Navigoitaessa näppäimistöllä tai mobiililaitteella" +
                  " avustavassa tilassa kohdistin ei aina liiku loogisesti.",
            text2: "2.4.3 Kohdistusjärjestys",
          },
          {
            heading: "Hallittavuus: Ongelmat näkyvän kohdistuksen kanssa",
            text1: "Näppäimistöä käytettäessä kohdistin katoaa joskus" +
                  " kokonaan palvelun käytön aikana.",
            text2: "2.4.7 Näkyvä kohdistus",
          },
          {
            heading: "Ymmärrettävyys: Ongelmat kohdistamisessa",
            text1: "Joissakin pudotusvalikoissa oleva sisältö" +
                  " avautuu pelkästä kohdistuksesta käyttäjän tekemättä" +
                  " valintaa.",
            text2: "3.2.1 Kohdistaminen",
          },
        ],
      },
      part3: {
        heading: "Havaitsitko digitaalisessa palvelussamme" +
                " saavutettavuusesteitä? Otathan yhteyttä ja teemme parhaamme" +
                " korjataksemme puutteen",
        subheading: "Ongelmista ilmoittaminen",
        text1: "Jos haluat ilmoittaa ongelmista, ota yhteyttä CSC:n" +
              " asiakaspalveluun:",
        text2: [
          { list: "Sähköposti" },
          { list: "Puhelin" },
        ],
      },
      part4: {
        heading: "Valvontaviranomainen",
        authorityLink: "#",
        authorityName: "Authority name",
        text: "Jos huomaat verkkosivustossa saavutettavuusongelmia, anna" +
            " palautetta ensin meille, eli verkkosivuston ylläpitäjälle." +
            " Vastaamme yhteydenottoosi 14 päivän kuluessa. Jos et ole" +
            " tyytyväinen meiltä saamaasi vastaukseen, tai vastauksemme ei" +
            " saavu 14 päivän kuluessa, voit tehdä ilmoituksen" +
            " { authorityName }. Viraston verkkosivuilla on yksityiskohtaiset" +
            " ohjeet (vain suomeksi ja ruotsiksi) valituksen tekemiseen ja" +
            " ilmoituksen käsittelyn etenemiseen.",
      },
      part5: {
        heading: "Valvontaviranomaisen yhteystiedot",
        text: [
          { list: "Nimi" },
          { list: "Yksikkö" },
          { list: "Verkkosivusto" },
          { list: "Sähköposti" },
          { list: "Puhelin"},
        ],
      },
      part6: {
        heading: "Pyrimme jatkuvasti parantamaan saavutettavuutta",
        subheading: "Olemme sitoutuneet parantamaan digitaalisten" +
                  " palvelujemme saavutettavuutta",
        text1: "Päivitämme tätä selostetta korjatessamme puutteita. Olemme" +
              " sitoutuneet parantamaan verkkopalveluiden saavutettavuutta." +
              " Varmistamme saavutettavuuden muun muassa seuraavilla" +
              " toimenpiteillä:",
        text2: [
          { list: "Otamme esteettömyysvaatimukset huomioon kehittäessämme" +
                " palveluita.",
          },
          { list: "Otamme saavutettavuusvaatimukset huomioon jo tehdessämme"+
                " hankintoja.",
          },
          { list : "Tuemme henkilöstöämme saavutettavan sisällön" +
                " tuottamisessa.",
          },
        ],
      },
    },
  },
};

let translations = default_translations;

function nestedJoin(dst, src) {
  // Join two objects with nested content overriding with the latter
  let to_assign = [];
  for (let [key, value] of Object.entries(src)) {
    if (typeof value == "object") {
      if (key in dst) {
        to_assign.push([key, nestedJoin(dst[key], src[key])]);
      } else {
        to_assign.push([key, src[key]]);
      }
    } else {
      to_assign.push([key, value]);
    }
  }
  let ret = Object.assign(dst, Object.fromEntries(to_assign));
  return ret;
}

// Override keys according to lang_overrides
translations = nestedJoin(translations, lang_overrides);

export default translations;
