// Create VueI18n instance with options

function getLangCookie() {
    let matches = document.cookie.match(new RegExp(
      "(?:^|; )" + 'lang' + "=([^;]*)"
    ));
    return matches ? decodeURIComponent(matches[1]) : 'en';
  }

const i18n = new VueI18n({
    locale: getLangCookie(), // set locale
    messages: langPlaceholders, // set locale messages
});

// Depends on vue.js and vue-router, needs ES6 support to work

// To improve readability some larger code blocks are separated by a dash-line.
// This is just to test whether or not this is something I want to start using

// NOTE: All the components used in the routing can be found from the
// btablecomp.js file.

// The view for the application front page. Currently does nothing as it's not
// needed yet.
const FrontPage = Vue.extend({
    template: `
<div>
    <p>Not yet implemented</p>
</div>
    `,
});

// ---------------------------------------------------------------------------

// The view for the application user page for showing the user information in
// a bit more detail. Shows e.g. the storage expenditure and the billing unit
// (BU) usage caused by that.
const UserPage = Vue.extend({
    data: function () {
        return {
            Containers: undefined,
            Objects: undefined,
            Account: undefined,
            Size: undefined,
            Billed: undefined,
            Bytes: undefined,
            DisableTooltip: false,
        }
    },
    methods: {
        fetchMeta: function () {
            getProjectMeta().then((ret) => {
                this.Containers = ret["Containers"];
                this.Objects = ret["Objects"];
                this.Account = ret["Account"];
                this.Size = ret["Size"];
                this.Billed = ret["Billed"];
                this.Bytes = ret["Bytes"];
            })
        },
        disable: function() {
            if (document.cookie.match("DISABLE_BILLING_NOTE")) {
                this.DisableTooltip = true;
            }
            else {
                setTimeout(() => {
                    this.DisableTooltip = true
                    document.cookie = "DISABLE_BILLING_NOTE=true"
                }, 4000)
            }
        }
    },
    beforeMount(){
        this.fetchMeta();
        this.disable();
        if ( app.active == undefined || app.active == "" ) {
            getActiveProject().then( function ( value ) {
                app.active = value;
            })
        }
    },
    template: `
<div class="dashboard">
    <div class="tile is-ancestor">
        <div class="tile is-parent is-horizontal is-4">
            <div class="tile is-child box">
                <p class="title is-size-5">{{ $t('message.dashboard.prj_usage') }}</p>
                <p>
                    <ul>
                        <li>{{ $t('message.dashboard.account') }} {{ Account }}</li>
                        <li>{{ $t('message.dashboard.containers') }} {{ Containers }}</li>
                        <li>{{ $t('message.dashboard.objects') }} {{ Objects }}</li>
                        <li>{{ $t('message.dashboard.usage') }} {{ Size }}</li>
                    </ul>
                </p>
            </div>
        </div>
        <div class="tile is-parent is-horizontal is-8">
            <div class="tile is-child box">
                <p class="title is-size-5">{{ $t('message.dashboard.cur_billing') }}</p>
                <progress
                    v-if="Bytes < 1099511627776"
                    class="progress is-success is-large"
                    :value="Bytes"
                    :max="1099511627776"
                >{{ parseInt(Bytes/1099511627776) }}</progress>
                <progress
                    v-else
                    class="progress is-danger is-large"
                    :value="Bytes"
                    :max="1099511627776"
                >{{ parseInt(Bytes/1099511627776) }}</progress>
                <p>
                    <ul>
                        <li>
                        <b>{{ $t('message.dashboard.prj_str_usag') }} </b> {{ Size }} / 1TiB
                        <b-tooltip
                            v-if="!DisableTooltip"
                            size="is-large"
                            :label="$t('message.dashboard.default_notify')"
                            position="is-right"
                            multilined
                            always
                        >
                            <b-icon size="is-small" icon="information"></b-icon>
                        </b-tooltip>
                        <b-tooltip
                            v-else
                            size="is-large"
                            :label="$t('message.dashboard.default_notify')"
                            position="is-right"
                            multilined
                        >
                            <b-icon size="is-small" icon="information"></b-icon>
                        </b-tooltip>
                        </li>
                        <li><b>{{ $t('message.dashboard.equals') }} </b> {{ Billed }} <b>BU / {{ $t('message.dashboard.hour') }} </b></li>
                    </ul>
                </p>
            </div>
        </div>
    </div>
    <div class="tile is-ancestor">
        <div class="tile is-parent is-horizontal is-12">
            <div class="tile is-child is-12 box">
                <p class="title is-size-5">{{ $t('message.dashboard.more_info') }}</p>
                <ul>
                    <li><a 
                        target="_blank"
                        :href="$t('message.dashboard.pouta_accounting')"
                    >{{ $t('message.dashboard.billing_info') }}</a></li>
                    <li><a 
                        target="_blank"
                        :href="$t('message.dashboard.pouta_obj_store_quota_info')"
                    >{{ $t('message.dashboard.quota_info') }}</a></li>
                    <li><a 
                        target="_blank" 
                        :href="$t('message.dashboard.my_csc')"
                    >{{ $t('message.dashboard.avail_info') }}</a></li>
                </ul>
            </div>
        </div>
    </div>
</div>
    `,
});

