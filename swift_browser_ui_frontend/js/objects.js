// The view for the object list page, will show the user all the objects in a
// specified container that's currently being accessed. Also caches the
// accessed objects during the session to prevent unnecessary API usage.
const ObjectPage = Vue.extend({
    data: function () {
        let vals = {};
        vals['oList'] = [];
        // The container queried is specified by the route
        let container = this.$route.params.container;
        // If the object listing isn't cached, pull it from the API using a
        // convenience function in api.js
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
        // Large downloads are prevented by default, but can be enabled with a
        // button for the duration of the session
        if (document.cookie.match("ENA_DL")) {
            vals['allowLargeDownloads'] = true;
        } else { vals['allowLargeDownloads'] = false; };
        // Get the current page to navigate to directly, if that's specified
        vals['currentPage'] = (
            this.$route.query.page ? parseInt(this.$route.query.page) : 1
        );
        return vals;
    },
    // Search function specific things are also commented in containers.js
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
            // Snackbar for enabling large downloads for the duration of the
            // session
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
            // Enables large downloads upon execution
            this.allowLargeDownloads = true;
            const expiryDate = new Date();
            expiryDate.setMonth(expiryDate.getMonth() + 1);
            document.cookie = 'ENA_DL=' +
                this.allowLargeDownloads +
                '; path=/; expires=' +
                expiryDate.toUTCString();
        },
        // Make human readable translation functions available in instance
        // namespace
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
