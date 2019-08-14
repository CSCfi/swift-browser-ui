// The view for the container list page, will show the user all the containers
// that are available for the project that's currently being accessed.
// Data needs to be pulled from the parent class with a function, because
// vue.js has it's own way of doing things with a strict hierarchy
const ContainerPage = Vue.extend({
    data: function () {
        let vals = {};
        vals['bList'] = [];
        // If the listing isn't cached yet, pull the container listing from
        // from the backend API using a function in api.js
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
        vals['isPaginated'] = true;  // Pagination on by default
        vals['perPage'] = 15;  // Default page size
        vals['defaultSortDirection'] = 'asc';
        vals['searchQuery'] = ""
        // If current page is linked in the query string, navigate directly
        // to the page
        vals['currentPage'] = (
            this.$route.query.page ? parseInt(this.$route.query.page) : 1
        );
        return vals;
    },
    watch: {
        searchQuery: function () {
            // Run debounced search every time the search box input changes
            this.debounceFilter();
        }
    },
    created: function () {
        // Lodash debounce to prevent the search execution from executing on
        // every keypress, thus blocking input
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
                <span v-else class="has-text-weight-bold">
                    <b-icon icon="folder" size="is-small">
                    </b-icon> 
                    {{ props.row.name }}
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
            // Add pagination current page number to the URL in query string
            this.$router.push("?page=" + pageNumber);
        },
        localHumanReadableSize: function (size) {
            // Make getHumanReadableSize usable in instance namespace
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
