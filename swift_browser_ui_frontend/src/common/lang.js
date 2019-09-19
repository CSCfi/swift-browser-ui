// Ready translated locale messages

const translations = {
  en: {
    message: {
      index: {
        logIn: "Log In",
      },
      error: {
        frontPage: "To the Front Page",
        Unauthorized: "401 – Not logged in",
        Unauthorized_text: "The action requested requires logging" +
                           "in. Use the button below to Log in.",
        Notfound: "404 – Could not find the page that was requested.",
        Notfound_text: "The front page, however, can be found – in the link " +
                       "below.",
        Forbidden: "403 – Wait, thats forbidden!",
        Forbidden_text: "The previous request could not be fulfilled. " +
                        "If said operation should be allowed to be " +
                        "performed, contact the service administrator. " +
                        "Otherwise head back to the front page from the " +
                        "button below.",
      },
      program_name: "Object Browser",
      currentProj: "Current project",
      logOut: "Log Out",
      cscOrg: "CSC - IT Center For Science LTD",
      devel: "developed by",
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
      },
      dashboard: {
        prj_usage: "Project usage",
        account: "Account",
        containers: "Containers",
        objects: "Objects",
        usage: "Usage",
        cur_billing: "Currently consumes",
        prj_str_usag: "Project storage usage",
        equals: "Equals",
        more_info: "More information",
        billing_info: "Pouta billing information",
        quota_info: "Pouta default quotas",
        avail_info: "Information on project billing unit availability etc.",
        dashboard: "User information",
        browser: "Browser",
        tooltip_disable: "Hide tooltip",
        hour: "hour",
        default_notify: "The information on consumed billing units and the " +
                        "available quota is derived from the default Pouta " +
                        "values. If there's a separate pricing contract " +
                        "with CSC for the project used, the values " +
                        "specific the project may vary.",
        pouta_accounting: "https://research.csc.fi/pouta-accounting",
        pouta_obj_store_quota_info: "https://research.csc.fi/pouta-object-storage-quotas-and-billing",
        my_csc: "https://my.csc.fi",
      },
      largeFileMessage: "",
      download: "Download",
      downloadLink: "Download Link",
      downloadAlt: "Download link for",
      downloadAltLarge: "Confirm download large file",
      largeDownMessage: "No large (> 1GiB) downloads enabled. Click to " +
                        "enable them for the duration of the session.",
      largeDownAction: "Enable",
      emptyContainer: "This container is empty.",
      emptyProject: "The project doesn't contain any containers.",
      searchBy: "Search by Name",
    },
  },
  fi: {
    message: {
      index: {
        logIn: "Kirjaudu sisään",
      },
      error: {
        frontPage: "Etusivulle",
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
      },
      program_name: "Object Browser",
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
      },
      dashboard: {
        prj_usage: "Projektin resurssienkäyttö",
        account: "Käyttäjä",
        containers: "Kontteja",
        objects: "Objekteja",
        usage: "Tilankäyttö",
        cur_billing: "Nykyinen kulutus",
        prj_str_usag: "Projektin tilankäyttö",
        equals: "Tarkoittaen",
        more_info: "Lisätietoja",
        billing_info: "Tietoa Pouta-palvelun laskutuksesta (englanniksi)",
        quota_info: "Tietoa Pouta-palvelun käyttörajoista (englanniksi)",
        avail_info: "Tietoa projektin laskutusyksiköiden määrästä jne. " +
                    "(englanniksi)",
        dashboard: "Käyttäjän tiedot",
        browser: "Selain",
        tooltip_disable: "Piilota ohje",
        hour: "tunti",
        default_notify: "Esitetty tieto laskutusysiköiden kulutuksesta ja " +
                        "käyttörajoista on laskettu Poudan oletusarvojen " +
                        "mukaan. Jos käytetylle projektille on erillinen " +
                        "sopimus laskutuksesta CSC:n kanssa, tarkat arvot " +
                        "voivat poiketa näytetyistä.",
        pouta_accounting: "https://research.csc.fi/pouta-accounting",
        pouta_obj_store_quota_info: "https://research.csc.fi/pouta-object-storage-quotas-and-billing",
        my_csc: "https://my.csc.fi",
      },
      largeFileMessage: "",
      download: "Lataa",
      downloadLink: "Latauslinkki",
      downloadAlt: "Latauslinkki tiedostolle",
      downloadAltLarge: "Hyväksy suuren tiedoston lataus",
      largeDownMessage: "Suurten tiedostojen (> 1Gt) lataus täytyy hyväksyä " +
                        "erikseen. Paina hyväksyäksesi suuret lataukset " +
                        "nykyisen kirjautumisen ajaksi.",
      largeDownAction: "Hyväksy",
      emptyContainer: "Säiliö on tyhjä.",
      emptyProject: "Projektilla ei ole säiliöitä.",
      searchBy: "Etsi nimellä",
    },
  },
};

export default translations;