// ---------------------------------------------------------------------------

// The view for the container list page, will show the user all the containers
// that are available for the project that's currently being accessed.
// Data needs to be pulled from the parent class with a function, because
// vue.js has it's own way of doing things with a strict hierarchy
const ContainerPage = Vue.extend({
    data: function () {
        let vals = {};
        vals['bList'] = [];
        if (app.bList == undefined) {
            app.isLoading = true;
            getBuckets().then(function (ret) {
                if (ret.status != 200) {
                    app.isLoading = false;
                }
                vals['bList'] = ret;

                app.bList = vals['bList']
                app.isLoading = false;
            }).catch(function () {
                app.isLoading = false;
            }
            );
        } else {
            vals['bList'] = app.bList;
        };
        vals['selected'] = vals['bList'][0];
        vals['isPaginated'] = true;
        vals['perPage'] = 15;
        vals['defaultSortDirection'] = 'asc';
        vals['searchQuery'] = ""
        vals['currentPage'] = (
            this.$route.query.page ? parseInt(this.$route.query.page) : 1
        );
        return vals;
    },
    watch: {
        searchQuery: function () {
            this.debounceFilter();
        }
    },
    created: function () {
        this.debounceFilter = _.debounce(this.filter, 400);
    },
    template: `
<div id="container-table">
    <b-field grouped group-multiline class="groupControls">
        <b-select v-model="perPage" :disabled="!isPaginated">
            <option value="5"> 5 {{ $t('message.table.pageNb') }}</option>
            <option value="10"> 10 {{ $t('message.table.pageNb') }}</option>
            <option value="15"> 15 {{ $t('message.table.pageNb') }}</option>
            <option value="25"> 25 {{ $t('message.table.pageNb') }}</option>
            <option value="50"> 50 {{ $t('message.table.pageNb') }}</option>
            <option value="100"> 100 {{ $t('message.table.pageNb') }}</option>
        </b-select>
        <div class="control is-flex">
            <b-switch 
                v-if="bList.length < 500"
                v-model="isPaginated"
            >{{ $t('message.table.paginated') }}</b-switch>
        </div>
        <b-field class="control searchBox">
            <b-input v-model="searchQuery" v-bind:placeholder="$t('message.searchBy')"/>
        </b-field>      
    </b-field>
    <b-table
        style="width: 90%;margin-left: 5%; margin-right: 5%;"
        :data="bList"
        :selected.sync="selected"
        :current-page.sync="currentPage"
        v-on:page-change="(page) => addPageToURL ( page )"
        v-on:dblclick="(row) => $router.push( getContainerAddress ( row['name'] ) )"
        v-on:keyup.native.enter="$router.push( getContainerAddress ( selected['name'] ))"
        v-on:keyup.native.space="$router.push( getContainerAddress ( selected['name'] ))"
        :paginated="isPaginated"
        :per-page="perPage"
        :pagination-simple="isPaginated"
        :default-sort-direction="defaultSortDirection"
        default-sort="name"
        focusable
        hoverable
        narrowed
    >
        <template slot-scope="props">
            <b-table-column field="name" :label="$t('message.table.name')" sortable>
                <span v-if="!props.row.bytes">
                    <b-icon icon="folder-outline" size="is-small">
                    </b-icon> 
                   {{ props.row.name }}
                </span>
                <span v-else>
                    <b-icon icon="folder" size="is-small">
                    </b-icon> 
                    <strong> {{ props.row.name }}  </strong>
                </span>
            </b-table-column>
            <b-table-column field="count" :label="$t('message.table.objects')" width="120" sortable>
                {{ props.row.count }}
            </b-table-column>
            <b-table-column field="bytes" :label="$t('message.table.size')" width="120" sortable>
                {{ localHumanReadableSize(props.row.bytes) }}
            </b-table-column>
        </template>
        <template slot="empty" slot-scope="props">
            <p
                style="text-align:center;margin-top:5%;margin-bottom:5%;"
            >{{ $t('message.emptyProject') }}</span>
            </p>
        </template>
    </b-table>
</div>
    `,
    methods: {
        getContainerAddress: function (container) {
            return this.$route.params.project + '/' + container;
        },
        addPageToURL: function (pageNumber) {
            this.$router.push("?page=" + pageNumber);
        },
        localHumanReadableSize: function (size) {
            return getHumanReadableSize(size);
        },
        filter: function() {
            var name_cmp = new RegExp(this.searchQuery, 'i');
            this.bList = app.bList.filter(
                element => element.name.match(name_cmp)
            );
        }
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
        if (app.oCache[container] == undefined) {
            app.isLoading = true;
            getObjects(this.$route.params.container).then(
                function (ret) {
                    if (ret.status != 200) {
                        app.isLoading = false;
                    }
                    vals['oList'] = ret;

                    // Purge old cached items from object query cache if the
                    // cache has grown to be too large (250000).
                    recursivePruneCache(app.oCache);

                    app.oCache[container] = vals['oList'];
                    app.isLoading = false;
                }
            ).catch(function () {
                app.isLoading = false;
            });
        } else {
            vals['oList'] = app.oCache[container];
        };
        vals['selected'] = vals['oList'][0];
        vals['isPaginated'] = true;
        vals['perPage'] = 15;
        vals['defaultSortDirection'] = 'asc';
        vals['searchQuery'] = "";
        if (document.cookie.match("ENA_DL")) {
            vals['allowLargeDownloads'] = true;
        } else { vals['allowLargeDownloads'] = false; };
        vals['currentPage'] = (
            this.$route.query.page ? parseInt(this.$route.query.page) : 1
        );
        return vals;
    },
    watch: {
        searchQuery: function () {
            this.debounceFilter();
        }
    },
    created: function () {
        this.debounceFilter = _.debounce(this.filter, 400);
    },
    template: `
<div id="object-table">
    <b-field grouped group-multiline class="groupControls">
        <b-select v-model="perPage" :disabled="!isPaginated">
            <option value="5"> 5 {{ $t('message.table.pageNb') }}</option>
            <option value="10"> 10 {{ $t('message.table.pageNb') }}</option>
            <option value="15"> 15 {{ $t('message.table.pageNb') }}</option>
            <option value="25"> 25 {{ $t('message.table.pageNb') }}</option>
            <option value="50"> 50 {{ $t('message.table.pageNb') }}</option>
            <option value="100"> 100 {{ $t('message.table.pageNb') }}</option>
        </b-select>
        <div class="control is-flex">
            <b-switch
                v-if="oList.length < 500"
                v-model="isPaginated"
            >{{ $t('message.table.paginated') }}</b-switch>
        </div>
        <b-field class="control searchBox">
            <b-input v-model="searchQuery" v-bind:placeholder="$t('message.searchBy')"/>
        </b-field>
    </b-field>
    <b-table
        style="width: 90%;margin-left: 5%; margin-right: 5%;"
        :data="oList"
        :selected.sync="selected"
        :current-page.sync="currentPage"
        focusable
        hoverable
        detailed
        header-checkable
        narrowed
        :paginated="isPaginated"
        :per-page="perPage"
        :pagination-simple="isPaginated"
        :default-sort-direction="defaultSortDirection"
        default-sort="name"
        v-on:page-change="( page ) => addPageToURL( page )"
    >
        <template slot-scope="props">
            <b-table-column field="name" :label="$t('message.table.name')" sortable>
                {{ props.row.name }}
            </b-table-column>
            <b-table-column field="last_modified" :label="$t('message.table.modified')" sortable>
                {{ localHumanReadableDate(props.row.last_modified) }}
            </b-table-column>
            <b-table-column field="bytes" :label="$t('message.table.size')" sortable>
                {{ localHumanReadableSize(props.row.bytes) }}
            </b-table-column>
            <b-table-column field="url" label="" width="110">
                <a
                    v-if="props.row.bytes < 1073741824"
                    :href="props.row.url"
                    target="_blank"
                    :alt="$t('message.downloadAlt') + ' ' + props.row.name"
                >
                <b-icon icon="cloud-download" size="is-small">
                </b-icon> {{ $t('message.download') }}
                </a>
                <a
                    v-else-if="allowLargeDownloads"
                    :href="props.row.url"
                    target="_blank"
                    :alt="$t('message.downloadAlt') + ' ' + props.row.name"
                >
                <b-icon icon="cloud-download" size="is-small">
                </b-icon> {{ $t('message.download') }}
                </a>
                <a
                    v-else
                    @click="confirmDownload ()"
                    :alt="$t('message.downloadAltLarge') + ' ' + props.row.name"
                >
                <b-icon icon="cloud-download" size="is-small">
                </b-icon> {{ $t('message.download') }}
                </a>
            </b-table-column>
        </template>
        <template slot="detail" slot-scope="props">
            <ul>
            <li>
                <b>{{ $t('message.table.fileHash') }}: </b>{{ props.row.hash }}
            </li>
            <li>
                <b>{{ $t('message.table.fileType') }}: </b>{{ props.row.content_type }} 
            </li>
            <li>
                <b>{{ $t('message.table.fileDown') }}: </b>
                <a
                    v-if="props.row.bytes < 1073741824"
                    :href="props.row.url"
                    target="_blank"
                    :alt="$t('message.downloadAlt') + ' ' + props.row.name"
                >
                <b-icon icon="cloud-download" size="is-small">
                </b-icon> {{ $t('message.downloadLink') }}
                </a>
                <a
                    v-else-if="allowLargeDownloads"
                    :href="props.row.url"
                    target="_blank"
                    :alt="$t('message.downloadAlt') + ' ' + props.row.name"
                >
                <b-icon icon="cloud-download" size="is-small">
                </b-icon> {{ $t('message.downloadLink') }}
                </a>
                <a
                    v-else
                    @click="confirmDownload ()"
                    :alt="$t('message.downloadAltLarge') + ' ' + props.row.name"
                >
                <b-icon icon="cloud-download" size="is-small">
                </b-icon> {{ $t('message.downloadLink') }}
                </a>
            </li>
            </ul>
        </template>
        <template slot="empty" slot-scope="props">
            <p
                style="width:100%;text-align:center;margin-top:5%;margin-bottom:5%"
            >{{ $t('message.emptyContainer') }}</p>
        </template>
    </b-table>
</div>
    `,
    methods: {
        addPageToURL: function (pageNumber) {
            this.$router.push("?page=" + pageNumber)
        },
        confirmDownload: function () {
            this.$snackbar.open({
                duration: 5000,
                message: this.$t('message.largeDownMessage'),
                type: "is-success",
                position: "is-top",
                actionText: this.$t('message.largeDownAction'),
                onAction: this.enableDownload,
            })
        },
        enableDownload: function () {
            this.allowLargeDownloads = true;
            const expiryDate = new Date();
            expiryDate.setMonth(expiryDate.getMonth() + 1);
            document.cookie = 'ENA_DL=' + this.allowLargeDownloads + '; path=/; expires=' + expiryDate.toUTCString();
        },
        localHumanReadableSize: function ( size ) {
            return getHumanReadableSize( size );
        },
        localHumanReadableDate: function ( date ) {
            return getHumanReadableDate( date );
        },
        filter: function () {
            var name_re = new RegExp(this.searchQuery, 'i')
            this.oList = app.oCache[this.$route.params.container].filter(
                element => element.name.match(name_re)
            )
        }
    },
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
            // retl.push({
            //     alias: "browse",
            //     address: ( "/browse" ),
            // })
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
        logout: function () {
            // Call API to kill the session immediately
            let logoutURL = new URL("/login/kill", document.location.origin);
            fetch(
                logoutURL,
                { method: 'GET', credentials: 'include' }
            ).then(function (response) {
                if (response.status = 204) {
                    // Impelement a page here to inform the user about a
                    // successful logout.
                }
            })
        },
        setCookieLang: function() {
            const expiryDate = new Date();
            expiryDate.setMonth(expiryDate.getMonth() + 1);
            document.cookie = 'lang=' + i18n.locale + '; path=/; expires=' + expiryDate.toUTCString();
            this.$router.go(this.$router.currentRoute);
        },
        getProjectChangeURL ( newProject ) {
            let rescopeURL = new URL( "/login/rescope", document.location.origin );
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
    var options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric',
                    hour:'2-digit', minute: '2-digit', second: '2-digit' };
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