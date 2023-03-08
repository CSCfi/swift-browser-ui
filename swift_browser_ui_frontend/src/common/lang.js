// Ready translated locale messages

import lang_overrides from "@/assets/lang_overrides";

let default_translations = {
  en: {
    message: {
      indexOIDC: {
        logIn: "Login",
        href: "/login/oidc",
      },
      index: {
        formName: "Openstack Account",
        logIn: "Log In",
        loginmethods: [
          {
            msg: "Log In with SSO",
            href: "/login/oidc_front",
          },
        ],
      },
      error: {
        frontPage: "To the Front Page",
        BadRequest: "400 - Bad Request",
        BadRequest_text:
          "Something was wrong with the request. This can " +
          "be for example due to missing password and/or " +
          "username.",
        UIdown: "503 - Service Unavailable",
        UIdown_text: "Allas User Interface is currently Unavailable",
        Unauthorized: "401 – Not logged in",
        Unauthorized_text:
          "The action requested requires logging " +
          "in, or the log in credentials were incorrect. " +
          "Use the button below to Log in.",
        Notfound: "404 – Could not find the page that was requested.",
        Notfound_text:
          "The front page, however, can be found – in the link " + "below.",
        Forbidden: "403 – Wait, that is forbidden!",
        Forbidden_text:
          "The previous request could not be fulfilled. " +
          "If said operation should be allowed to be " +
          "performed, contact the service administrator. " +
          "Otherwise head back to the front page from the " +
          "button below.",
        inUse: "Bucket name already in use.",
        invalidName: "Bucket name is invalid.",
        createFail: "Bucket creation failed.",
        idb: "Firefox in private mode is not supported.",
        idb_text:
          "Firefox is not supported in private mode. " +
          "To continue, please turn off Firefox's private browsing or " +
          "switch to another browser.",
      },
      dropFiles: "Drag and drop folders here or ",
      help: "Help",
      helplink: "https://docs.csc.fi/data/sensitive-data/sd_connect/",
      support: "Support",
      program_name: "SD Connect",
      program_description:
        "Web UI for browsing contents in Swift object " + "storage systems.",
      program_description_step_2: "",
      currentProj: "Current project",
      selectProj: "Select project",
      createFolder: "Create folder",
      uploadSecondaryNav: "Upload",
      logOut: "Log Out",
      cscOrg: "CSC - IT Center For Science LTD",
      devel: "Developed by",
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
          "This folder is shared with you. You can view files only by" +
          " using SD Desktop and download files in this folder (Read access)",
        shared_with_read_write:
          "This folder is shared with you. You can view, download, upload" +
          " and edit tags in this folder (Read and write access).",
      },
      table: {
        name: "Name",
        objects: "Objects",
        size: "Size",
        modified: "Last Modified",
        paginated: "Paginated",
        pageNb: "per page",
        fileHash: "Hash",
        fileType: "Type",
        fileDown: "File Download",
        owner: "Owner Project Identifier",
        created: "Created",
        folderDetails: "No details for folders",
        clearChecked: "Clear checked",
        tags: "Tags",
        editTags: "Edit tags",
        deleteSelected: "Delete selected items",
        clearSelected: "Clear selections",
        itemSelected: "item selected",
        itemsSelected: "items selected",
        items: "Items",
        itemsPerPage: "Items per page: ",
        nextPage: "Next page",
        prevPage: "Previous Page",
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
        render: "Render folders",
        text: "Display as text",
        hideTags: "Hide tags",
        showTags: "Display tags",
        hidePagination: "Hide pagination",
        showPagination: "Display pagination",
      },
      discover: {
        sync_shares: "Synchronize shared buckets",
        sync_success_template: "Successfully synchronized ",
        sync_success_concat: " shared buckets",
        sync_failure_template: "No new shared buckets to synchronize.",
      },
      dashboard: {
        prj_usage: "Project usage",
        account: "Project Identifier",
        containers: "Buckets",
        objects: "Objects",
        usage: "Usage",
        cur_billing: "Currently consumes",
        prj_str_usag: "Project storage usage",
        equals: "Equals",
        more_info: "More information",
        dashboard: "User information",
        browser: "Browser",
        project_info: "Project information",
        tooltip_disable: "Hide tooltip",
        hour: "hour",
        default_notify:
          "The information on consumed billing units and the " +
          "available quota is derived from the default Pouta " +
          "values. If there's a separate pricing contract " +
          "with CSC for the project used, the values " +
          "specific the project may vary.",
        resources: "Resources",
        tokens: "Sharing API tokens",
        links: [
          {
            msg: "Pouta billing information",
            href: "https://docs.csc.fi/cloud/pouta/accounting/",
          },
          {
            msg: "Pouta default quotas",
            href: "https://docs.csc.fi/data/Allas/introduction/#billing-and-quotas",
          },
          {
            msg: "Information on project billing unit availability etc.",
            href: "https://my.csc.fi",
          },
        ],
      },
      share: {
        share: "Share",
        share_id: "Share ID",
        share_id_tooltip:
          "<strong>When another project wants to share a folder " +
          "with your project</strong><br/>Select this button and " +
          "send the Share ID (now copied in your cache) " +
          "to the project's member.<br/><br/> " +
          "<strong>When you want to share a folder with " +
          "another project</strong><br/>Ask the Share ID from " +
          "another project's member.",
        close: "Close",
        instructions: "Share ID instructions",
        close_instructions: "Close instructions",
        share_cont: "Share the bucket",
        share_title: "Share folder",
        share_subtitle:
          "This folder is already accessible to all the members" +
          " of this project.",
        share_other_projects: "Share with other projects",
        share_guide_step1:
          "1. Ask recipient project’s member to select " +
          "Copy Share ID button next to Select project dropdown when " +
          "correct project is selected.",
        share_guide_step2:
          "2. Recipient’s Share ID is copied in the cache memory " +
          "and recipient project’s member can paste it to email etc. " +
          "and send it to you.",
        permissions: "Permissions",
        read_perm: "Read",
        write_perm: "Read and write",
        shared_successfully: "Folder was shared successfully!",
        remove_permission: "Permission was removed successfully!",
        update_permission: "Permission was changed successfully.",
        shared_table_title: "Project's folder has been shared with",
        field_label: "Project Identifiers to share with",
        field_placeholder: "Add Share IDs",
        cancel: "Cancel",
        confirm: "Share",
        to_me: "Shared to the project",
        from_me: "Shared from the project",
        request_sharing: "Request sharing",
        shared: "Shared",
        sharedTo: "Shared to",
        container: "Bucket",
        owner: "Owner project identifier",
        shared_details_to: "Shared to: ",
        shared_details_address: "Bucket address: ",
        shared_details_rights: "Rights given: ",
        shared_details_read: "Read access",
        shared_details_write: "Write access",
        created: "Created",
        fail_noperm: "Please select permissions to grant!",
        fail_noid: "Please give at least one Project Identifier!",
        fail_nocont: "Please specify the bucket!",
        fail_duplicate: "The project already has access to the bucket!",
        new_share_button: "Share a bucket",
        container_label: "Bucket",
        revoke: "Revoke bucket access",
        revoke_project: "Revoke access from project",
        success_delete: "Successfully deleted sharing action",
        request_sync_nocont:
          "Cannot synchronize access requests without a " + "bucket",
        request_synced: "Successfully synchronized access requests",
        request_not_synced: "No access requests to sync",
        sync_requests: "Synchronize bucket share requests",
      },
      request: {
        project: "Project",
        container: "Bucket / Identifier",
        container_message: "The requested bucket name",
        owner: "Owner Project Identifier",
        owner_message: "Project Identifier of the bucket owner",
        request: "Request",
        multi_project:
          "Your account has access to multiple projects. " +
          "Please verify that the correct project is set " +
          "active in the menu, and submit the request with " +
          "the Request button.",
        requestHeading: "Request access to a bucket",
      },
      largeFileMessage: "",
      download: " Download",
      downloadLink: "Download Link",
      downloadContainer: " Download Bucket",
      downloadAlt: "Download link for",
      downloadAltLarge: "Confirm download large file",
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
      emptyShared: "No buckets have been shared to the project.",
      emptyRequested:
        "No shared buckets have been requested for the " + "project.",
      sharing: "Sharing - ",
      containers: "Buckets - ",
      upload: {
        upload: " Upload",
        uploadfolder: " Upload Folder",
        chunking: "Chunking",
        uploading: "Uploading ",
        cancelupload: " Cancel uploading",
        addfiles: "File / Files scheduled for uploading",
        upfinish: "Finished uploading ",
        upfail: "Failed uploading ",
        upnotsupported: "Uploading is not supported on your browser",
        isStarting: "Data upload will start shortly",
        hasStarted: "Upload has started",
        inProgress: "Upload in progress",
        longProgress: "Upload in progress, uploading ",
        viewDestinationFolder: "View destination folder",
        maximize: "Maximize",
        minimize: "Minimize",
        estimate: "It may take few minutes.",
        complete: "Uploading completed",
        cancelled: "Upload cancelled",
      },
      copy: " Copy",
      copied: "Share ID copied to clipboard!",
      copy_failed: "Copy failed!",
      create: "Create",
      delete: "Delete",
      remove: "Remove",
      edit: "Edit",
      editTags: "Edit tags",
      cancel: "Cancel",
      save: "Save",
      options: "Options",
      createContainerButton: "Create folder",
      copysuccess: "The folder is being copied",
      copytime: "It may take few seconds",
      copyfail: "Failed to copy the bucket",
      renderFolders: "Render as Folders",
      tagName: "Tags (optional)",
      tagPlaceholder: "# Add a tag and press enter",
      container_ops: {
        addContainer: "Create new folder",
        editContainer: "Editing bucket: ",
        norename:
          "Please note that folder names cannot be modified " +
          "after creating a folder.",
        createdFolder:
          "Created folder will be shared with all project members in ",
        viewProjectMembers: "View project members",
        deleteConfirm: "Delete Bucket",
        deleteNote:
          "Deleting a container requires " + "deleting all objects first.",
        deleteConfirmMessage:
          "Are you sure you want to delete this " + "bucket?",
        deleteSuccess: "Bucket Deleted",
        folderName: "Folder name",
        containerMessage: "The name of the new bucket",
        fullDelete:
          "Deleting a bucket with contents requires deleting " +
          "all objects inside it first.",
      },
      objects: {
        objectName: "Object",
        editObject: "Editing object: ",
        filterBy: "Filter by Name or Tag",
        norename:
          "Please note that folder names cannot be modified" +
          "after creating a folder.",
        deleteConfirm: "Delete Objects",
        deleteObjects: "Delete Object / Objects",
        deleteSuccess: "Objects deleted",
        deleteObjectsMessage:
          "Are you sure you want to delete these " + "objects?",
      },
      replicate: {
        destinationLabel: "Destination bucket",
        destinationMessage: "Insert copy destination bucket here",
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
        back: "Back to main view",
      },
      encrypt: {
        uploadFiles: "Upload files",
        upload_step1: "Create a new folder or use existing ones.",
        upload_step2: "Files to be uploaded",
        enTooLarge:
          "The total size of files amounts to more than 1024 " +
          "megabytes, which can lead to a failure in encryption. " +
          "Try uploading files in smaller batches, or encrypt " +
          "them before uploading normally.",
        enNotAvail:
          "ServiceWorker function not available in this browser. " +
          "Recommended browsers are Firefox and Chrome.",
        enFiles: "Encrypt files before upload",
        fsWriteFail:
          "Failed to copy files into temporary file system. " +
          "Try refreshing and uploading in smaller batches.",
        enFail:
          "Failed to encrypt files. This might be due to incorrectly " +
          "loaded encryption engine, or unavailable memory. Try " +
          "refreshing the page.",
        files: "Files",
        ephemeral: "Use own private key",
        multipleReceivers: "Add other receivers' public keys",
        pk: "Private key",
        pk_msg: "Sender private key",
        phrase: "Private key passphrase",
        phrase_msg: "Private key passphrase",
        pubkey: "Receiver public keys",
        pubkey_msg: "Paste a receiver public key",
        pubkeyLabel: "Public key (sha256)",
        noRecipients: "No additional receivers public keys",
        addkey: "Add receiver public key",
        addFiles: "Add files",
        container: "Destination bucket",
        container_msg: "Upload destination bucket",
        container_hint: "Use this field to change the name of the bucket",
        dropMsg: "Select files",
        enup: "Encrypt and Upload",
        normup: "Upload",
        upStart: "Started uploading.",
        enStart: "Encrypting files. This might take a few minutes.",
        enSuccess: "Encryption successful.",
        empty: "No files selected",
        defaultKeysMessage: "Default public keys added.",
        clearDrop: "Clear Files",
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
        container: "Bucket",
        object: "Object",
        folder: "Folder",
        tags: "Tags",
        objects: "Objects",
        size: "Size",
        empty: "No results found",
        searchBy: "Search by Name or Tag",
        buildingIndex:
          "This project has a large number of objects. Please, " +
          "wait while the search index is ready, and try again.",
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
        description: "Login with your user credentials.",
        uname: "Username",
        pwd: "Password",
      },
      supportMenu: {
        manual: "User manual",
        billing: "Billing unit calculator",
        sharing: "Sharing API tokens",
        about: "About Sensitive Data Services",
      },
      footerMenu: {
        title: "SD Connect",
        serviceProvider: "CSC - IT Center for Science Ltd.",
        serviceProviderLink: "https://csc.fi",
        menuItem1: "Item 1",
        menuItemLink1: "#",
        menuItem2: "Item 2",
        menuItemLink2: "#",
      },
    },
    label: {
      csclogo: "link to main page",
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
      edit_tag: "modify current tags",
      delete_tag: "delete tag",
      footer: "copyright information",
    },
  },
  fi: {
    message: {
      index: {
        formName: "Openstack Käyttäjä",
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
        BadRequest: "400 - Virheellinen pyyntö",
        BadRequest_text:
          "Virhe sivupyynnössä. Tämä voi johtua esimerkiksi " +
          "puuttuvasta salasanasta ja/tai käyttäjänimestä ",
        UIdown: "503 - Palvelu ei ole käytettävissä",
        UIdown_text: "Allas-käyttöliittymä on tilapäisesti poissa käytöstä",
        Unauthorized: "401 – Kirjaudu sisään",
        Unauthorized_text:
          "Sivun näyttäminen vaatii sisäänkirjauksen, " +
          "jonka voi toteuttaa oheisesta painikkeesta.",
        Notfound: "404 – Etsittyä sivua ei löydetty.",
        Notfound_text: "Etusivun voi löytää alapuolisesta painikkeesta.",
        Forbidden: "403 – Tuo on kiellettyä.",
        Forbidden_text:
          "Edellinen operaatio ei ole sallittu. Mikäli " +
          "kyseisen operaation tulisi olla sallittu, ota " +
          "yhteys palvelun ylläpitoon. Muussa tapauksessa " +
          "paluu etusivulle on mahdollista oheisesta " +
          "painikkeesta",
        inUse: "Säiliön nimi on jo käytössä.",
        invalidName: "Säiliön nimi ei kelpaa.",
        createFail: "Säiliön luonti epäonnistui.",
        idb: "Firefoxin yksityinen selaus ei ole tuettu.",
        idb_text:
          "Firefoxin yksityinen selaus ei ole tuettu." +
          "Voidaksesi kirjautua vaihda pois yksityisestä selaamisesta " +
          "tai käytä toista selainta.",
      },
      dropFiles: "Vedä ja pudota kansiot tähän tai ",
      help: "Apua",
      helplink: "https://docs.csc.fi/data/sensitive-data/sd_connect/",
      support: "Tuki",
      program_name: "SD Connect",
      program_description:
        "Web-käyttöliittymä tallennettujen tiedostojen " +
        "selaamiseen Swift-objektitietojärjestelmissä.",
      currentProj: "Nykyinen projekti",
      selectProj: "Valitse projekti",
      createFolder: "Luo kansio",
      uploadSecondaryNav: "Lähetä",
      logOut: "Kirjaudu ulos",
      cscOrg: "CSC – Tieteen Tietotekniikan Keskus Oy",
      devel: "kehittänyt",
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
        owner: "Omistavan projektin tunniste",
        created: "Luotu",
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
      discover: {
        sync_shares: "Synkronoi jaetut säiliöt",
        sync_success_template: "Synkronoitiin ",
        sync_success_concat: " jaettua säiliötä",
        sync_failure_template: "Ei uusia jaettuja säiliöitä synkronoitavaksi.",
      },
      dashboard: {
        prj_usage: "Projektin resurssienkäyttö",
        account: "Projektin tunniste",
        containers: "Kontteja",
        objects: "Objekteja",
        usage: "Tilankäyttö",
        cur_billing: "Nykyinen kulutus",
        prj_str_usag: "Projektin tilankäyttö",
        equals: "Tarkoittaen",
        more_info: "Lisätietoja",
        dashboard: "Käyttäjän tiedot",
        browser: "Selain",
        project_info: "Projektin tiedot",
        tooltip_disable: "Piilota ohje",
        hour: "tunti",
        default_notify:
          "Esitetty tieto laskutusysiköiden kulutuksesta ja " +
          "käyttörajoista on laskettu Poudan oletusarvojen " +
          "mukaan. Jos käytetylle projektille on erillinen " +
          "sopimus laskutuksesta CSC:n kanssa, tarkat arvot " +
          "voivat poiketa näytetyistä.",
        resources: "Resurssit",
        tokens: "Jaetun sisällön APIn avaimet",
        links: [
          {
            msg: "Tietoa Pouta-palvelun laskutuksesta (englanniksi)",
            href: "https://docs.csc.fi/cloud/pouta/accounting/",
          },
          {
            msg: "Tietoa Pouta-palvelun käyttörajoista (englanniksi)",
            href: "https://docs.csc.fi/data/Allas/introduction/#billing-and-quotas",
          },
          {
            msg:
              "Tietoa projektin laskutusyksiköiden määrästä jne." +
              " (englanniksi)",
            href: "https://my.csc.fi",
          },
        ],
      },
      share: {
        share: "Jaa",
        share_id: "Jaa tunnus",
        share_id_tooltip:
          "<strong>Mikäli toisesta projektista halutaan jakaa kansio " +
          "projektisi kanssa</strong><br/>Valitse tämä nappi ja lähetä " +
          "Jakotunnus toisen projektin jäsenelle.<br/><br/><strong>" +
          "Halutessasi jakaa kansion toisen projektin kanssa</strong>" +
          "<br/>Pyydä jakotunnusta joltakin kyseisen projektin jäseneltä.",
        close: "Kiinni",
        instructions: "Jaa tunnus ohjeet",
        close_instructions: "Sulje ohjeet",
        share_cont: "Jaa säiliö",
        share_title: "Jaa kansio ",
        share_subtitle:
          "Tämä kansio on jo kaikkien tämän projektin jäsenten käytettävissä.",
        share_other_projects: "Jaa toisen projektin kanssa",
        share_guide_step1:
          "1. Projektin jäsenet löytävät projektitunnuksen projektin " +
          "tietosivulta. Siirry Profiili valikkoon -> Projektin tiedot.",
        share_guide_step2:
          "2. Kopioi projektin tunnus ja lähetä se sähköpostitse jne.",
        permissions: "Käyttöoikeudet",
        read_perm: "Salli säiliön luku",
        write_perm: "Salli säiliöön kirjoitus",
        shared_successfully: "Kansion jakaminen onnistui!",
        remove_permission: "Lupa poistettiin onnistuneesti!",
        update_permission: "Lupa muutettiin onnistuneesti.",
        shared_table_title: "Projektin kansio on jaettu",
        project_id: "Projektin tunnus",
        field_label: "Jaa projektitunnisteille",
        field_placeholder: "Lisää projektitunnukset",
        cancel: "Peru",
        confirm: "Jaa",
        to_me: "Jaettu projektille",
        from_me: "Jaettu projektista",
        request_sharing: "Pyydä jakamista",
        shared: "Jaettu",
        sharedTo: "Jaettu",
        container: "Säiliö",
        owner: "Omistavan projektin tunniste",
        created: "Luotu",
        shared_details_to: "Jaettu projektille: ",
        shared_details_address: "Säiliön osoite: ",
        shared_details_rights: "Annetut oikeudet: ",
        shared_details_read: "Lukuoikeus",
        shared_details_write: "Kirjoitusoikeus",
        fail_noperm: "Valitse jaettavat oikeudet!",
        fail_noid:
          "Anna vähintään yhden projektin tunniste (Project " + "Identifier)!",
        fail_nocont: "Anna jaettava säiliö!",
        fail_duplicate: "Säiliö on jo jaettu projektille!",
        new_share_button: "Jaa säiliö",
        container_label: "Säiliö",
        revoke: "Poista jakaminen",
        revoke_project: "Poista jakaminen projektilta",
        success_delete: "Säiliön jaetun oikeuden poistaminen onnistui",
        request_sync_nocont: "Ei voida hakea jakopyyntöjä ilman säiliötä",
        request_synced: "Säiliön jakopyyntöjen haku onnistui",
        request_not_synced: "Ei säiliötä koskevia jakopyyntöjä",
        sync_requests: "Synkronoi säiliön jakopyynnöt",
      },
      request: {
        project: "Projekti",
        container: "Säiliö / tunniste",
        container_message: "Jaettavaksi pyydetyn säiliön nimi",
        owner: "Omistavan projektin tunniste",
        owner_message: "Halutun säiliön omistavan projektin tunniste",
        request: "Pyydä jakoa",
        multi_project:
          "Käyttäjällä on pääsy useisiin projekteihin. " +
          "Tarkistathan, että haluttu projekti on valittu " +
          "valikossa, ja lisää pyyntö Pyydä jakoa " +
          "-painikkeella.",
        requestHeading: "Pyydä oikeuksia säiliöön",
      },
      largeFileMessage: "",
      download: " Lataa",
      downloadContainer: " Lataa säiliö",
      downloadLink: "Latauslinkki",
      downloadAlt: "Latauslinkki tiedostolle",
      downloadAltLarge: "Hyväksy suuren tiedoston lataus",
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
      emptyShared: "Projektille ei ole jaettu säiliöitä.",
      emptyRequested: "Projektille ei ole pyydetty jakamaan säiliöitä.",
      sharing: "Jako - ",
      containers: "Säiliöt - ",
      upload: {
        upload: " Lähetä",
        uploadfolder: " Lähetä kansio",
        chunking: "Paloitellaan ",
        uploading: "Lähetetään ",
        cancelupload: " Peru lähetys",
        addfiles: "Lisättiin tiedosto / tiedostoja lähetettäväksi",
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
      create: "Luo",
      delete: "Poista",
      remove: "Poista",
      edit: "Muokkaa",
      editTags: "Muokkaa tägejä",
      cancel: "Peruuta",
      save: "Tallenna",
      options: "Valinnat",
      createContainerButton: "Luo säiliö",
      copysuccess: "Kansiota kopioidaan",
      copytime: "Se voi kestää muutaman sekunnin",
      copyfail: "Säiliön kopiointi epäonnistui",
      renderFolders: "Näytä kansioina",
      tagName: "Tägit",
      tagPlaceholder: "# Lisää tunniste ja paina rivinvaihtoa",
      container_ops: {
        addContainer: "Luo uusi säiliö",
        editContainer: "Muokataan säiliötä: ",
        norename:
          "Säiliötä ei voi nimetä uudelleen, " +
          "mutta sen voi kopioida uudella nimellä.",
        createdFolder: "Luotu kansio jaetaan kaikille jäsenille projektissa ",
        viewProjectMembers: "Näytä projektin jäsenet",
        deleteConfirm: "Poista säiliö",
        deleteNote:
          "Säilön poistaminen edellyttää kaikkien " +
          "objektien poistamista ensin.",
        deleteConfirmMessage: "Haluatko varmasti poistaa tämän säiliön?",
        deleteSuccess: "Säiliö poistettu",
        folderName: "Kansion nimi",
        containerMessage: "Uuden säiliön nimi",
        fullDelete: "Säiliön sisältö on poistettava ennen säiliön postamista.",
      },
      objects: {
        objectName: "Objekti",
        editObject: "Muokataan objekti: ",
        filterBy: "Suodata nimellä tai tägillä",
        norename:
          "Objektia ei voi nimetä uudelleen, " +
          "mutta sen voi kopioida uudella nimellä.",
        deleteConfirm: "Poista objektit",
        deleteObjects: "Poista objekti / objektit",
        deleteSuccess: "Objektit poistettu",
        deleteObjectsMessage: "Halutako varmasti poistaa nämä objektit?",
      },
      replicate: {
        destinationLabel: "Kohdesäiliö",
        destinationMessage: "Lisää kopioinnin kohdesäiliö tähän",
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
        enTooLarge:
          "Tiedostojen yhteenlaskettu koko on yli 1024 " +
          "megatavun rajan, mikä voi johtaa ongelmiin nykyisen " +
          "salausratkaisun rajoitteiden vuoksi. Lähetä tiedostot " +
          "pienemmissä erissä tai salaa ne ennen lähettämistä " +
          "tavallisesti.",
        enNotAvail:
          "Selaimestasi ei löydy ServiceWorker -ominaisuutta. " +
          "Suositellut selaimet ovat Chrome ja Firefox.",
        enFiles: "Salaa tiedostot ennen lähetystä",
        fsWriteFail:
          "Tiedostojen kopiointi väliaikaiseen tallennustilaan " +
          "ei onnistunut. Päivitä sivu ja koita uudelleen, tai " +
          "lähetä tiedostot pienemmissä erissä.",
        enFail:
          "Tiedostojen salaus epäonnistui. Mahdollisia syitä ovat " +
          "epäonnistunut salausohjelman lataus tai tilan loppuminen. " +
          "Päivitä sivu ja kokeile uudelleen.",
        files: "Tiedostot",
        ephemeral: "Käytä omaa yksityistä avainta",
        multipleReceivers: "Lisää muita vastaanottajien julkisia avaimia",
        pk: "Yksityinen avain",
        pk_msg: "Lähettäjän yksityinen avain",
        phrase: "Yksityisen avaimen salasana",
        phrase_msg: "Yksityisen avaimen salasana",
        addkey: "Lisää vastaanottajan julkinen avain",
        addFiles: "Lisää tiedostoja",
        pubkey: "Vastaanottajien julkiset avaimet",
        pubkeyLabel: "Julkinen avain (sha256)",
        pubkey_msg: "Liitä vastaanottajan julkinen avain",
        noRecipients: "Ei lisättyjä vastaanottajien julkisia avaimia",
        container: "Kohdesäiliö",
        container_msg: "Kohdesäiliö",
        container_hint: "Voit muuttaa säiliön nimeä tällä kentällä",
        dropMsg: "Valitse tiedostot",
        enup: "Salaa ja lähetä",
        normup: "Lähetä",
        upStart: "Aloitettiin tiedostojen lähetys.",
        enStart: "Salataan tiedostoja. Tämä voi kestää muutaman minuutin.",
        enSuccess: "Salaaminen onnistui.",
        empty: "Ei valittuja tiedostoja",
        defaultKeysMessage: "Oletusarvoiset julkiset avaimet lisätty.",
        clearDrop: "Tyhjennä tiedostot",
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
        refresh: "Refresh",
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
        manual: "Käyttöohje",
        billing: "Hinnoittelulaskuri",
        sharing: "API avainten jakaminen",
        about: "Tietoa",
      },
      footerMenu: {
        title: "SD Connect",
        serviceProvider: "CSC – Tieteen tietotekniikan keskus Oy",
        serviceProviderLink: "#",
        menuItem1: "Menu 1",
        menuItemLink1: "#",
        menuItem2: "Menu 2",
        menuItemLink2: "#",
      },
    },
    label: {
      csclogo: "linkki etusivulle",
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
