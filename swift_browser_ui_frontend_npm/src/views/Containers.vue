<template>
  <div id="container-table">
    <b-field
      grouped
      group-multiline
      class="groupControls"
    >
      <b-select
        v-model="perPage"
        :disabled="!isPaginated"
      >
        <option value="5">
          5 {{ $t('message.table.pageNb') }}
        </option>
        <option value="10">
          10 {{ $t('message.table.pageNb') }}
        </option>
        <option value="15">
          15 {{ $t('message.table.pageNb') }}
        </option>
        <option value="25">
          25 {{ $t('message.table.pageNb') }}
        </option>
        <option value="50">
          50 {{ $t('message.table.pageNb') }}
        </option>
        <option value="100">
          100 {{ $t('message.table.pageNb') }}
        </option>
      </b-select>
      <div class="control is-flex">
        <b-switch 
          v-if="bList.length < 500"
          v-model="isPaginated"
        >
          {{ $t('message.table.paginated') }}
        </b-switch>
      </div>
      <b-field class="control searchBox">
        <b-input
          v-model="searchQuery"
          :placeholder="$t('message.searchBy')"
        />
      </b-field>      
    </b-field>
    <b-table
      focusable
      hoverable
      narrowed
      style="width: 90%;margin-left: 5%; margin-right: 5%;"
      default-sort="name"
      :data="bList"
      :selected.sync="selected"
      :current-page.sync="currentPage"
      :paginated="isPaginated"
      :per-page="perPage"
      :pagination-simple="isPaginated"
      :default-sort-direction="defaultSortDirection"
      @page-change="(page) => addPageToURL ( page )"
      @dblclick="(row) => $router.push( getContainerAddress ( row['name'] ) )"
      @keyup.native.enter="$router.push( getContainerAddress ( selected['name'] ))"
      @keyup.native.space="$router.push( getContainerAddress ( selected['name'] ))"
    >
      <template slot-scope="props">
        <b-table-column
          sortable
          field="name"
          :label="$t('message.table.name')"
        >
          <span v-if="!props.row.bytes">
            <b-icon
              icon="folder-outline"
              size="is-small"
            /> 
            {{ props.row.name }}
          </span>
          <span
            v-else
            class="has-text-weight-bold"
          >
            <b-icon
              icon="folder"
              size="is-small"
            /> 
            {{ props.row.name }}
          </span>
        </b-table-column>
        <b-table-column
          field="count"
          :label="$t('message.table.objects')"
          width="120"
          sortable
        >
          {{ props.row.count }}
        </b-table-column>
        <b-table-column
          field="bytes"
          :label="$t('message.table.size')"
          width="120"
          sortable
        >
          {{ localHumanReadableSize(props.row.bytes) }}
        </b-table-column>
      </template>
      <template slot="empty">
        <p
          style="text-align:center;margin-top:5%;margin-bottom:5%;"
        >
          {{ $t('message.emptyProject') }}
        </p>
      </template>
    </b-table>
  </div>
</template>

<script>
import getBuckets from "@/api";
import getHumanReadableSize from "@/conv";
import debounce from "lodash/debounce";

export default {
  name: "Containers",
  data: function () {
    return {
      bList: [],
      selected: undefined,
      isPaginated: true,
      perPage: 15,
      defaultSortDirection: "asc",
      searchQuery: "",
      currentPage: 1,
    };
  },
  watch: {
    searchQuery: function () {
      // Run debounced search every time the search box input changes
      this.debounceFilter();
    },
  },
  created: function () {
    // Lodash debounce to prevent the search execution from executing on
    // every keypress, thus blocking input
    this.debounceFilter = debounce(this.filter, 400);
  },
  methods: {
    getContainers: function () {
      // Get the container listing from the API if the listing hasn't yet
      // been cached.
      this.$store.commit("setLoading", true);
      getBuckets().then((ret) => {
        if (ret.status != 200) {
          this.$store.commit("setLoading", false);
        }
        this.$store.commit("updateContainers", ret);
        this.$store.commit("setLoading", false);
      }).catch(() => {
        this.$store.commit("setLoading", false);
      });
    },
    checkPageFromRoute: function () {
      // Check if the pagination number is already specified in the link
      if (this.$route.query.page) {
        this.currentPage = parseInt(this.$route.query.page);
      } else {
        this.currentPage = 1;
        this.$router.push("?page=" + this.currentPage);
      }
    },
    getContainerAddress: function (container) {
      return this.$route.params.project + "/" + container;
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
      var name_cmp = new RegExp(this.searchQuery, "i");
      this.bList = this.$state.store.containerCache.filter(
        element => element.name.match(name_cmp)
      );
    },
  },
  beforeMount () {
    this.getContainers();
  },
};
</script>
