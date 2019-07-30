function getLangCookie() {
    let matches = document.cookie.match(new RegExp(
        "(?:^|; )" + 'lang' + "=([^;]*)"
    ));
    return matches ? decodeURIComponent(matches[1]) : 'en';
}

const i18n = new VueI18n({
    locale: getLangCookie(),
    messages: langPlaceholders,
})

const app = new Vue({
    i18n,
    data: {
        langs: [{ph: 'In English', value: 'en'}, {ph: 'Suomeksi', value: 'fi'}],
    },
    methods: {
        setCookieLang: function() {
            const expiryDate = new Date();
            expiryDate.setMonth(expiryDate.getMonth() + 1);
            document.cookie = 'lang=' + i18n.locale + '; path=/; expires=' + expiryDate.toUTCString();
        },
    }
});
