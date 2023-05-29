<template>
  <div
    class="search"
  >
    <c-autocomplete
      v-csc-control
      :items.prop="searchResults"
      :aria-label="$t('label.searchbox')"
      :placeholder="$t('message.search.searchBy')"
      hide-details
      custom-menu
      :items-per-page="8"
      @focus="searchGainedFocus"
      @changeQuery="onQueryChange"
    >
      <i
        slot="pre"
        class="mdi mdi-magnify"
      />
      <div
        v-for="(item, index) in searchResults"
        :key="index"
        slot="customMenu"
        :aria-posinset="index + 1"
        :aria-setsize="searchResults.length"
        role="option"
      >
        <c-loader
          v-show="isSearching"
        />
        <SearchResultItem
          :item="item"
          :search-array="searchArray"
          :route="getSearchRoute"
        />
      </div>
    </c-autocomplete>
    <c-toasts
      id="searchbox-toasts"
      data-testid="searchbox-toasts"
      vertical="top"
      horizontal="right"
    />
  </div>
</template>

<script>
import { tokenize } from "@/common/conv";
import { getDB } from "@/common/db";
import escapeRegExp from "lodash/escapeRegExp";
import SearchResultItem from "@/components/SearchResultItem.vue";
import debounce from "lodash/debounce";

export default {
  name: "SearchBox",
  components: {
    SearchResultItem,
  },
  props: ["containers"],
  data: function () {
    return {
      searchArray: [],
      searchResults: [],
      searchElements: [],
      selectedItem: null,
      refs: [],
      isSearching: false,
    };
  },
  computed: {
    active() {
      return this.$store.state.active;
    },
  },
  created: function () {
    this.debounceSearch = debounce(this.search, 400);
  },
  methods: {
    onQueryChange: function (event) {
      const safeQuery = escapeRegExp(event.detail);
      const query = safeQuery.trim();
      const newSearchArray = tokenize(query, 0);
      // Run debounced search every time the search box input changes
      if (newSearchArray.length > 0 && newSearchArray[0].length > 1) {
        this.isSearching = true;
        this.searchArray = newSearchArray;
        this.debounceSearch();
      } else {
        this.isSearching = false;
        this.searchResults = [];
        this.searchArray = [];
      }
    },
    search: async function () {
      if (this.searchArray.length === 0) {
        return;
      }
      const query = [...this.searchArray];

      function multipleQueryWordsAndRank(item) {
        // Narrows down search results when there are more than
        // Ranks results as such:
        // Items with tag match have highest rank
        // Ranks based on array index they match
        const rankOffset = item.container ? 2.0 : 1.0;
        let match = new Set();
        query.map(q => {
          if (item.tags !== undefined) {
            item.tags.forEach((tag, i) => {
              if (tag.startsWith(q)) {
                item.rank = 0.0 + (i + 1) / 10;
                match.add(q);
                return;
              }
            });
          }
          item.tokens.forEach((token, i) => {
            if (token.startsWith(q)) {
              item.rank = rankOffset + (i + 1) / 10;
              match.add(q);
              return;
            }
          });
        });
        if (match.size === query.length) {
          return true;
        }
        return false;
      }

      const rankedSort = (a, b) => a.rank - b.rank;

      const containers = await getDB().containers
        .where("tokens")
        .startsWith(query[0])
        .or("tags")
        .startsWith(query[0])
        .filter(multipleQueryWordsAndRank)
        .and(cont => cont.projectID === this.active.id)
        .limit(1000)
        .toArray();
      this.searchResults = containers.map(item => ({
        ...item, value: item.name,
      })).sort(rankedSort).slice(0, 100);

      const containerIDs = new Set(
        await getDB().containers
          .where({ projectID: this.active.id })
          .primaryKeys(),
      );

      const objects = await getDB().objects
        .where("tokens")
        .startsWith(query[0])
        .or("tags")
        .startsWith(query[0])
        .filter(multipleQueryWordsAndRank)
        .and(obj => containerIDs.has(obj.containerID))
        .limit(1000)
        .toArray();

      this.searchResults = this.searchResults
        .concat(objects.map(item => ({
          ...item, value: item.name,
        })).sort(rankedSort).slice(0, 100))
        .sort(rankedSort);
      this.isSearching = false;
    },
    getSearchRoute: function (item) {
      if (!item) {
        return null;
      }
      let route = {};
      if (item.owner) {
        route = {
          name: "SharedObjects",
          params: {
            container: item.container,
            owner: item.owner,
          },
        };
      }
      else {
        route = {
          name: "ObjectsView",
          params: {
            container: item.name,
          },
        };
      }

      if (item.container) {
        route["query"] = { selected: item.name };
      }
      return route;
    },
    searchGainedFocus: async function () {
      const preferences = await getDB().preferences.get(1);

      const ojbCount = this.containers.reduce(
        (prev, cont) => prev + cont.count,
        0,
      );

      if (
        !(
          this.active.id in preferences &&
          preferences[this.active.id].largeProjectNotification
        ) &&
        ojbCount >= 10000
      ) {
        document.querySelector("#searchbox-toasts").addToast(
          {
            duration: 20000,
            type: "info",
            progress: false,
            message: this.$t("message.search.buildingIndex"),
          },
        );
        getDB().preferences
          .where(":id")
          .equals(1)
          .modify({ [this.active.id]: { largeProjectNotification: true } });
      }
    },
  },
};
</script>
<style scoped lang="scss">
 @import "@/css/prod.scss";
.empty-search {
  height: 2rem;
}

div[aria-selected='true'], div[slot="customMenu"]:hover {
  background-color: $csc-primary-lighter;
}
</style>
