// Parameterized text override example file
let lang_overrides = {
  en: {
    message: {
      program_name: "SD Connect",
      program_description: "SD Connect provides a simple-to-use web user " +
        "interface, along with a command line interface, for storing " +
        "encrypted sensitive data for the duration of your research project " +
        "by allowing data uploads through drag-n-drop, and simple data " +
        "sharing.",
      dashboard: {
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
      program_name: "SD Connect",
      program_description: "SD Connect tarjoaa yksinkertaisen " +
        "web-käyttöliittymän ja komentorivikäyttöliittymän sensitiivisen " +
        "datan säilyttämiseen tutkimusprojektin ajaksi, mahdollistamalla " +
        "tiedostojen lähettämisen raahaamalla ja yksinkertaisen jakamisen.",
      dashboard: {
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
