// Parameterized text override example file
let lang_overrides = {
  en: {
    message: {
      index: {
        placeholder: "",
        loginmethods: [
          {
            msg: "Log In using Haka",
            href: "/login",
          },
          {
            msg: "Log in with CSC Login",
            href: "/loginpassword",
          },
        ],
      },
      program_name: "SD Connect",
      program_description: "SD Connect provides a simple-to-use web user " +
        "interface, along with a command line interface, for storing " +
        "encrypted sensitive data for the duration of your research project " +
        "by allowing data uploads through drag-n-drop, and simple data " +
        "sharing.",
      helplink: "https://docs.csc.fi/data/sensitive-data/",
      dashboard: {
        default_notify: "The information on consumed billing units and " +
                        "available quota is derived from the default CSC " +
                        "values. Default quota can be increased, and the " +
                        "increase will not reflect here.",
        links: [
          {
            msg: "Sensitive Data Services User Guide",
            href: "https://docs.csc.fi/data/sensitive-data/",
          },
          {
            msg: "Billing Unit Calculator",
            href: "https://research.csc.fi/pricing#buc",
          },
          {
            msg: "About Sensitive Data Services for Research",
            href: "https://research.csc.fi/sensitive-data",
          },
        ],
      },
    },
  },
  fi: {
    message: {
      placeholder: "",
      index: {
        loginmethods: [
          {
            msg: "Kirjaudu Haka:lla",
            href: "/login",
          },
          {
            msg: "Kirjaudu CSC käyttäjällä",
            href: "/loginpassword",
          },
        ],
      },
      program_name: "SD Connect",
      program_description: "SD Connect tarjoaa yksinkertaisen " +
        "web-käyttöliittymän ja komentorivikäyttöliittymän sensitiivisen " +
        "datan säilyttämiseen tutkimusprojektin ajaksi, mahdollistamalla " +
        "tiedostojen lähettämisen raahaamalla ja yksinkertaisen jakamisen.",
      helplink: "https://docs.csc.fi/data/sensitive-data/",
      dashboard: {
        default_notify: "Tieto laskutusyksiköiden kulutuksesta ja " +
                        "käyttörajasta on laskettu CSC:n Allas-palvelun " +
                        "oletusarvojen mukaan. Mahdollinen korotettu " +
                        "käyttöraja ei näy käyttöliittymässä.",
        links: [
          {
            msg: "Sensitive Data Services User Guide",
            href: "https://docs.csc.fi/data/sensitive-data/",
          },
          {
            msg: "Billing Unit Calculator",
            href: "https://research.csc.fi/pricing#buc",
          },
          {
            msg: "About Sensitive Data Services for Research",
            href: "https://research.csc.fi/sensitive-data",
          },
        ],
      },
    },
  },
};

export default lang_overrides;
