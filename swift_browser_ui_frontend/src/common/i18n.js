import { createI18n } from "vue-i18n";

import getLangCookie from "@/common/conv";
import translations from "@/common/lang";

export const i18n = createI18n({
  locale: getLangCookie(),
  messages: translations,
  warnHtmlMessage: false,
});
