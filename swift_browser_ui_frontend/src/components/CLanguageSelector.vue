<template>
  <c-menu :items.prop="langItems">
    <span class="menu-active">{{ current }}</span>
  </c-menu>
</template>

<script>
export default {
  name: "LanguageSelector",
  data: function() {
    return {
      langs: [{ph: "In English", value: "en"}, {ph: "Suomeksi", value: "fi"}],
      langItems: [],
    };
  },
  computed: {
    current: function () {
      return this.langs.find(i =>  {return i.value == this.$i18n.locale;}).ph;
    },
  },
  created: function () {
    this.setLang();
  },
  methods: {
    setLang: function () {
      for (let lang of this.langs) {
        this.langItems.push({
          name: lang.ph,
          action: () => {
            this.$i18n.locale = lang.value;
            this.setCookieLang();
          },
        });
      }
      this.setCookieLang();
    },
    setCookieLang: function () {
      const expiryDate = new Date();
      expiryDate.setMonth(expiryDate.getMonth() + 1);
      document.cookie = "OBJ_UI_LANG=" +
        this.$i18n.locale +
        "; path=/; expires="
        + expiryDate.toUTCString();
    },
  },
};
</script>
