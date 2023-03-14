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
        frontPage: "Go to front page",
        BadRequest: "400 – Bad Request",
        BadRequest_text:
          "Something was wrong with the request. This can " +
          "be for example due to missing password and/or " +
          "username.",
        UIdown: "503 – Service Unavailable",
        UIdown_text: "Allas user interface is currently unavailable",
        Unauthorized: "401 – Not Logged In",
        Unauthorized_text:
          "The action requested requires logging " +
          "in, or the log in credentials were incorrect. " +
          "Use the button below to Log in.",
        Notfound: "404 – Page Not Found",
        Notfound_text:
          "The page you were looking for was not found.",
        Forbidden: "403 – Forbidden",
        Forbidden_text:
          "Your previous request could not be fulfilled.",
        inUse: "Folder name already in use.",
        invalidName: "Folder name is invalid.",
        createFail: "Folder creation failed.",
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
        shared_with_read:
          "This folder is shared with you. (Read access)",
        shared_with_read_write:
          "This folder is shared with you. You can view, download, upload" +
          " and edit tags in this folder (Read and write access).",
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
        back_to_all_folders: "Back to all folders",
        back_to_sharing_folders: "Back to folders you have shared",
        back_to_shared_folders: "Back to folders shared with you",
      },
      tableOptions: {
        displayOptions: "Display options",
        render: "Show as folders",
        text: "Show as objects",
        hideTags: "Hide tags",
        showTags: "Display tags",
        hidePagination: "Hide pagination",
        showPagination: "Display pagination",
      },
      dashboard: {
        projectInfo: "Project information",
        projectInfoBaseLink: "#",
      },
      share: {
        share: "Share",
        share_id: "Share ID",
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
        share_subtitle:
          "This folder is shared by default " +
          "with all project members in the project ",
        share_other_projects: "Share with other projects",
        share_guide_intro:
          "To share a folder with another project you need to:",
        share_guide_step1:
          "1. Enter the Share ID. You need to know in advance " +
          "the Share ID (a 32-digit code) associated " +
          "with the project you want to share a folder with. The " +
          "recipient can copy the Share ID from the user " +
          "interface and provide it to you via email. You can share " +
          "a folder with multiple projects.",
        share_guide_step2:
          "2. Select the permission rights: ",
        share_guide_step2_list: [
          "View: project members can access the folder's content " +
          "but can not directly download or copy " +
          "its content.",
          "Copy and download: project members can copy, download " +
          "and decrypt the folder content.",
          "Copy, download and upload: project members can copy, " +
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
        fail_noperm: "Please select permissions to grant!",
        fail_noid: "Please give at least one Project Identifier!",
        fail_duplicate: "The project already has access to the folder!",
      },
      download: " Download",
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
        complete: "Uploading completed",
        cancelled: "Uploading cancelled",
      },
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
        deleteConfirm: "Delete folder",
        deleteNote: "You can only delete empty folders. " +
        "Please delete all items first.",
        deleteConfirmMessage:
          "Are you sure you want to delete this folder?",
        deleteSuccess: "Folder deleted",
        folderName: "Folder name",
      },
      objects: {
        filterBy: "Filter by name or tag",
        deleteConfirm: "Delete files",
        deleteObjects: "Delete file(s)",
        deleteSuccess: "Files deleted",
        deleteObjectsMessage:
          "Are you sure you want to delete the file(s)?",
      },
      replicate: {
        destinationExists: "Folder already exists",
        copy_folder: "Copy folder: ",
        name_newFolder: "Name new folder",
      },
      tokens: {
        empty: "No API tokens created for the project",
        identifier: "Identifier",
        revoke: "Revoke",
        identLabel: "New token identifier",
        identMessage: "Insert new token identifier here",
        createToken: "Create token",
        latestToken: "Latest token: ",
        copyToken:
          "The token will be displayed just this once after its " +
          "creation, and recovering it will not be possible " +
          "afterwards. Please make sure that you have stored " +
          "the token somewhere before navigating away from the " +
          "token page.",
        tokenCopied: "Token copied.",
        back: "Back to all folders",
      },
      encrypt: {
        uploadFiles: "Upload files",
        upload_step1: "Create a new folder or use existing ones.",
        upload_step2: "Files to be uploaded",
        ephemeral: "Use your own private key for encryption",
        multipleReceivers: "Add other recipient's public keys",
        pk: "Private key",
        pk_msg: "Sender's private key",
        phrase: "Private key passphrase",
        phrase_msg: "Private key passphrase",
        pubkey: "Recipient's public keys",
        pubkey_msg: "Paste the public key of a recipient",
        pubkeyLabel: "Public keys of recipients",
        noRecipients: "No public keys added",
        addkey: "Add the recipient's public key (sha256)",
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
        advancedOptions: "Advanced encryption options",
        enReady:
          "Encryption engine is ready. Refresh the " +
          "window to enable encryption.",
        refresh: "Refresh",
      },
      search: {
        container: "Folder",
        object: "Object",
        folder: "Folder",
        tags: "Tags",
        objects: "Objects",
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
        item1: "User manual",
        itemLink1: "#",
        item2: "Billing",
        itemLink2: "#",
        item3: "Sharing API tokens",
        item4: "About",
        itemLink4: "#",
      },
      footerMenu: {
        title: "Swift browser",
        serviceProvider: "Service provider",
        serviceProviderLink: "#",
        menuItem1: "Item 1",
        menuItemLink1: "#",
        menuItem2:"Item 2",
        menuItemLink2:"#",
      },
    },
    label: {
      logo: "link to main page",
      language_menu: "select language",
      support_menu: "user support",
      project_info: "more project information",
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
        frontPage: "Etusivulle",
        BadRequest: "400 – Virheellinen pyyntö",
        BadRequest_text:
          "Virhe sivupyynnössä. Tämä voi johtua esimerkiksi " +
          "puuttuvasta salasanasta ja/tai käyttäjänimestä ",
        UIdown: "503 - Palvelu ei ole käytettävissä",
        UIdown_text: "Allas-käyttöliittymä on tilapäisesti poissa käytöstä",
        Unauthorized: "401 – Kirjaudu sisään",
        Unauthorized_text:
          "Sivun näyttäminen vaatii sisäänkirjauksen, " +
          "siirry kirjautumissivulle oheisesta painikkeesta.",
        Notfound: "404 – Etsittyä sivua ei löydetty.",
        Notfound_text: "Siirry kirjautumissivulle oheisesta painikkeesta.",
        Forbidden: "403 – Tuo on kiellettyä.",
        Forbidden_text:
          "Edellinen operaatio ei ole sallittu.",
        inUse: "Kansion nimi on jo käytössä.",
        invalidName: "Kansion nimi ei kelpaa.",
        createFail: "Kansion luonti epäonnistui.",
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
        notShared: "Tätä kansiota ei ole jaettu millekään projektille.",
        sharing_to_one_project: "Tämä kansio on jaettu yhdelle projektille.",
        sharing_to_many_projects: "Tämä kansio on jaettu useille projekteille.",
        shared_with_read:
          "Tämä kansio on jaettu kanssasi. Voit tarkastella ja ladata" +
          " tiedostoja tässä kansiossa (Read access).",
        shared_with_read_write:
          "Tämä kansio on jaettu kanssasi. Voit tarkastella, ladata," +
          " ladata ja muokata tunnisteita tässä kansiossa" +
          " (Read and write access).",
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
        folderDetails: "Ei yksityiskohtia kansioille",
        clearChecked: "Poista valinnat",
        tags: "Tunnisteet",
        editTags: "Muokkaa tunnisteita",
        deleteSelected: "Poista valitut kohteet",
        clearSelected: "Tyhjennä valinnat",
        itemSelected: "kohde valittu",
        itemsSelected: "kohdetta valittu",
        items: "Kohteet",
        itemsPerPage: "Kohteita sivulla: ",
        nextPage: "Seuraava sivu",
        prevPage: "Edellinen sivu",
        page: "Sivu",
        shared_status: "Jaettu tila",
        sharing: "Olet jakanut",
        shared: "Jaettu kanssasi",
        edit_sharing: " Muokkaa jakamista",
        source_project_id: "Jaa tämän kansion tunnus",
        date_of_sharing: "Jakamispäivämäärä",
        back_to_all_folders: "Takaisin kaikki kansiot",
        back_to_sharing_folders: "Takaisin jakamasi kansiot",
        back_to_shared_folders: "Takaisin sinulle jaetut kansiot",
      },
      tableOptions: {
        displayOptions: "Asetukset",
        render: "Luo kansiot",
        text: "Näytä tekstinä",
        hideTags: "Piilota tunnisteet",
        showTags: "Näytä tunnisteet",
        hidePagination: "Piilota sivutus",
        showPagination: "Näytä sivutus",
      },
      dashboard: {
        projectInfo: "Projektin tiedot",
        projectInfoBaseLink: "#",
      },
      share: {
        share: "Jaa",
        share_id: "Jaa tunnus",
        share_id_tooltip:
          "Tällä toiminnolla voit kopioida Jaa tunnuksen: uniikin " +
          "32-numeroisen koodin, joka on yhdistetty projektiisi. " +
          "Lähetä tunnus (esim. sähköpostilla) muiden projektien " +
          "jäsenille, niin he voivat jakaa kansioita sinulle.",
        close: "Sulje",
        instructions: "Kuinka jaan kansion",
        close_instructions: "Sulje ohjeet",
        share_cont: "Jaa säiliö",
        share_title: "Jaa kansio ",
        share_subtitle:
          "Tämä kansio on kaikkien jäsenten käytettävissä projektissa ",
        share_other_projects: "Jaa toisen projektin kanssa",
        share_guide_intro:
          "Kun haluat jakaa kansion toisen projektin kanssa: ",
        share_guide_step1:
          "1. Syötä Jaa tunnus koodi. Sinun tulee tietää " +
          "vastaanottavan projektin Jaa tunnus (32-numeroinen " +
          "koodi). Vastaanottaja voi " +
          "kopioida Jaa tunnuksen käyttöliittymästä Kopio Jaa tunnus-napilla " +
          "ja lähettää sen sinulle esim. sähköpostilla. " +
          "Voit jakaa kansion useiden projektien kanssa.",
        share_guide_step2:
          "2. Valitse käyttöoikeudet: ",
        share_guide_step2_list: [
          "Katsele: projektin jäsenet voivat katsella kansion sisältöä, " +
          "mutta eivät voi ladata ja kopioida " +
          "kansion sisältöä.",
          "Kopioi ja lataa: projektin jäsenet voivat kopioida ja ladata " +
          "kansion sisällön sekä purkaa kansion sisällön salauksen.",
          "Kopioi, lataa ja lähetä: projektin jäsenet voivat kopioida ja " +
          "ladata kansion sisällön sekä purkaa kansion sisällön salauksen. " +
          "He voivat myös lähettää tiedostoja jaettuun kansioon."],
        permissions: "Käyttöoikeudet",
        view_perm: "Katsele",
        read_perm: "Kopioi ja lataa",
        write_perm: "Kopioida, lataa ja lähetä",
        shared_successfully: "Kansion jakaminen onnistui!",
        remove_permission: "Lupa poistettiin onnistuneesti!",
        update_permission: "Lupa muutettiin onnistuneesti.",
        shared_table_title: "Tämä kansio on jaettu",
        field_placeholder: "Lisää projektitunnukset",
        cancel: "Peru",
        confirm: "Jaa",
        fail_noperm: "Valitse jaettavat oikeudet!",
        fail_noid:
          "Anna vähintään yhden projektin tunniste (Project " + "Identifier)!",
        fail_duplicate: "Säiliö on jo jaettu projektille!",
      },
      download: " Lataa",
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
      containers: "Säiliöt - ",
      upload: {
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
        complete: "Lähetys on valmis",
        cancelled: "Lataus peruutettu",
      },
      copy: " Kopioi",
      copied: "Jaa tunnus kopioitu leikepöydälle!",
      copy_failed: "Kopiointi epäonnistui!",
      delete: "Poista",
      remove: "Poista",
      editTags: "Muokkaa tägejä",
      cancel: "Peruuta",
      save: "Tallenna",
      options: "Valinnat",
      copysuccess: "Kansiota kopioidaan",
      copytime: "Se voi kestää muutaman sekunnin",
      copyfail: "Säiliön kopiointi epäonnistui",
      tagName: "Tägit",
      tagPlaceholder: "# Lisää tunniste ja paina rivinvaihtoa",
      container_ops: {
        addContainer: "Luo uusi säiliö",
        norename:
          "Säiliötä ei voi nimetä uudelleen, " +
          "mutta sen voi kopioida uudella nimellä.",
        createdFolder: "Luotu kansio jaetaan kaikille jäsenille projektissa ",
        viewProjectMembers: "Näytä projektin jäsenet",
        deleteConfirm: "Poista säiliö",
        deleteNote: "Säilön poistaminen edellyttää kaikkien " +
          "objektien poistamista ensin.",
        deleteConfirmMessage: "Haluatko varmasti poistaa tämän säiliön?",
        deleteSuccess: "Säiliö poistettu",
        folderName: "Kansion nimi",
      },
      objects: {
        filterBy: "Suodata nimellä tai tägillä",
        deleteConfirm: "Poista objektit",
        deleteObjects: "Poista objekti / objektit",
        deleteSuccess: "Objektit poistettu",
        deleteObjectsMessage: "Halutako varmasti poistaa nämä objektit?",
      },
      replicate: {
        destinationExists: "Kansio on jo olemassa",
        copy_folder: "Kopioi kansio: ",
        name_newFolder: "Nimeä uusi kansio",
      },
      tokens: {
        empty: "Projektille ei ole luotu API-avaimia",
        identifier: "Tunniste",
        revoke: "Mitätöi",
        identLabel: "Uuden avaimen tunniste",
        identMessage: "Syötä tunniste uudelle API-avaimelle",
        createToken: "Luo avain",
        latestToken: "Viimeisin avain: ",
        back: "Palaa päänäkymään",
        copyToken:
          "Avain näytetään vain kerran luonnin jälkeen, eikä sen " +
          "kopiointi tai palautus jälkeenpäin ole mahdollista. " +
          "Varmistathan ottaneesi avaimen talteen ennen " +
          "navigointia pois sivulta.",
        tokenCopied: "Avain kopioitu.",
      },
      encrypt: {
        uploadFiles: "Lataa tiedostoja",
        upload_step1: "Luo uusi kansio tai käytä olemassa olevia.",
        upload_step2: "Ladattavat tiedostot",
        ephemeral: "Käytä omaa yksityistä avainta",
        multipleReceivers: "Lisää muita vastaanottajien julkisia avaimia",
        pk: "Yksityinen avain",
        pk_msg: "Lähettäjän yksityinen avain",
        phrase: "Yksityisen avaimen salasana",
        phrase_msg: "Yksityisen avaimen salasana",
        addkey: "Lisää vastaanottajan julkinen avain",
        pubkey: "Vastaanottajien julkiset avaimet",
        pubkeyLabel: "Julkinen avain (sha256)",
        pubkey_msg: "Liitä vastaanottajan julkinen avain",
        noRecipients: "Ei lisättyjä vastaanottajien julkisia avaimia",
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
        advancedOptions: "Edistyneitä salausvaihtoehtoja",
        enReady:
          "Encryption engine is ready. Refresh the " +
          "window to enable encryption.",
        refresh: "Refresh", //to translate
      },
      search: {
        container: "Säiliö",
        object: "Objekti",
        folder: "Kansio",
        tags: "Tägit",
        objects: "Objektia",
        size: "Koko",
        empty: "Tuloksia ei löytynyt",
        searchBy: "Etsi nimellä tai tägillä",
        buildingIndex:
          "Tässä projektissa on suuri määrä kohteita. Odota, " +
          "kunnes hakuindeksi on valmis, ja yritä uudelleen.",
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
        item1: "Käyttöohje",
        itemLink1: "#",
        item2: "Hinnoittelu",
        itemLink2: "#",
        item3: "API avainten jakaminen",
        item4: "Tietoa",
        itemLink4: "#",
      },
      footerMenu: {
        title: "Swift browser",
        serviceProvider: "Palveluntarjoaja",
        serviceProviderLink: "#",
        menuItem1: "Menu 1",
        menuItemLink1: "#",
        menuItem2: "Menu 2",
        menuItemLink2: "#",
      },
    },
    label: {
      logo: "linkki etusivulle",
      language_menu: "kieli",
      support_menu: "käyttäjätuki",
      project_info: "lisätietoja projektista",
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