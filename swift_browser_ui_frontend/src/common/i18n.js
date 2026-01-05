import { createI18n } from "vue-i18n";

import translations from "@/common/lang";

function getLangCookie() {
  let matches = document.cookie.match(
    new RegExp("(?:^|; )" + "OBJ_UI_LANG" + "=([^;]*)"),
  );
  return matches ? decodeURIComponent(matches[1]) : "en";
}

export const i18n = createI18n({
  locale: getLangCookie(),
  messages: translations,
  warnHtmlMessage: false,
});
