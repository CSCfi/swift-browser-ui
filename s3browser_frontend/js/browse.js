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
                app.bList = vars['bList']
            });
        } else {
            vars['bList'] = app.bList;
        }
        return vars;
    },
    template: '\
<div>\
    <table id=\'btable\'>\
        <tr\
            is="bucket-table-heading"\
        ></tr>\
        <tr\
            is="bucket-table-row"\
            v-for="item in bList"\
            v-bind:key="item.name"\
            v-bind:bname="item.name"\
            v-bind:baddress="getContainerAddress ( item.name )"\
            v-on:bclick="showContainer( item.name )"\
        ></tr>\
    </table>\
</div>\
    ',
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
                    app.oCache[container] = vals['oList'];
                }
            );
        } else {
            vals['oList'] = app.oCache[container];
        }
        return vals;
    },
    template: '\
<div>\
    <table id=\'otable\'>\
        <tr\
            is="object-table-heading"\
            v-on:oheadingclick="$emit(\'oheadingclick\')"\
        ></tr>\
        <tr\
            is="object-table-row"\
            v-for="item in oList"\
            v-bind:key=\'item.name\'\
            v-bind:stobject=\'item\'\
            v-bind:dloadlink=\'item.url\'\
            v-on:oheadingclick="$emit( \'oheadingclick\' )"\
        ></tr>\
    </table>\
</div>\
    ',
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
        oCache: [],
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
    },
});
