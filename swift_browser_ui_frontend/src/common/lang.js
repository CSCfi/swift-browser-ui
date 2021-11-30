// Ready translated locale messages

import lang_overrides from "@/assets/lang_overrides";

let default_translations = {
  en: {
    message: {
      index: {
        formName: "Openstack Account",
        logIn: "Log In",
        loginmethods: [
          {
            msg: "Log In with SSO",
            href: "/login",
          },
        ],
      },
      error: {
        frontPage: "To the Front Page",
        BadRequest: "400 - Bad Request",
        BadRequest_text: "Something was wrong with the request. This can " +
                         "be for example due to missing password and/or " +
                         "username.",
        UIdown: "503 - Service Unavailable",
        UIdown_text: "Allas User Interface is currently Unavailable",
        Unauthorized: "401 – Not logged in",
        Unauthorized_text: "The action requested requires logging " +
                           "in, or the log in credentials were incorrect. " +
                           "Use the button below to Log in.",
        Notfound: "404 – Could not find the page that was requested.",
        Notfound_text: "The front page, however, can be found – in the link " +
                       "below.",
        Forbidden: "403 – Wait, that is forbidden!",
        Forbidden_text: "The previous request could not be fulfilled. " +
                        "If said operation should be allowed to be " +
                        "performed, contact the service administrator. " +
                        "Otherwise head back to the front page from the " +
                        "button below.",
        inUse: "Bucket name already in use.",
        invalidName: "Bucket name is invalid.",
        createFail: "Bucket creation failed.",
      },
      help: "Help",
      helplink: "",
      program_name: "Object Browser",
      program_description: "Web UI for browsing contents in Swift object " +
                           "storage systems.",
      currentProj: "Current project",
      logOut: "Log Out",
      cscOrg: "CSC - IT Center For Science LTD",
      devel: "Developed by",
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
        showTags: "Display tags",
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
        tooltip_disable: "Hide tooltip",
        hour: "hour",
        default_notify: "The information on consumed billing units and the " +
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
        share_cont: "Share the bucket",
        read_perm: "Grant read permissions",
        write_perm: "Grant write permissions",
        field_label: "Project Identifiers to share with",
        field_placeholder: "Add Project Identifiers here",
        cancel: "Cancel",
        confirm: "Share",
        to_me: "Shared to the project",
        from_me: "Shared from the project",
        request_sharing: "Request sharing",
        shared: "Shared",
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
        request_sync_nocont: "Cannot synchronize access requests without a " +
                             "bucket",
        request_synced: "Successfully synchronized access requests",
        request_not_synced: "No access requests to sync",
        sync_requests: "Synchronize bucket share requests",
      },
      request: {
        project: "Project",
        container: "Bucket / Identfier",
        container_message: "The requested bucket name",
        owner: "Owner Project Identifier",
        owner_message: "Project Identifier of the bucket owner",
        request: "Request",
        multi_project: "Your account has access to multiple projects. " +
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
      largeDownMessage: "No large (> 1GiB) downloads enabled. Click to " +
                        "enable them for the duration of the session.",
      largeDownAction: "Enable",
      emptyContainer: "This bucket is empty.",
      emptyProject: "The project does not contain any buckets " +
                    "or their use is not permitted.",
      emptyShared: "No buckets have been shared to the project.",
      emptyRequested: "No shared buckets have been requested for the " +
                      "project.",
      searchBy: "Search by Name",
      sharing: "Sharing - ",
      containers: "Buckets - ",
      upload: " Upload",
      uploadfolder: " Upload Folder",
      chunking: "Chunking",
      uploading: "Uploading ",
      cancelupload: " Cancel uploading",
      addfiles: "File / Files scheduled for uploading",
      upfinish: "Finished uploading ",
      upfail: "Failed uploading ",
      upnotsupported: "Uploading is not supported on your browser",
      copy: " Copy",
      create: "Create",
      delete: "Delete",
      edit: "Edit",
      save: "Save",
      createContainerButton: "Create Bucket",
      copysuccess: "Started copying the bucket in the background",
      copyfail: "Failed to copy the bucket",
      renderFolders: "Render as Folders",
      container_ops: {
        addContainer: "Add a new bucket",
        editContainer: "Editing bucket: ",
        deleteConfirm: "Delete Bucket",
        deleteConfirmMessage: "Are you sure you want to delete this " +
                              "bucket?",
        deleteSuccess: "Bucket Deleted",
        containerName: "Bucket",
        containerMessage: "The name of the new bucket",
        fullDelete: "Deleting a bucket with contents requires deleting " +
                    "all objects inside it first.",
        tagName: "Tags",
        tagMessage: "Press enter to add.",
      },
      objects: {
        deleteConfirm: "Delete Objects",
        deleteObjects: "Delete Object / Objects",
        deleteSuccess: "Objects deleted",
        deleteObjectsMessage: "Are you sure you want to delete these " +
                              "objects?",
      },
      replicate: {
        destinationLabel: "Destination bucket",
        destinationMessage: "Insert copy destination bucket here",
        destinationExists: " Destination already exists",
      },
      tokens: {
        empty: "No API tokens created for the project",
        identifier: "Identifier",
        revoke: "Revoke",
        identLabel: "New token identifier",
        identMessage: "Insert new token identifier here",
        createToken: "Create token",
        latestToken: "Latest token: ",
        copyToken: "The token will be displayed just this once after its " +
                   "creation, and recovering it will not be possible " +
                   "afterwards. Please make sure that you have stored " +
                   "the token somewhere before navigating away from the " +
                   "token page.",
        tokenCopied: "Token copied.",
      },
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
            href: "/login",
          },
        ],
      },
      error: {
        frontPage: "Etusivulle",
        BadRequest: "400 - Virheellinen pyyntö",
        BadRequest_text: "Virhe sivupyynnössä. Tämä voi johtua esimerkiksi " +
                         "puuttuvasta salasanasta ja/tai käyttäjänimestä ",
        UIdown: "503 - Palvelu ei ole käytettävissä",
        UIdown_text: "Allas-käyttöliittymä on tilapäisesti poissa käytöstä",
        Unauthorized: "401 – Kirjaudu sisään",
        Unauthorized_text: "Sivun näyttäminen vaatii sisäänkirjauksen, " +
                           "jonka voi toteuttaa oheisesta painikkeesta.",
        Notfound: "404 – Etsittyä sivua ei löydetty.",
        Notfound_text: "Etusivun voi löytää alapuolisesta painikkeesta.",
        Forbidden: "403 – Tuo on kiellettyä.",
        Forbidden_text: "Edellinen operaatio ei ole sallittu. Mikäli " +
                        "kyseisen operaation tulisi olla sallittu, ota " +
                        "yhteys palvelun ylläpitoon. Muussa tapauksessa " +
                        "paluu etusivulle on mahdollista oheisesta " +
                        "painikkeesta",
        inUse: "Säiliön nimi on jo käytössä.",
        invalidName: "Säiliön nimi ei kelpaa.",
        createFail: "Säiliön luonti epäonnistui.",
      },
      help: "Apua",
      helplink: "",
      program_name: "Object Browser",
      program_description: "Web-käyttöliittymä tallennettujen tiedostojen " +
                           "selaamiseen Swift-objektitietojärjestelmissä.",
      currentProj: "Nykyinen projekti",
      logOut: "Kirjaudu ulos",
      cscOrg: "CSC – Tieteen Tietotekniikan Keskus Oy",
      devel: "kehittänyt",
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
        showTags: "Näytä Tägit",
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
        tooltip_disable: "Piilota ohje",
        hour: "tunti",
        default_notify: "Esitetty tieto laskutusysiköiden kulutuksesta ja " +
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
            msg: "Tietoa projektin laskutusyksiköiden määrästä jne." +
                 " (englanniksi)",
            href: "https://my.csc.fi",
          },
        ],
      },
      share: {
        share: "Jaa",
        share_cont: "Jaa säiliö",
        read_perm: "Salli säiliön luku",
        write_perm: "Salli säiliöön kirjoitus",
        field_label: "Jaa projektitunnisteille",
        field_placeholder: "Lisää projektitunnisteet",
        cancel: "Peru",
        confirm: "Jaa",
        to_me: "Jaettu projektille",
        from_me: "Jaettu projektista",
        request_sharing: "Pyydä jakamista",
        shared: "Jaettu",
        container: "Säiliö",
        owner: "Omistavan projektin tunniste",
        created: "Luotu",
        shared_details_to: "Jaettu projektille: ",
        shared_details_address: "Säiliön osoite: ",
        shared_details_rights: "Annetut oikeudet: ",
        shared_details_read: "Lukuoikeus",
        shared_details_write: "Kirjoitusoikeus",
        fail_noperm: "Valitse jaettavat oikeudet!",
        fail_noid: "Anna vähintään yhden projektin tunniste (Project " +
                   "Identifier)!",
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
        multi_project: "Käyttäjällä on pääsy useisiin projekteihin. " +
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
      largeDownMessage: "Suurten tiedostojen (> 1Gt) lataus täytyy hyväksyä " +
                        "erikseen. Paina hyväksyäksesi suuret lataukset " +
                        "nykyisen kirjautumisen ajaksi.",
      largeDownAction: "Hyväksy",
      emptyContainer: "Säiliö on tyhjä.",
      emptyProject: "Projektilla ei ole säiliöitä " +
                    "tai niiden käyttöä ei ole sallittu.",
      emptyShared: "Projektille ei ole jaettu säiliöitä.",
      emptyRequested: "Projektille ei ole pyydetty jakamaan säiliöitä.",
      searchBy: "Etsi nimellä",
      sharing: "Jako - ",
      containers: "Säiliöt - ",
      upload: " Lähetä",
      uploadfolder: " Lähetä kansio",
      chunking: "Paloitellaan ",
      uploading: "Lähetetään ",
      cancelupload: " Peru lähetys",
      addfiles: "Lisättiin tiedosto / tiedostoja lähetettäväksi",
      upfinish: "Lähetettiin tiedosto ",
      upfail: "Epäonnistuttiin lähettäessä tiedosto ",
      upnotsupported: "Selain ei tue tiedostojen lähettämistä",
      copy: " Kopioi",
      create: "Luo",
      delete: "Poista",
      edit: "Muokkaa",
      save: "Tallenna",
      createContainerButton: "Luo säiliö",
      copysuccess: "Aloitettiin säiliön kopiointi taustalla",
      copyfail: "Säiliön kopiointi epäonnistui",
      renderFolders: "Näytä kansioina",
      container_ops: {
        addContainer: "Luo uusi säiliö",
        editContainer: "Muokataan säiliötä: ",
        deleteConfirm: "Poista säiliö",
        deleteConfirmMessage: "Haluatko varmasti poistaa tämän säiliön?",
        deleteSuccess: "Säiliö poistettu",
        containerName: "Säiliö",
        containerMessage: "Uuden säiliön nimi",
        fullDelete: "Säiliön sisältö on poistettava ennen säiliön postamista.",
        tagName: "Tägit",
        tagMessage: "Paina 'enter' lisätäksesi.",
      },
      objects: {
        deleteConfirm: "Poista objektit",
        deleteObjects: "Poista objekti / objektit",
        deleteSuccess: "Objektit poistettu",
        deleteObjectsMessage: "Halutako varmasti poistaa nämä objektit?",
      },
      replicate: {
        destinationLabel: "Kohdesäiliö",
        destinationMessage: "Lisää kopioinnin kohdesäiliö tähän",
        destinationExists: " Kohdesäiliö on jo olemassa",
      },
      tokens: {
        empty: "Projektille ei ole luotu API-avaimia",
        identifier: "Tunniste",
        revoke: "Mitätöi",
        identLabel: "Uuden avaimen tunniste",
        identMessage: "Syötä tunniste uudelle API-avaimelle",
        createToken: "Luo avain",
        latestToken: "Viimeisin avain: ",
        copyToken: "Avain näytetään vain kerran luonnin jälkeen, eikä sen " +
                   "kopiointi tai palautus jälkeenpäin ole mahdollista. " +
                   "Varmistathan ottaneesi avaimen talteen ennen " +
                   "navigointia pois sivulta.",
        tokenCopied: "Avain kopioitu.",
      },
    },
  },
};

let translations = default_translations;

function nestedJoin (dst, src) {
  // Join two objects with nested content overriding with the latter
  let to_assign = [];
  for (let [key, value] of Object.entries(src)) {
    if (typeof(value) == "object") {
      if (key in dst) {
        to_assign.push([key, nestedJoin(dst[key], src[key])]);
      }
      else {
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
