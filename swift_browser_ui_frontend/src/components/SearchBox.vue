<template>    
  <c-autocomplete
    id="searchbox"
    v-control
    :label="$t('message.search.searchBy')"
    shadow
    :items.prop="searchResults"
    @changeQuery="searchQuery"
  >
    <i
      slot="pre"
      class="mdi mdi-magnify"
    />
  </c-autocomplete>
</template>

<script>
import { tokenize } from "@/common/conv";
import escapeRegExp from "lodash/escapeRegExp";
// import SearchResultItem from "@/components/SearchResultItem";
import debounce from "lodash/debounce";

export default {
  name: "SearchBox",
  components: {
    // SearchResultItem,
  },
  data: function () {
    return {
      searchArray: [],
      searchResults: [],
      debounceSearch: debounce(this.search, 400),
      isSearching: false,
    };
  },
  computed: {
    active() {
      return this.$store.state.active;
    },
  },
  methods: {
    searchQuery: function (event) {
      this.debounceSearch.cancel();
      // request parameter should be sanitized first
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

      const containers = await this.$store.state.db.containers
        .where("tokens")
        .startsWith(query[0])
        .or("tags")
        .startsWith(query[0])
        .filter(cont => !cont.name.endsWith("_segments"))
        .filter(multipleQueryWordsAndRank)
        .and(cont => cont.projectID === this.active.id)
        .limit(1000)
        .toArray();
      this.searchResults = containers.sort(rankedSort).slice(0, 100);

      const containerIDs = new Set(
        await this.$store.state.db.containers
          .where({ projectID: this.active.id })
          .filter(cont => !cont.name.endsWith("_segments"))
          .primaryKeys(),
      );

      const objects = await this.$store.state.db.objects
        .where("tokens")
        .startsWith(query[0])
        .or("tags")
        .startsWith(query[0])
        .filter(multipleQueryWordsAndRank)
        .and(obj => containerIDs.has(obj.containerID))
        .limit(1000)
        .toArray();

      this.searchResults = this.searchResults
        .concat(objects.sort(rankedSort).slice(0, 100))
        .sort(rankedSort);
      this.isSearching = false;
    },
    getSearchRoute: function (item) {
      if (!item) {
        return null;
      }
      let route = {
        name: "ObjectsView",
        params: {
          container: item.container || item.name,
        },
      };
      if (item.container) {
        route["query"] = { selected: item.name };
      }
      return route;
    },
    searchGainedFocus: async function () {
      const preferences = await this.$store.state.db.preferences.get(1);

      const ojbCount = this.containers.value.reduce(
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
        this.$buefy.notification.open({
          message: this.$t("message.search.buildingIndex"),
          type: "is-info",
          position: "is-top-right",
          duration: 20000,
          hasIcon: true,
        });
        this.$store.state.db.preferences
          .where(":id")
          .equals(1)
          .modify({ [this.active.id]: { largeProjectNotification: true } });
      }
    },
  },
};
</script>
