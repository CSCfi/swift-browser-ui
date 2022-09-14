<template>
  <div
    id="object-table"
  >
    <c-row>
      <router-link
        class="back-link"
        :to="{
          name: 'AllFolders',
          params: {
            user: $store.state.uname,
            project: $store.state.active.id,
          }
        }"
      >
        <i class="mdi mdi-chevron-left" />
        Back to all folders
      </router-link>
    </c-row>

    <div class="folder-info">
      <div class="folder-info-heading">
        <i class="mdi mdi-folder-outline" />
        <span>{{ container }}</span>
      </div>

      <ul class="folder-details">
        <li>
          <b>{{ $t("message.share.sharedTo") }}: </b> N/A
        </li>
        <li>
          <b>{{ $t("message.table.created") }}: </b> N/A
        </li>
      </ul>
    </div>

    <div
      v-if="checkedRows.length"
      class="selection-bar"
    >
      <div class="info">
        <i class="mdi mdi-information-outline" />
        <span>
          {{ checkedRows.length }}
          {{ checkedRows.length === 1
            ? $t("message.table.itemSelected")
            : $t("message.table.itemsSelected") }}
        </span>
      </div>

      <div class="action-buttons">
        <c-button
          v-for="button in selectionActionButtons"
          :key="button.label"
          inverted
          text
          @click="button.action"
        >
          <i
            slot="icon"
            :class="button.icon"
            class="mdi"
          /> {{ button.label }}
        </c-button>
      </div>
    </div>

    <c-row
      id="optionsbar"
      justify="space-between"
    >
      <div class="search">
        <b-input
          v-model="searchQuery"
          :placeholder="$t('message.objects.filterBy')"
          type="search"
          icon="filter-variant"
        />
      </div>

      <c-menu
        :key="optionsKey"
        :items.prop="tableOptions"
        options-testid="table-options-selector"
      >
        <span class="menu-active display-options-menu">
          <i class="mdi mdi-tune" />
          {{ $t("message.tableOptions.displayOptions") }}
        </span>
      </c-menu>
    </c-row>

    <CObjectTable
      :objs="filteredObjects.length ? filteredObjects : oList.value"
      :disable-pagination="disablePagination"
      :hide-tags="hideTags"
      :render-folders="renderFolders"
      :checked-rows="checkedRows"
      @selected-rows="handleSelection"
      @delete-object="confirmDelete([$event])"
    />
  </div>
</template>

<script>
import { swiftDeleteObjects } from "@/common/api";
import { getHumanReadableSize, truncate } from "@/common/conv";
import { liveQuery } from "dexie";
import { useObservable } from "@vueuse/rxjs";
import CObjectTable from "@/components/CObjectTable";
import debounce from "lodash/debounce";
import escapeRegExp from "lodash/escapeRegExp";

