// Depends on vue.js and vue-router, needs ES6 support to work

// Create VueI18n instance with options

function getLangCookie() {
    let matches = document.cookie.match(new RegExp(
        "(?:^|; )" + 'OBJ_UI_LANG' + "=([^;]*)"
    ));
    return matches ? decodeURIComponent(matches[1]) : 'en';
};

const i18n = new VueI18n({
    locale: getLangCookie(), // set locale
    messages: langPlaceholders, // set locale messages
});

// The view for the application front page. Currently does nothing as it's not
// needed yet.
const FrontPage = Vue.extend({
    template: `
<div></div>
    `,
});

// Define the Vue routes, for now we're using simple routes, in which there is
// no direct queries, but the actual route endpoint is signified by location
// in the URL. This is because it's in my opinion simpler, since it makes it
// possible to e.g. use the URL directly as breadcrumbs.
const routes = [
    { path: '/browse', component: FrontPage },
    { path: '/browse/:user', component: UserPage },
    { path: '/browse/:user/:project', component: ContainerPage },
    { path: '/browse/:user/:project/:container', component: ObjectPage },
    { path: '/placeholder', component: undefined },
];

// Define the Vue router instance
// We're using history mode instead of hash-mode.
const router = new VueRouter({
    mode: "history",
    routes: routes,
});


// Define the page root Vue App, injecting the internalization and router
// modules
const app = new Vue({
    router: router,
    i18n,
    data: {
        oCache: {},
        bList: undefined,
        projects: [],
        active: "",
        uname: "",
        meta: undefined,
        multipleProjects: false,
        isLoading: false,
        isFullPage: true,
        langs: [{ph: 'In English', value: 'en'}, {ph: 'Suomeksi', value: 'fi'}],
    },
    methods: {
        getRouteAsList: function () {
            // Create a list representation of the current application route
            // to help in the initialization of the breadcrumb component
            let retl = [];
            if (this.$route.params.user != undefined) {
                retl.push({
                    alias: this.$route.params.user,
                    address: ("/browse/" + this.$route.params.user),
                });
            };
            if (this.$route.params.project != undefined) {
                retl.push({
                    alias: this.$route.params.project,
                    address: (
                        "/browse/" + this.$route.params.user +
                        "/" + this.$route.params.project
                    ),
                });
            };
            if (this.$route.params.container != undefined) {
                retl.push({
                    alias: this.$route.params.container,
                    address: (
                        "/browse/" + this.$route.params.user +
                        "/" + this.$route.params.project +
                        "/" + this.$route.params.container
                    ),
                });
            };
            return retl;
        },
        changeProject: function (newProject) {
            // Re-scope to project given by the user
            changeProjectApi(newProject).then(function (ret) {
                if (ret) {
                    getActiveProject().then(function (value) {
                        app.active = value;
                        app.bList = undefined;
                        app.oCache = {};

                        app.$router.push(
                            '/browse/' +
                            app.uname + '/' +
                            app.active['name']
                        );
                        app.$router.go(0);
                    })
                }
                else {
                    app.$router.push('/browse/' + app.uname);
                };
            })
        },
        setCookieLang: function() {
            const expiryDate = new Date();
            expiryDate.setMonth(expiryDate.getMonth() + 1);
            document.cookie = 'OBJ_UI_LANG=' +
                              i18n.locale +
                              '; path=/; expires=' +
                              expiryDate.toUTCString();
            this.$router.go(this.$router.currentRoute);
        },
        getProjectChangeURL ( newProject ) {
            let rescopeURL = new URL(
                "/login/rescope",
                document.location.origin
            );
            rescopeURL.searchParams.append( "project", newProject );
            return rescopeURL.toString();        
        },
    },
});

var shiftSizeDivision = function (vallist) {
    'use strict';
    // Javascript won't let us do anything but floating point division by
    // default, so a different approach was chosen anyway.
    //  ( right shift by ten is a faster alias to division by 1024,
    //  decimal file sizes are heresy and thus can't be enabled )
    switch (vallist[0] >>> 10) {
        case 0:
            return vallist;
        default:
            vallist[0] = vallist[0] >>> 10;
            vallist[1] = vallist[1] + 1;
            return shiftSizeDivision(vallist);
    }
};

var getHumanReadableSize = function (val) {
    // Get a human readable version of the size, which is returned from the
    // API as bytes, flooring to the most significant size without decimals.

    // As JS doesn't allow us to natively handle 64 bit integers, ditch all
    // unnecessary stuff from the value, we only need the significant part.
    let byteval = val > 4294967296 ? parseInt(val / 1073741824) : val;
    let count = val > 4294967296 ? 3 : 0;

    let human = shiftSizeDivision([byteval, count]);
    let ret = human[0].toString();
    switch (human[1]) {
        case 0:
            ret += " B";
            break;
        case 1:
            ret += " KiB";
            break;
        case 2:
            ret += " MiB";
            break;
        case 3:
            ret += " GiB";
            break;
        case 4:
            ret += " TiB";
            break;
    }
    return ret;
};


var getHumanReadableDate = function (val) {
    let dateVal = new Date(val);
    var options = {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour:'2-digit',
        minute: '2-digit',
        second: '2-digit'
    };
    var zone = { timeZone: 'EEST' }; /* For now default to this. */
    switch (i18n.locale) {
        case 'en':
            langLocale = 'en-GB';
            break;
        case 'fi':
            langLocale = 'fi-FI';
            break;
        default:
            langLocale = 'en-GB';

    }
    return dateVal.toLocaleDateString(langLocale, options, zone);
}


var recursivePruneCache = function (object_cache) {
    // Prune the object_cache until the cache is < 250000 objects in total
    if (getNestedObjectTotal(object_cache) > 250000) {
        delete bject_cache[Object.keys(object_cache)[0]];
        return recursivePruneCache(object_cache);
    }
    return object_cache;
}


var getNestedObjectTotal = function (nested) {
    // Get the size of a object containing arrays, in the amount of total
    // array elements
    let ret = 0;
    for (var key in nested) {
        ret += nested[key].length;
    }
    return ret;
}
