// Depends on vue.js and vue-router, needs ES6 support to work

// To improve readability some larger code blocks are separated by a dash-line.
// This is just to test whether or not this is something I want to start using

// NOTE: All the components used in the routing can be found from the
// btablecomp.js file.

// The view for the application front page. Currently does nothing as it's not
// needed yet.
const FrontPage = Vue.extend({
    template: '\
<div>\
<p>Not yet implemented</p>\
</div>\
    ',
});

// The view for the application user page, e.g. for showing user information in
// a bit more detail. Currently does nothing as it's not needed yet.
const UserPage = Vue.extend({
    template: '\
<div>\
<p>Not yet implemented</p>\
</div>\
    ',
});

// ---------------------------------------------------------------------------

// The view for the container list page, will show the user all the containers
// that are available for the project that's currently being accessed.
// Data needs to be pulled from the parent class with a function, because
// vue.js has it's own way of doing things with a strict hierarchy
const ContainerPage = Vue.extend({
    data: function () {
        let vars = {};
        vars['bList'] = [];
        if ( app.bList == undefined ) {
            getBuckets().then( function ( ret ) {
                vars['bList'] = ret;

                for ( let i = 0; i < vars['bList'].length; i++) {
                    vars['bList'][i]['size'] = getHumanReadableSize(
                        vars['bList'][i]['bytes']
                    );
                };

                app.bList = vars['bList']
            });
        } else {
            vars['bList'] = app.bList;
        };
        vars['bColumns'] = [
            {
                field: "name",
                label: "Name",
                sortable: true,
            },
            {
                field: "count",
                label: "Objects",
                sortable: true,
                width: 80,
            },
            {
                field: "size",
                label: "Size",
                width: 140,
            },
        ];
        vars['selected'] = vars['bList'][0];
        return vars;
    },
    template: `
<div>
    <b-table 
        style="width: 90%;margin: 5%;"
        :data="bList"
        :columns="bColumns"
        :selected.sync="selected"
        v-on:dblclick="(row) => $router.push( getContainerAddress ( row['name'] ) )"
        v-on:keyup.native.enter="$router.push( getContainerAddress ( selected['name'] ))"
        v-on:keyup.native.space="$router.push( getContainerAddress ( selected['name'] ))"
        focusable
        hoverable
        detailed
    ></b-table>
</div>
    `,
    methods: {
        getContainerAddress: function ( container ) {
            return this.$route.params.project + '/' + container;
        },
    },
});

// ---------------------------------------------------------------------------

// The view for the object list page, will show the user all the objects in a
// specified container that's currently being accessed. Also caches the
// accessed objects during the session to prevent unnecessary API usage.
const ObjectPage = Vue.extend({
    data: function () {
        let vals = {};
        vals['oList'] = [];
        let container = this.$route.params.container;
        if ( app.oCache[container] == undefined ) {
            getObjects( this.$route.params.container ).then(
                function ( ret ) {
                    vals['oList'] = ret;

                    for ( let i = 0; i < vals['oList'].length; i++ ) {
                        vals['oList'][i]['size'] = getHumanReadableSize(
                            vals['oList'][i]['bytes']
                        );
                    };

                    app.oCache[container] = vals['oList'];
                }
            );
        } else {
            vals['oList'] = app.oCache[container];
        };
        vals['oColumns'] = [
            {
                field: "name",
                label: "Name",
            },
            {
                field: "last_modified",
                label: "Last Modified",
            },
            {
                field: "size",
                label: "Size",
            },
        ];
        vals['selected'] = vals['oList'][0];
        return vals;
    },
    template: `
<div>
    <b-table
        style="width: 90%;margin: 5%;"
        :data="oList"
        :columns="oColumns"
        :selected.sync="selected"
        focusable
        hoverable
        detailed
        checkable
        header-checkable
    ></b-table>
</div>
    `,
});

// ----------------------------------------------------------------------------

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

const router = new VueRouter({
    mode: "history",
    routes: routes,
});

// Define the single project Vue App
const app = new Vue({
    router: router,
    data: {
        oCache: {},
        bList: undefined,
        projects: [],
        active: "",
        uname: "",
    },
    methods: {
        getRouteAsList: function () {
            // Create a list representation of the current application route
            // to help in the initialization of the breadcrumb component
            let retl = [];
            retl.push({
                alias: "browse",
                address: ( "/browse" ),
            })
            if ( this.$route.params.user != undefined ) {
                retl.push({
                    alias: this.$route.params.user,
                    address: ( "/browse/" + this.$route.params.user ),
                });
            };
            if ( this.$route.params.project != undefined ) {
                retl.push({
                    alias: this.$route.params.project,
                    address: (
                        "/browse/" + this.$route.params.user +
                        "/" + this.$route.params.project                        
                    ),
                });
            };
            if ( this.$route.params.container != undefined ) {
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
        changeProject: function ( newProject ) {
            // Re-scope to project given by the user
            changeProjectApi( newProject ).then( function ( ret ) {
                if ( ret ) {
                    getActiveProject().then( function ( value ) {
                        app.active = value;
                        app.bList = undefined;
                        app.oCache = {};
                        app.$router.push(
                            '/browse/' +
                            app.uname + '/' +
                            app.active['name']
                        );
                    })
                };
            })
        },
        logout: function () {
            // Call API to kill the session immediately
            let logoutURL = new URL( "/login/kill", document.location.origin );
            fetch(
                logoutURL,
                { method: 'GET', credential: 'include' }
            ).then( function ( response ) {
                if ( response.status = 204 ) {
                    // Impelement a page here to inform the user about a
                    // successful logout.
                }
            })
        },
    },
});

var shiftSizeDivision = function ( vallist ) {
    'use strict';
    // Javascript won't let us do anything but floating point division by
    // default, so a different approach was chosen.
    //  ( right shift by ten is a faster alias to division by 1024 )
    switch ( vallist[0] >>> 10 ) {
        case 0:
            return vallist;
        default:
            vallist[0] = vallist[0] >>> 10;
            vallist[1] = vallist[1] + 1;
            return shiftSizeDivision( vallist );
    }
};

var getHumanReadableSize = function ( val ) {
    // Get a human readable version of the size, which is returned from the
    // API as bytes, flooring to the most significant size without decimals.
    
    // As JS doesn't allow us to natively handle 64 bit integers, ditch all
    // unnecessary stuff from the value, we only need the significant part.
    let byteval = val > 4294967296 ? parseInt( val / 1073741824 ) : val;
    let count = val > 4294967296 ? 3 : 0;

    let human = shiftSizeDivision( [ byteval, count ] );
    let ret = human[0].toString();
    switch ( human[1] ) {
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