export default {
  name: "ObjectTable",
  components: {
    CObjectTable,
  },
  filters: {
    truncate,
  },
  data: function () {
    return {
      oList: {value: []},
      selected: undefined,
      disablePagination: false,
      renderFolders: true,
      hideTags: false,
      searchQuery: "",
      currentPage: 1,
      checkedRows: [],
      optionsKey: 1,
      abortController: null,
      filteredObjects: [],
      inCurrentFolder: [],
    };
  },
  computed: {
    prefix () {
      return this.$route.query.prefix || "";
    },
    queryPage () {
      return this.$route.query.page || 1;
    },
    project () {
      return this.$route.params.project;
    },
    container () {
      return this.$route.params.container;
    },
    active () {
      return this.$store.state.active;
    },
    sharedObjects() {
      return this.$store.state.objectCache;
    },
    openCreateFolderModal() {
      return this.$store.state.openCreateFolderModal;
    },
    locale () {
      return this.$i18n.locale;
    },
  },
  watch: {
    active: function() {
      this.updateObjects();
    },
    searchQuery: function () {
      // Run debounced search every time the search box input changes
      this.debounceFilter();
    },
    renderFolders: function () {
      this.selected = undefined;
      this.checkedRows = [];
      if (this.renderFolders) {
        this.inCurrentFolder = this.getFolderContents();
      } else {
        this.inCurrentFolder = [];
        this.$route.query.prefix = "";
      }
    },
    sharedObjects: function () {
      if(this.$route.name !== "SharedObjects") {
        return;
      }
      this.oList = {value: this.sharedObjects};
    },
    prefix: function () {
      if (this.renderFolders) {
        this.inCurrentFolder = this.getFolderContents();
        this.$store.commit("setPrefix", this.prefix);
      }
    },
    queryPage: function () {
      this.currentPage = this.queryPage;
    },
    ["oList.value"]: async function() {
      if (this.oList.value !== undefined && this.$route.query.selected) {
        const selected = this.$route.query.selected;
        const obj = this.oList.value.find(o => {
          return o.name === selected;
        });
        if (obj) {
          this.selected = obj;
        }
      }
    },
    locale () {
      this.setLocalizedContent();
    },
  },
  created: function () {
    // Lodash debounce to prevent the search execution from executing on
    // every keypress, thus blocking input
    this.debounceFilter = debounce(this.filter, 400);
    this.$store.commit("erasePrefix");
    this.setLocalizedContent();
    this.set;
  },
  beforeMount () {
    this.abortController = new AbortController();
    this.getDirectCurrentPage();
    this.checkLargeDownloads();
  },
  mounted () {
    this.updateObjects();
  },
  beforeDestroy () {
    this.abortController.abort();
  },
  methods: {
    updateObjects: async function () {
      if (
        this.container === undefined
        || (
          this.active.id === undefined
          && this.$route.params.project
        )
      ) {
        return;
      }

      if(this.$route.name === "SharedObjects") {
        await this.$store.dispatch(
          "updateSharedObjects",
          {
            project: this.$route.params.project,
            owner: this.$route.params.owner,
            container: {
              id: 0,
              name: this.$route.params.container,
            },
            signal: this.abortController.signal,
          },
        );
        return;
      }

      const container = await this.$store.state.db.containers
        .get({
          projectID: this.$route.params.project,
          name: this.container,
        });
      this.oList = useObservable(
        liveQuery(() =>
          this.$store.state.db.objects
            .where({"containerID": container.id})
            .toArray(),
        ),
      );
      this.$store.dispatch(
        "updateObjects",
        {
          projectID: this.$route.params.project,
          container: container,
          signal: this.abortController.signal,
        },
      );
    },
    isRowCheckable: function (row) {
      return this.renderFolders ? this.isFile(row.name) : true;
    },
    checkLargeDownloads: function () {
      if (document.cookie.match("ENA_DL")) {
        this.allowLargeDownloads = true;
      }
    },
    addPageToURL: function (pageNumber) {
      if (this.$route.name == "SharedObjects") {
        this.$router.push({
          name: "SharedObjects",
          params: {
            project: this.$route.params.project,
            owner: this.$route.params.owner,
            container: this.$route.params.container,
          },
          query: {
            page: pageNumber,
            prefix: this.getPrefix(),
          },
        });
      } else {
        this.$router.push({
          name: "ObjectsView",
          params: {
            user: this.$route.params.user,
            project: this.$route.params.project,
            container: this.$route.params.container,
          },
          query: {
            page: pageNumber,
            prefix: this.getPrefix(),
          },
        });
      }
    },
    confirmDownload: function () {
      // Snackbar for enabling large downloads for the duration of the
      // session
      this.$buefy.snackbar.open({
        duration: 5000,
        message: this.$t("message.largeDownMessage"),
        type: "is-success",
        position: "is-top",
        actionText: this.$t("message.largeDownAction"),
        onAction: this.enableDownload,
      });
    },
    enableDownload: function () {
      // Enables large downloads upon execution
      this.allowLargeDownloads = true;
      const expiryDate = new Date();
      expiryDate.setMonth(expiryDate.getMonth() + 1);
      document.cookie = "ENA_DL=" +
        this.allowLargeDownloads +
        "; path=/; expires=" +
        expiryDate.toUTCString();
    },
    getDirectCurrentPage: function () {
      this.currentPage = this.$route.query.page ?
        parseInt(this.$route.query.page) :
        1;
    },
    // Make human readable translation functions available in instance
    // namespace
    localHumanReadableSize: function ( size ) {
      return getHumanReadableSize( size );
    },
    getHumanReadableDate: function ( val ) {
      let dateVal = new Date(val);
      let langLocale = "en-GB";
      var options = {
        weekday: "short",
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      };
      var zone = { timeZone: "EEST" };
      switch (this.$i18n.locale) {
        case "en":
          langLocale = "en-GB";
          break;
        case "fi":
          langLocale = "fi-FI";
          break;
        default:
          langLocale = "en-GB";
      }
      return dateVal.toLocaleDateString(langLocale, options, zone);
    },
    getFolderContents: function () {
      // Get folderized list of the objects
      // request parameter should be sanitized first
      var safeKey = escapeRegExp(this.getPrefix());
      let pre_re = new RegExp(safeKey);

      let tmpList = this.oList.value.filter(
        el => el.name.match(pre_re),
      );

      let idList = [];
      let folders = new Set();

      tmpList.forEach(element => {
        let folderName = this.getFolderName(element.name);

        if (folders.has(folderName)) {
          return;
        }
        folders.add(folderName);
        idList.push(element.id);
      });

      return idList;
    },
    getPrefix: function () {
      // Get current pseudofolder prefix
      if (this.$route.query.prefix == undefined) {
        return "";
      }
      return this.$route.query.prefix;
    },
    changeFolder: function (folder) {
      // Change currently displayed pseudofolder
      if (this.$route.name == "SharedObjects") {
        this.$router.push({
          name: "SharedObjects",
          params: {
            project: this.$route.params.project,
            owner: this.$route.params.owner,
            container: this.$route.params.container,
          },
          query: {
            page: this.pageNumber,
            prefix: this.getPrefix().concat(folder, "/"),
          },
        });
      } else {
        this.$router.push({
          name: "ObjectsView",
          params: {
            project: this.$route.params.project,
            owner: this.$route.params.owner,
            container: this.$route.params.container,
          },
          query: {
            page: this.pageNumber,
            prefix: this.getPrefix().concat(folder, "/"),
          },
        });
      }

      this.inCurrentFolder = this.getFolderContents();
    },
    getFolderName: function (path) {
      // Get the name of the currently displayed pseudofolder
      let endregex = new RegExp("/.*$");
      return path.replace(this.getPrefix(), "").replace(endregex, "");
    },
    isFile: function (path) {
      // Return true if path represents a file in the active prefix context
      return path.replace(this.getPrefix(), "").match("/") ? false : true;
    },
    isVisible: function(id) {
      let visible = true;
      if (
        this.renderFolders
        && !this.inCurrentFolder.includes(id)
      ) {
        visible = false;
      }
      if (this.filteredObjects.includes(id)) {
        visible = false;
      }
      return visible;
    },
    filter: function () {
      if(this.searchQuery.length === 0) {
        this.filteredObjects = [];
        return;
      }
      // request parameter should be sanitized first
      var safeKey = escapeRegExp(this.searchQuery);
      var name_re = new RegExp(safeKey, "i");
      function search (prev, element) {
        if (
          element.name.match(name_re) ||
          (
            element.tags &&
            element.tags.join("\n").match(name_re)
          )
        ) {
          return prev;
        }
        prev.push(element.id);
        return prev;
      }

      const filteredObjectsIds = this.oList.value.reduce(search, []);

      this.filteredObjects = this.oList.value.
        filter(obj => filteredObjectsIds.indexOf(obj.id) === -1);
    },
    displayTags: function (name) {
      return this.showTags && !(this.renderFolders && !this.isFile(name));
    },
    confirmDelete: function (deletables) {
      this.$buefy.dialog.confirm({
        title: this.$t("message.objects.deleteObjects"),
        message: this.$t("message.objects.deleteObjectsMessage"),
        confirmText: this.$t("message.objects.deleteConfirm"),
        type: "is-danger",
        hasIcon: true,
        onConfirm: () => {this.deleteObjects(deletables);},
      });
    },
    deleteObjects: function (deletables) {
      this.clearSelections();
      this.$buefy.toast.open({
        message: this.$t("message.objects.deleteSuccess"),
        type: "is-success",
      });
      let to_remove = new Array;
      if (typeof(deletables) == "string") {
        to_remove.push(deletables);
      } else {
        for (let object of deletables) {
          to_remove.push(object.name);
        }
      }
      if(this.$route.name !== "SharedObjects") {
        const objIDs = deletables.reduce(
          (prev, obj) => [...prev, obj.id], [],
        );
        this.$store.state.db.objects.bulkDelete(objIDs);
      }
      swiftDeleteObjects(
        this.$route.params.project,
        this.$route.params.container,
        to_remove,
      ).then(async () => {
        if (this.$route.name === "SharedObjects") {
          await this.$store.dispatch(
            "updateSharedObjects",
            {
              project: this.$route.params.project,
              container: {
                name: this.$route.params.container,
                id: 0,
              },
            },
          );
        }
      });
    },
    handleSelection(selection) {
      const objects = this.oList.value;
      this.checkedRows = objects.filter(
        item => selection.indexOf(item.name) > -1,
      );
    },
    clearSelections() {
      const dataTable = document.getElementById("objtable");
      dataTable.clearSelections();
    },
    setTableOptionsMenu() {
      this.tableOptions = [
        {
          name: this.renderFolders
            ? this.$t("message.tableOptions.text")
            : this.$t("message.tableOptions.render"),
          action: () => {
            this.renderFolders = !(this.renderFolders);
            this.setTableOptionsMenu();
          },
        },
        {
          name: this.hideTags
            ? this.$t("message.tableOptions.showTags")
            : this.$t("message.tableOptions.hideTags"),
          action: () => {
            this.hideTags = !(this.hideTags);
            this.setTableOptionsMenu();
          },
        },
        {
          name: this.disablePagination
            ? this.$t("message.tableOptions.showPagination")
            : this.$t("message.tableOptions.hidePagination"),
          action: () => {
            this.disablePagination = !(this.disablePagination);
            this.setTableOptionsMenu();
          },
        },
      ];
      this.optionsKey++;
    },
    setSelectionActionButtons() {
      this.selectionActionButtons = [
        {
          label: this.$t("message.table.deleteSelected"),
          icon: "mdi-trash-can-outline",
          action: () => this.confirmDelete(this.checkedRows),
        },
        {
          label: this.$t("message.table.clearSelected"),
          icon: "mdi-refresh",
          action: () => this.clearSelections(),
        },
      ];
    },
    setLocalizedContent() {
      this.setTableOptionsMenu();
      this.setSelectionActionButtons();
    },
  },
};
</script>

