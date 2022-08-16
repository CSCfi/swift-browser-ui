<template>
  <div>
    <c-modal
      v-control
      v-csc-model="openCreateFolderModal"
    >
      <CreateFolderModal />
    </c-modal>
    <c-modal
      v-control
      v-csc-model="openUploadModal"
    >
      <UploadModal />
    </c-modal>
    <div class="contents">
      <b-field
        grouped
        group-multiline
        class="groupControls"
      >
        <b-select
          v-model="perPage"
          data-testid="containersPerPage"
          :disabled="!isPaginated"
        >
          {{ $t("message.table.paginated") }}
        </b-switch>
        <b-switch v-model="showTags">
          {{ $t("message.table.showTags") }}
        </b-switch>
      </div>
      <b-autocomplete
        id="searchbox"
        v-model="searchQuery"
        rounded
        icon="magnify"
        clearable
        :placeholder="$t('message.search.searchBy')"
        :data="searchResults"
        field="name"
        :open-on-focus="true"
        :keep-first="true"
        :loading="isSearching"
        max-height="350px"
        @select="(option) => $router.push(getSearchRoute(option))"
        @focus="(event) => searchGainedFocus()"
      >
        <template slot-scope="props">
          <SearchResultItem
            :item="props.option"
            :search-array="searchArray"
            :route="getSearchRoute"
          />
        </template>
        <template #empty>
          <div
            v-if="searchArray.length > 0 && searchArray[0].length > 1"
            class="media empty-search"
          >
            {{ $t("message.table.paginated") }}
          </b-switch>
          <b-switch v-model="showTags">
            {{ $t("message.table.showTags") }}
          </b-switch>
        </div>
        <b-autocomplete
          id="searchbox"
          v-model="searchQuery"
          rounded
          icon="magnify"
          clearable
          :placeholder="$t('message.search.searchBy')"
          :data="searchResults"
          field="name"
          :open-on-focus="true"
          :keep-first="true"
          :loading="isSearching"
          max-height="350px"
          @select="option => $router.push(getSearchRoute(option))"
          @focus="event => searchGainedFocus()"
        >
          <template slot-scope="props">
            <SearchResultItem
              :item="props.option"
              :search-array="searchArray"
              :route="getSearchRoute"
            />
          </template>
          <template #empty>
            <div
              v-if="searchArray.length > 0 && searchArray[0].length > 1"
              class="media empty-search"
            >
              <b-loading
                v-model="isSearching"
                :is-full-page="false"
              />
              <div
                v-show="!isSearching"
                class="media-content"
              >
                {{ $t("message.search.empty") }}
              </div>
            </div>
          </div>
        </template>
      </b-autocomplete>
    </b-field>
    <b-table
      focusable
      hoverable
      narrowed
      default-sort="name"
      :data="containers.value"
      :selected.sync="selected"
      :current-page.sync="currentPage"
      :paginated="isPaginated"
      :per-page="perPage"
      :pagination-simple="isPaginated"
      :default-sort-direction="defaultSortDirection"
      @page-change="page => addPageToURL(page)"
      @dblclick="row => $router.push(getConAddr(row['name']))"
      @keyup.native.enter="viewFolder"
      @keyup.native.space="viewFolder"
    >
      <b-table-column
        sortable
        field="name"
        :label="$t('message.table.name')"
      >
        <b-table-column
          sortable
          field="name"
          :label="$t('message.table.name')"
        >
          <template #default="props">
            <span
              :class="props.row.count ?
                'title is-6' : ''"
            >
              <b-icon
                :icon="props.row.count ? 'folder' : 'folder-outline'"
                size="is-small"
              />
              {{ props.row.name | truncate(100) }}
            </span>
            <b-taglist v-if="showTags">
              <b-tag
                v-for="tag in props.row.tags"
                :key="tag"
                :type="selected == props.row ?
                        'is-primary-invert' : 'is-primary'"
                rounded
                ellipsis
              >
                {{ tag }}
              </b-tag>
            </b-taglist>
          </template>
        </b-table-column>
        <b-table-column
          field="count"
          :label="$t('message.table.objects')"
          width="120"
          sortable
        >
          <template #default="props">
            {{ props.row.count }}
          </template>
        </b-table-column>
        <b-table-column
          field="bytes"
          :label="$t('message.table.size')"
          width="120"
          sortable
        >
          <template #default="props">
            {{ localHumanReadableSize(props.row.bytes) }}
          </template>
        </b-table-column>
        <b-table-column
          field="functions"
          label=""
          width="150"
        >
          <template #default="props">
            <div class="field has-addons">
              <p class="control">
                <ContainerDownloadLink
                  v-if="selected == props.row"
                  class="is-small"
                  :inverted="true"
                  :disabled="!props.row.bytes ? true : false"
                  :container="props.row.name"
                />
                <ContainerDownloadLink
                  v-else
                  class="is-small"
                  :disabled="!props.row.bytes ? true : false"
                  :container="props.row.name"
                />
              </p>
              <p
                v-if="!props.row.bytes"
                class="control"
              >
                <b-button
                  v-if="selected == props.row"
                  type="is-primary"
                  outlined
                  size="is-small"
                  disabled
                  inverted
                  icon-left="share"
                >
                  {{ $t("message.share.share") }}
                </b-button>
                <b-button
                  v-else
                  type="is-primary"
                  outlined
                  size="is-small"
                  disabled
                  icon-left="share"
                >
                  {{ $t("message.share.share") }}
                </b-button>
              </p>
              <p
                v-else
                class="control"
              >
                <b-button
                  v-if="selected == props.row"
                  type="is-primary"
                  outlined
                  size="is-small"
                  inverted
                  icon-left="share"
                  @click="
                    $router.push({
                      name: 'SharingView',
                      query: { container: props.row.name },
                    })
                  "
                >
                  {{ $t("message.share.share") }}
                </b-button>
                <b-button
                  v-else
                  type="is-primary"
                  outlined
                  size="is-small"
                  icon-left="share"
                  @click="
                    $router.push({
                      name: 'SharingView',
                      query: { container: props.row.name },
                    })
                  "
                >
                  {{ $t("message.share.share") }}
                </b-button>
              </p>
              <p class="control">
                <ReplicateContainerButton
                  v-if="selected == props.row"
                  :project="active.id"
                  :container="props.row.name"
                  :smallsize="true"
                  :disabled="!props.row.bytes ? true : false"
                  :inverted="true"
                />
                <ReplicateContainerButton
                  v-else
                  :project="active.id"
                  :container="props.row.name"
                  :disabled="!props.row.bytes ? true : false"
                  :smallsize="true"
                />
              </p>
              <p class="control">
                <b-button
                  type="is-primary"
                  outlined
                  size="is-small"
                  icon-left="pencil"
                  :inverted="selected == props.row ? true : false"
                  @click="toggleCreateFolderModal(props.row.name)"
                >
                  {{ $t("message.edit") }}
                </b-button>
              </p>
            </div>
          </template>
        </b-table-column>
        <b-table-column
          field="dangerous"
          label=""
          width="75"
        >
          <template #default="props">
            <DeleteContainerButton
              v-if="selected == props.row"
              :inverted="true"
              :objects="props.row.count"
              :container="props.row.name"
            />
            <DeleteContainerButton
              v-else
              class="control"
            >
              <b-button
                v-if="selected == props.row"
                type="is-primary"
                outlined
                size="is-small"
                inverted
                icon-left="share"
                @click="
                  $router.push({
                    name: 'SharingView',
                    query: { container: props.row.name },
                  })
                "
              >
                {{ $t("message.share.share") }}
              </b-button>
              <b-button
                v-else
                type="is-primary"
                outlined
                size="is-small"
                icon-left="share"
                @click="
                  $router.push({
                    name: 'SharingView',
                    query: { container: props.row.name },
                  })
                "
              >
                {{ $t("message.share.share") }}
              </b-button>
            </p>
          </div>
        </template>
      </b-table-column>
      <b-table-column width="75">
        <template #default="props">
          <FolderOptionsMenu
            :props="props"
            :selected="selected == props.row"
          />
        </template>
      </b-table-column>

      <template #empty>
        <p class="emptyTable">
          {{ $t("message.emptyProject") }}
        </p>
      </template>
    </b-table>
  </div>
