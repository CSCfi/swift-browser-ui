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
      sharedConts: [],
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
      const minLength = 2; //only search if min chars typed in
      let query = event.detail.trim();
      if (query.length >= minLength) {
        query = escapeRegExp(query);
        const newSearchArray = tokenize(query, minLength);
        if (newSearchArray.length > 0) {
          //at least one search token formed
          this.isSearching = true;
          this.searchArray = newSearchArray;
          this.debounceSearch();
          return;
        }
      }
      this.isSearching = false;
      this.searchResults = [];
      this.searchArray = [];
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
          const re = new RegExp("^" + q, "i");

          if (item.tags !== undefined) {
            item.tags.forEach((tag, i) => {
              if (tag.match(re)) {
                item.rank = 0.0 + (i + 1) / 10;
                match.add(q);
                return;
              }
            });
          }
          item.tokens.forEach((token, i) => {
            if (token.match(re)) {
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
      const re = new RegExp("^" + query[0], "i");

      const containers = await getDB().containers
        .where({ projectID: this.active.id })
        .filter(cont => cont.tokens?.find(t => t.match(re))
          || cont.tags?.find(t => t.match(re)))
        .filter(multipleQueryWordsAndRank)
        .limit(1000)
        .toArray();
      this.searchResults = containers.map(item => ({
        ...item, value: item.name,
      })).sort(rankedSort).slice(0, 100);

      const conts = await getDB().containers
        .where({ projectID: this.active.id })
        .filter(cont => !cont.name.endsWith("_segments"))
        .limit(1000)
        .toArray();

      //get IDs of containers whose objects should be included in results
      const containerIDs = conts.map(({ id }) => id);

      //Objects in shared containers retain IDs from original container
      this.sharedConts = conts.filter(cont => cont.owner);

      //get IDs of original containers
      for(let i=0; i < this.sharedConts.length; i++) {
        const cont = await getDB().containers
          .get({
            projectID: this.sharedConts[i].owner,
            name: this.sharedConts[i].container,
          });
        this.sharedConts[i] = {...this.sharedConts[i], originalID: cont.id};
        containerIDs.push(cont.id);
      }

      const objects = await getDB().objects
        .filter(obj => obj.tokens?.find(t => t.match(re))
          || obj.tags?.find(t => t.match(re)))
        .filter(multipleQueryWordsAndRank)
        .and(obj => containerIDs.includes(obj.containerID))
        .limit(1000)
        .toArray();

      let subfolders = [];

      objects.forEach(obj => {
        const subName = obj.name.substring(0, obj.name.lastIndexOf("/"));
        const subShortName = subName.split("/").slice(-1)[0];

        if (subShortName.includes(query[0])) { //query not in other subfolders
          const index = subfolders.findIndex(sub => sub.name === subName
            && sub.container === obj.container);
          if (index < 0) {
            let count = 0;
            //add its subfolders' content
            const size = objects.reduce((result, o) => {
              if (o.name.startsWith(subName) && o.container === obj.container) {
                count++;
                result += o.bytes;
              }
              return result;
            }, 0);

            let subfolder = {
              container: obj.container, name: subName,
              subfolder: true, bytes: size, count: count,
            };

            //if shared, get owner for routing
            const sharedIndex = this.sharedConts
              .findIndex(cont => cont.originalID === obj.containerID);

            if (sharedIndex >= 0) {
              subfolder = {
                ...subfolder,
                owner: this.sharedConts[sharedIndex].owner,
              };
            }
            subfolders.push(subfolder);
          }
        }
      });

      this.searchResults = this.searchResults
        .concat(subfolders.map(item => ({
          ...item, value: item.name,
        })).sort(rankedSort).slice(0, 100))
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

      const index = this.sharedConts
        .findIndex(cont => cont.originalID === item.containerID);

      let prefix = null;
      if (item.subfolder) prefix = item.name;
      else if (item.name.includes("/")) { //for objects
        prefix = item.name.slice(0, item.name.lastIndexOf("/"));
      }

      if (item.owner || index >= 0) {
        route = {
          name: "SharedObjects",
          params: {
            container: item.container || this.sharedConts[index].container,
            owner: item.owner || this.sharedConts[index].owner,
          },
        };
      }
      else {
        //item.container for objects, name for containers
        route = {
          name: "ObjectsView",
          params: {
            container: item.container || item.name,
          },
        };
      }
      prefix !== null ? route.query={ prefix: prefix } : "";
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