<style scoped lang="scss">
@import "@/css/prod.scss";

.back-link {
  display: flex;
  padding-bottom: .5rem;
  color: $csc-primary;
  font-weight: 600;
  align-items: center;

  & .mdi {
    font-size: 2rem;
  }
}

.folder-info {
  border: 1px solid $csc-primary;
  margin: 0rem 0rem;
}

.folder-info-heading, .folder-details {
  padding: 1rem 2rem;
}

.folder-info-heading {
  display: flex;
  color: #FFF;
  font-size: 1rem;
  font-weight: 700;
  background: $csc-primary;
  align-items: center;
  & .mdi {
    font-size: 1.5rem;
    padding-right: .5rem
  }
  & span {
    align-self: center;
    display: inline-block;
  }
}

.folder-details {
  color: $csc-grey;

  & li {
    padding: .25rem 0;
  }
}

.selection-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  color: #FFF;
  background: $csc-blue;
  border-radius: .25rem;
  padding: 0 1rem;
  margin: 1.5rem 0 0;
  position: sticky;
  top: 0;
  z-index: 10;

  & .info {
    display: flex;
    flex: 1;
    min-width: 12rem;
    padding: 1rem;
    & .mdi {
      font-size: 1.5rem;
      padding-right: .5rem
    }
    & span {
      align-self: center;
      display: inline-block;
    }
  }

  & .action-buttons {
    display: flex;
    flex: 0;
    padding: .5rem 0;
  }
}

</style>