</template>

<script>
import { getHumanReadableSize, truncate, tokenize } from "@/common/conv";
import debounce from "lodash/debounce";
import { liveQuery } from "dexie";
import { useObservable } from "@vueuse/rxjs";
import escapeRegExp from "lodash/escapeRegExp";
import SearchResultItem from "@/components/SearchResultItem";
import ContainerDownloadLink from "@/components/ContainerDownloadLink";
import CreateFolderModal from "@/components/CreateFolderModal";
import UploadModal from "@/components/UploadModal";
import FolderOptionsMenu from "../components/FolderOptionsMenu.vue";


export default {
  name: "ContainersView",
  components: {
    SearchResultItem,
    ContainerDownloadLink,
    CreateFolderModal,
    UploadModal,
    FolderOptionsMenu,
  },
  filters: {
    truncate,
  },
  data: function () {
    return {
      files: [],
      folders: [],
      selected: undefined,
      isPaginated: true,
      perPage: 15,
      defaultSortDirection: "asc",
      searchQuery: "",
      searchArray: [],
      currentPage: 1,
      shareModalIsActive: false,
      showTags: true,
      abortController: null,
      searchResults: [],
      containers: { value: [] },
      isSearching: false,
    };
  },
  computed: {
    active() {
      return this.$store.state.active;
    },
    openCreateFolderModal: {
      get() {
        return this.$store.state.openCreateFolderModal;
      },
      set() {},
    },
    openUploadModal: {
      get() {
        return this.$store.state.openUploadModal;
      },
      set() {},
    },
  },
  watch: {
    searchQuery: function (previousSearchQuery, newSearchQuery) {
      this.debounceSearch.cancel();
      // request parameter should be sanitized first
      const safeQuery = escapeRegExp(this.searchQuery);
      const query = safeQuery.trim();
      const newSearchArray = tokenize(query, 0);
      // Run debounced search every time the search box input changes
      if (newSearchArray.length > 0 && newSearchArray[0].length > 1) {
        if (previousSearchQuery.trim() !== newSearchQuery.trim()) {
          this.isSearching = true;
          this.searchArray = newSearchArray;
          this.debounceSearch();
        } else {
          this.isSearching = false;
        }
      } else {
        this.isSearching = false;
        this.searchResults = [];
        this.searchArray = [];
      }
    },
    active: function () {
      this.fetchContainers();
    },
    project: function () {
      this.fetchContainers();
    },
  },
  created: function () {
    // Lodash debounce to prevent the search execution from executing on
    // every keypress, thus blocking input
    this.debounceSearch = debounce(this.search, 400);
  },
  beforeMount() {
    this.abortController = new AbortController();
    this.getDirectCurrentPage();
  },
  mounted() {
    this.fetchContainers();
  },
  beforeDestroy() {
    this.abortController.abort();
  },
  methods: {
    fetchContainers: async function () {
      if (
        this.active.id === undefined &&
        this.$route.params.project === undefined
      ) {
        return;
      }
      this.containers = useObservable(
        liveQuery(() =>
          this.$store.state.db.containers
            .where({ projectID: this.$route.params.project })
            .toArray(),
        ),
      );
      await this.$store.dispatch("updateContainers", {
        projectID: this.$route.params.project,
        signal: null,
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
    getConAddr: function (container) {
      return this.$route.params.project + "/" + container;
    },
    getDirectCurrentPage: function () {
      this.currentPage = this.$route.query.page
        ? parseInt(this.$route.query.page)
        : 1;
    },
    addPageToURL: function (pageNumber) {
      // Add pagination current page number to the URL in query string
      this.$router.push("?page=" + pageNumber);
    },
    localHumanReadableSize: function (size) {
      // Make getHumanReadableSize usable in instance namespace
      return getHumanReadableSize(size);
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
    viewFolder(event) {
      // Prevent keyboard navigation from opening folder
      // when accessing row menu
      if (event.target.localName !== "c-menu") {
        this.$router.push(this.getConAddr(this.selected["name"]));
      }
    },
  },
};
</script>

<style scoped>
c-modal {
  position: relative;
  margin: 0 auto;
  display: inline-flex;
}

.containerTable {
  width: 90%;
  margin-left: 5%;
  margin-right: 5%;
}
.emptyTable {
  text-align: center;
  margin-top: 5%;
  margin-bottom: 5%;
}
.autocomplete {
  min-width: 30%;
  margin-left: auto;
}
.empty-search {
  height: 2rem;
}

</style>
