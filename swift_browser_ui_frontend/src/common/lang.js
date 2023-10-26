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
        inUse: "Folder name is already in use.",
        inUseOtherPrj: "Folder name is already in use by another project.",
        invalidName: "Folder name or tag is invalid.",
        createFail: "Folder creation failed.",
        tooShort: "Please enter at least 3 characters",
        forbiddenChars: "Folder name cannot contain special " +
        "characters other than dot(.), hyphen(-), and underscore(_)",
        segments: "Folder name cannot end with '_segments'",
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
      createFolder: "Create folder",
      uploadSecondaryNav: "Upload",
      logOut: "Log out",
      folderTabs: {
        all: "All folders",
        sharedFrom: "Folders you have shared",
        sharedTo: "Folders shared with you",
      },
      folderDetails: {
        notShared: "This folder isn't shared to any projects.",
        sharing_to_one_project: "This folder is shared to one project.",
        sharing_to_many_projects: "This folder is shared to multiple projects.",
        shared_with_view: "This folder is shared with you. You can browse " +
        "this folder. (View).",
        shared_with_read:
          "This folder is shared with you. You can copy and download " +
          "the files in this folder as well as decrypt them. " +
          "(Copy and download).",
        shared_with_read_write:
          "This folder is shared with you. You can copy and download " +
          "the files in this folder as well as decrypt them. " +
          "You can also upload files to this folder. " +
          "(Copy, download and upload).",
      },
      table: {
        name: "Name",
        objects: "Objects",
        size: "Size",
        modified: "Last modified",
        activity: "Last activity",
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
        source_project_id: "Share ID of this folder",
        date_of_sharing: "Date of sharing",
        unknown_date: "Unknown",
        back_to_all_folders: "Back to all folders",
        back_to_sharing_folders: "Back to folders you have shared",
        back_to_shared_folders: "Back to folders shared with you",
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
        share_id_tooltip:
          "With this action, you can copy the Share ID: " +
          "a unique 32-digit code associated with your <b>currently " +
          "selected</b> project. Provide the Share ID to members " +
          "of other projects (e.g., via email) so that they can " +
          "share folders with you.",
        close: "Close",
        instructions: "How to share a folder",
        close_instructions: "Hide",
        share_cont: "Share the folder",
        share_title: "Share folder",
        share_other_projects: "Share with other projects",
        share_guide_intro:
          "To share a folder with another project you need to:",
        share_guide_step1:
          "1. <b>Enter the Share ID.</b> You need to know in advance " +
          "the Share ID (a 32-digit code) associated " +
          "with the project you want to share a folder with. The " +
          "recipient can copy the Share ID from the user " +
          "interface and provide it to you via email. You can share " +
          "a folder with multiple projects.",
        share_guide_step2: "2. <b>Select the permission rights:</b> ",
        share_guide_step2_list: [
          "<b>View:</b> project members can access the folder's content " +
            "but can not directly download or copy " +
            "its content.",
          "<b>Copy and download:</b> project members can copy, download " +
            "and decrypt the folder content.",
          "<b>Copy, download and upload:</b> project members can copy, " +
            "download and decrypt the folder content. They can also upload " +
            "new files to the shared folder accessible to both projects.",
        ],
        permissions: "Select permissions",
        view_perm: "View",
        read_perm: "Copy and download",
        write_perm: "Copy, download and upload",
        shared_successfully: "Folder was shared successfully!",
        remove_permission: "Permissions were removed successfully!",
        update_permission: "Permissions were changed successfully.",
        shared_table_title: "This folder is shared with",
        field_placeholder: "Add Share IDs",
        cancel: "Cancel",
        confirm: "Share",
        fail_noperm: "Please select permissions to grant.",
        fail_noid: "Please enter at least one Share ID.",
        fail_duplicate: "The project already has access to the folder.",
        invalid_share_id: " is not a valid Share ID. Please remove it.",
        invalid_share_ids: " are not valid Share IDs. Please remove them.",
      },
      download: " Download",
      downloadFiles: "Files can only be downloaded " +
      "individually because there are file or subfolder names longer than " +
      "99 characters.",
      largeDownMessage:
        "No large (> 1GiB) downloads enabled. Click to " +
        "enable them for the duration of the session.",
      largeDownAction: "Enable",
      emptyContainer: "This folder has no content.",
      emptyProject: {
        all: "There are no folders in this project.",
        sharedFrom: "You haven't shared any folders.",
        sharedTo: "No folders have been shared with you.",
      },
      sharing: "Sharing - ",
      containers: "Folders - ",
      upload: {
        duplicate: "Files with the same paths are not allowed.",
        sizeZero: "Empty files cannot be uploaded.",
        upfinish: "Finished uploading ",
        upfail: "Failed uploading ",
        upnotsupported: "Uploading is not supported by your browser",
        isStarting: "Data upload will start shortly",
        hasStarted: "Uploading has started",
        inProgress: "Upload in progress",
        longProgress: "Upload in progress",
        viewDestinationFolder: "View destination folder",
        maximize: "Maximize",
        minimize: "Minimize",
        estimate: "It may take few minutes.",
        progressLabel: "complete",
        complete: "Uploading completed",
        cancelled: "Uploading cancelled",
        uploadedItems: "Uploaded items will be displayed soon",
        addFiles: "Please add files to upload.",
        error: "Upload couldn't start. Please try again.",
        accessFail: "Folder could not be accessed.",
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
      copyfail: "Failed to copy the folder",
      tagName: "Tags (optional)",
      tagPlaceholder: "# Add a tag and press enter",
      container_ops: {
        addContainer: "Create new folder",
        norename:
          "Please note that folder names cannot be modified " +
          "after creating a folder.",
        createdFolder:
          "Created folder will be shared with all project members in ",
        viewProjectMembers: "View project members",
        deleteNote: "Folder must be empty before " + "it can be deleted.",
        deleteSuccess: "Folder was deleted.",
        folderName: "Folder name",
      },
      subfolders: {
        deleteNote:
          "Subfolders are deleted by deleting all " + "items in them.",
        deleteOneSuccess: "Subfolder was deleted.",
        deleteManySuccess: "Subfolders were deleted.",
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
        deleteManySuccess: " items deleted",
        deleteOneSuccess: " item deleted",
        deleteObjectsMessage:
          "Items can't be restored after being deleted. " +
          "Are you sure you want to proceed?",
      },
      replicate: {
        copy_folder: "Copy folder: ",
        name_newFolder: "Name new folder",
      },
      tokens: {
        empty: "No API tokens created for the project",
        title: "Create API tokens",
        identifier: "Token identifier",
        identLabel: "Insert new token identifier",
        createToken: "Create token",
        latestToken: "Latest token: ",
        copy: "Copy token",
        copyWarning:
          "Token will be displayed just this once " +
          "and recovering it is not be possible. " +
          "Please store the token somewhere " +
          "safe before closing this modal.",
        tokenCopied: "Token copied.",
        tokenRemoved: "Token removed.",
        inUse: "Token identifier already in use.",
        creationFailed: "Token creation failed.",
      },
      encrypt: {
        uploadFiles: "Upload files",
        uploadDestination: "Destination folder: ",
        upload_step1: "Create a new folder",
        upload_step2: "Files to be uploaded",
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
          "have access to this shared folder.",
        advancedOptions: "Advanced encryption options",
        enReady:
          "Encryption engine is ready. Refresh the " +
          "window to enable encryption.",
        refresh: "Refresh",
      },
      search: {
        container: "Folder",
        object: "Item",
        folder: "Subfolder",
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
        createTokens: "Create API tokens",
      },
      footerMenu: {
        title: "Swift browser",
        serviceProvider: "Service provider",
        serviceProviderLink: "#",
        menuItem1: "Item 1",
        menuItemLink1: "#",
        menuItem2: "Item 2",
        menuItemLink2: "#",
        menuItem3: "Item 3",
        menuItemLink3: "#",
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
      folder_tabs: "different types of folder",
      searchbox: "search for folders",
      tagsList: "list of tags",
      edit_tag: "edit tags",
      delete_tag: "delete tag",
      footer: "copyright information",
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
        inUse: "Kansion nimi on jo käytössä.",
        inUseOtherPrj: "Kansion nimi on jo käytössä toisessa projektissa.",
        invalidName: "Kansion nimi tai asiasana ei kelpaa.",
        createFail: "Kansion luonti epäonnistui.",
        tooShort: "Anna vähintään 3 merkkiä",
        forbiddenChars: "Kansion nimi ei voi sisältää muita " +
        "erikoismerkkejä kuin piste(.), viiva(-) ja alaviiva(_)",
        segments: "Kansion nimi ei saa päättyä '_segments'",
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
      createFolder: "Luo kansio",
      uploadSecondaryNav: "Lähetä",
      logOut: "Kirjaudu ulos",
      folderTabs: {
        all: "Kaikki kansiot",
        sharedFrom: "Jakamasi kansiot",
        sharedTo: "Sinulle jaetut kansiot",
      },
      folderDetails: {
        notShared: "Tätä kansiota ei ole jaettu toiselle projektille.",
        sharing_to_one_project: "Tämä kansio on jaettu yhdelle projektille.",
        sharing_to_many_projects: "Tämä kansio on jaettu useille projekteille.",
        shared_with_view: "Tämä kansio on jaettu kanssasi. Voit " +
        "selata tätä kansiota. (Katsele).",
        shared_with_read:
          "Tämä kansio on jaettu kanssasi. Voit kopioida ja ladata " +
          "tiedostoja tässä kansiossa ja purkaa kansion sisällön " +
          "salauksen. (Kopioi ja lataa).",
        shared_with_read_write:
          "Tämä kansio on jaettu kanssasi. Voit kopioida ja ladata " +
          "tiedostoja, sekä purkaa kansion sisällön salauksen. " +
          "Voit myös lähettää tiedostoja tähän kansioon. " +
          "(Kopioi, lataa ja lähetä).",
      },
      table: {
        name: "Nimi",
        objects: "Objekteja",
        size: "Koko",
        modified: "Muokattu viimeksi",
        activity: "Viimeisin toiminta",
        paginated: "Sivutus",
        pageNb: "sivulla",
        fileHash: "Tarkistussumma",
        fileType: "Tyyppi",
        fileDown: "Tiedoston lataus",
        folderDetails: "Ei yksityiskohtia kansioille",
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
        back_to_all_folders: "Takaisin",
        back_to_sharing_folders: "Takaisin",
        back_to_shared_folders: "Takaisin",
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
        share_id_tooltip:
          "Tällä toiminnolla voit kopioida jakamistunnuksen: uniikin " +
          "32-numeroisen koodin, joka on yhdistetty <b>valitsemaasi</b> " +
          "projektiin. Lähetä tunnus (esim. sähköpostilla) muiden projektien " +
          "jäsenille, niin he voivat jakaa kansioita sinulle.",
        close: "Sulje",
        instructions: "Kuinka jaan kansion",
        close_instructions: "Sulje ohjeet",
        share_cont: "Jaa säiliö",
        share_title: "Jaa kansio ",
        share_other_projects: "Jaa toisen projektin kanssa",
        share_guide_intro: "Kun haluat jakaa kansion toisen projektin kanssa: ",
        share_guide_step1:
          "1. <b>Syötä jakamistunnus.</b> Sinun tulee tietää " +
          "vastaanottavan projektin jakamistunnus (32-numeroinen " +
          "koodi). Vastaanottaja voi kopioida " +
          "jakamistunnuksen Kopioi jakamistunnus -napilla " +
          "ja lähettää sen sinulle esim. sähköpostilla. " +
          "Voit jakaa kansion useiden projektien kanssa.",
        share_guide_step2: "2. <b>Valitse käyttöoikeudet:</b> ",
        share_guide_step2_list: [
          "<b>Tarkastele:</b> projektin jäsenet voivat tarkastella kansion " +
            "sisältöä, mutta eivät voi ladata ja kopioida kansion sisältöä.",
          "<b>Kopioi ja lataa:</b> projektin jäsenet voivat kopioida ja " +
            "ladata kansion sisällön sekä purkaa kansion sisällön salauksen.",
          "<b>Kopioi, lataa ja lähetä:</b> projektin jäsenet voivat kopioida " +
            "ja ladata kansion sisällön sekä purkaa kansion sisällön " +
            "salauksen. He voivat myös lähettää tiedostoja jaettuun kansioon.",
        ],
        permissions: "Käyttöoikeudet",
        view_perm: "Katsele",
        read_perm: "Kopioi ja lataa",
        write_perm: "Kopioi, lataa ja lähetä",
        shared_successfully: "Kansion jakaminen onnistui.",
        remove_permission: "Käyttöoikeus poistettiin onnistuneesti.",
        update_permission: "Käyttöoikeus muutettiin onnistuneesti.",
        shared_table_title: "Tämä kansio on jaettu",
        field_placeholder: "Lisää jakamistunnus",
        cancel: "Peru",
        confirm: "Jaa",
        fail_noperm: "Valitse käyttöoikeudet.",
        fail_noid: "Anna vähintään yhden projektin jakamistunnus.",
        fail_duplicate: "Kansio on jo jaettu kyseiselle projektille.",
        invalid_share_id: " ei ole kelvollinen jakamistunnus. Poistakaa se.",
        invalid_share_ids:
          " eivät ole kelvollisia jakamistunnuksia. Poistakaa ne.",
      },
      download: " Lataa",
      downloadFiles: "Tiedostot voidaan ladata vain " +
      "erikseen, koska tiedostojen tai alikansioiden nimet ovat " +
      "yli 99 merkkiä pitkiä.",
      largeDownMessage:
        "Suurten tiedostojen (> 1Gt) lataus täytyy hyväksyä " +
        "erikseen. Paina hyväksyäksesi suuret lataukset " +
        "nykyisen kirjautumisen ajaksi.",
      largeDownAction: "Hyväksy",
      emptyContainer: "Tämä kansio on tyhjä.",
      emptyProject: {
        all: "Tässä projektissa ei ole kansioita.",
        sharedFrom: "Et ole jakanut yhtään kansiota.",
        sharedTo: "Sinulle ei ole jaettu kansioita.",
      },
      sharing: "Jako - ",
      containers: "Kansiot - ",
      upload: {
        duplicate: "Tiedostot, joilla on samat polut, eivät ole sallittuja.",
        sizeZero: "Tyhjiä tiedostoja ei voi lähettää.",
        upfinish: "Lähetettiin tiedosto ",
        upfail: "Epäonnistuttiin lähettäessä tiedosto ",
        upnotsupported: "Selain ei tue tiedostojen lähettämistä",
        hasStarted: "Lähetys aloitettu",
        isStarting: "Tiedostojen lähetys käynnistyy pian",
        inProgress: "Lähetys käynnissä",
        longProgress: "Lähetys käynnissä, lähetetään tiedostoa ",
        viewDestinationFolder: "Näytä kohdekansio",
        maximize: "Suurenna",
        minimize: "Pienennä",
        estimate: "Toiminto voi kestää muutamia minuutteja.",
        progressLabel: "valmis",
        complete: "Lähetys on valmis",
        cancelled: "Lähetys peruutettu",
        uploadedItems: "Lähetetyt tiedostot näytetään pian",
        addFiles: "Lisää ladattavat tiedostot.",
        error: "Lataus ei alkanut. Yritä uudelleen.",
        accessFail: "Kansioon ei ole pääsyä.",
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
      copysuccess: "Kansiota kopioidaan",
      copytime: "Se voi kestää muutaman sekunnin",
      copyfail: "Kansion kopiointi epäonnistui",
      tagName: "Asiasanat",
      tagPlaceholder: "# Lisää asiasana ja paina rivinvaihtoa",
      container_ops: {
        addContainer: "Luo uusi kansio",
        norename:
          "Kansiota ei voi nimetä uudelleen, " +
          "mutta sen voi kopioida uudella nimellä.",
        createdFolder: "Luotu kansio jaetaan kaikille jäsenille projektissa ",
        viewProjectMembers: "Näytä projektin jäsenet",
        deleteNote:
          "Kansion poistaminen edellyttää kaikkien " +
          "tiedostojen poistamista ensin.",
        deleteSuccess: "Kansio poistettu",
        folderName: "Kansion nimi",
      },
      subfolders: {
        deleteNote:
          "Alikansion poistaminen edellyttää sen kaikkien " +
          "tiedostojen poistamista.",
        deleteOneSuccess: "Alikansio poistettu.",
        deleteManySuccess: "Alikansiot poistettu.",
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
        deleteManySuccess: " tiedostoa poistettu",
        deleteOneSuccess: " tiedosto poistettu",
        deleteObjectsMessage:
          "Tiedostoja ei voi palauttaa poistamisen jälkeen. " +
          "Haluatko varmasti poistaa nämä tiedostot?",
      },
      replicate: {
        copy_folder: "Kopioi kansio: ",
        name_newFolder: "Nimeä uusi kansio",
      },
      tokens: {
        empty: "Tälle projektille ei ole luotu API-avaimia",
        title: "Luo API-avaimia",
        identifier: "Avainten tunnisteet",
        identLabel: "Syötä tunniste uudelle API-avaimelle",
        createToken: "Luo avain",
        latestToken: "Viimeisin avain: ",
        copy: "Kopioi avain",
        copyWarning:
          "Avain näytetään vain tämän kerran, " +
          "eikä sen kopiointi tai palautus ole mahdollista jälkeenpäin. " +
          "Tallenna avain turvalliseen paikkaan " +
          "ennen kuin suljet tämän ikkunan.",
        tokenCopied: "Avain kopioitu.",
        tokenRemoved: "Avain poistettu.",
        creationFailed: "Avaimen luonti epäonnistui.",
        inUse: "Avaimen tunniste on jo käytössä.",
      },
      encrypt: {
        uploadFiles: "Lataa tiedostoja",
        uploadDestination: "Kohdekansio: ",
        upload_step1: "Luo uusi kansio",
        upload_step2: "Ladattavat tiedostot",
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
          "joilla on pääsy tähän jaettuun kansioon.",
        advancedOptions: "Edistyneitä salausvaihtoehtoja",
        enReady:
          "Salausohjelma on valmiina. Päivitä " +
          "selainikkuna mahdollistaaksesi salauksen.",
        refresh: "Päivitä",
      },
      search: {
        container: "Kansio",
        object: "Tiedosto",
        folder: "Alikansio",
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
        createTokens: "Luo API-avaimia",
      },
      footerMenu: {
        title: "Swift browser",
        serviceProvider: "Palveluntarjoaja",
        serviceProviderLink: "#",
        menuItem1: "Menu 1",
        menuItemLink1: "#",
        menuItem2: "Menu 2",
        menuItemLink2: "#",
        menuItem3: "Menu 3",
        menuItemLink3: "#",
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
      folder_tabs: "erityyppisiä kansioita",
      searchbox: "etsi kansioita",
      tagsList: "luettelo tunnisteista",
      edit_tag: "muokata nykyisiä tunnisteita",
      delete_tag: "poista tunniste",
      footer: "tekijänoikeustiedot",
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
