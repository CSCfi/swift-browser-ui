<template>
  <div
    id="object-table"
  >
    <div class="folder-info">
      <div class="folder-info-heading">
        <div class="folder-name">
          <i class="mdi mdi-folder-outline" /> 
          <span>{{ container }}</span>
        </div>

        <c-button
          v-for="button in folderInfoButtons"
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

      <ul class="folder-details">
        <li>
          <b>{{ $t("message.share.sharedTo") }}: </b> N/A
        </li>
        <li>
          <b>{{ $t("message.table.created") }}: </b> N/A
        </li>
      </ul>
    </div>

    <c-row
      id="optionsbar"
      justify="space-between"
    >
      <c-text-field
        v-csc-model="searchQuery"
        :placeholder="$t('message.objects.filterBy')"
        shadow
      >
        <i class="mdi mdi-magnify" />
      </c-text-field>
      <c-menu
        :items.prop="tableOptions"
        options-testid="table-options-selector"
      >
        <span class="menu-active">Display options</span>
      </c-menu>
    </c-row>
    <CObjectTable
      :objs="oList.value"
      :disable-pagination="disablePagination"
      :hide-tags="hideTags"
      :render-folders="renderFolders"
    />
  </div>
</template>

<script>
import { getHumanReadableSize, truncate } from "@/common/conv";
import { modifyBrowserPageStyles } from "@/common/globalFunctions";
import { liveQuery } from "dexie";
import { useObservable } from "@vueuse/rxjs";
import CObjectTable from "@/components/CObjectTable";
import debounce from "lodash/debounce";
import escapeRegExp from "lodash/escapeRegExp";
// import ContainerDownloadLink from "@/components/ContainerDownloadLink";
// import ReplicateContainerButton from "@/components/ReplicateContainer";
// import DeleteObjectsButton from "@/components/ObjectDeleteButton";

export default {
  name: "ObjectTable",
  components: {
    CObjectTable,
    // ContainerDownloadLink,
    // ReplicateContainerButton,
    // DeleteObjectsButton,
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
      perPage: 15,
      defaultSortDirection: "asc",
      searchQuery: "",
      currentPage: 1,
      checkedRows: [],
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
    folderInfoButtons() {
      return [
        { label: this.$t("message.download"),
          icon: "mdi-download",
          action: (() => {
            const href = "/download/".concat(
              this.$route.params.project,
              "/",
              this.container);

            window.open(href, "_blank");
          }),
        },
        { label: this.$t("message.share.share"),
          icon: "mdi-share-variant",
          action: (() => this.$router.push({
            name: "SharingView",
            query: { container: this.container },
          })),
        },
        { label: "Options (placeholder)",
          icon: "mdi-dots-horizontal",
          action: (() => {}), 
        },
      ];
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
  },
  created: function () {
    // Lodash debounce to prevent the search execution from executing on
    // every keypress, thus blocking input
    this.debounceFilter = debounce(this.filter, 400);
    this.$store.commit("erasePrefix");
    this.tableOptions = [
      {
        name: "Render folders",
        action: () => {this.renderFolders = !(this.renderFolders);},
      },
      {
        name: "Hide tags",
        action: () => {this.hideTags = !(this.hideTags);},
      },
      {
        name: "Hide pagination",
        action: () => {this.disablePagination = !(this.disablePagination);},
      },
    ];
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
      this.filteredObjects = this.oList.value.reduce(search, []);
    },
    displayTags: function (name) {
      return this.showTags && !(this.renderFolders && !this.isFile(name));
    },
    getEditRoute: function(containerName, objectName) {
      if (this.$route.name == "SharedObjects") {
        return {
          name: "EditSharedObjectView",
          params: {
            container: containerName,
            object: objectName,
            owner: this.$route.params.owner,
          },
        };
      }
      return {
        name: "EditObjectView",
        params: {
          container: containerName,
          object: objectName,
        },
      };
    },
    toggleUploadModal: function () {
      this.$store.commit("toggleUploadModal", true);
      modifyBrowserPageStyles();
    },
  },
};
</script>

<style scoped lang="scss">
@import "@/css/prod.scss";
.object-table {
  margin-left: 5%;
  margin-right: 5%;
  margin-left: 5%;
  margin-right: 5%;
}

.folder-info {
  border: 1px solid $csc-primary;
  margin: 1rem 0rem;
}

.folder-info-heading, .folder-details {
  padding: 1rem 2rem; 
}

.folder-info-heading {
  display: flex;
  flex-wrap: wrap;
  justify-content: end;
  color: #FFF;
  font-size: 1rem;
  font-weight: 700;
  background: $csc-primary;
  align-items: center;

  & .folder-name {
    display: flex;
    flex: 1;
    & .mdi {
      font-size: 1.5rem;
      padding-right: .5rem
    }
    & span {
      align-self: center;
      display: inline-block;
    }
  }
  & c-button {
    flex: 0
  }
}

.folder-details {
  color: $csc-grey;

  & li {
    padding: .25rem 0;
  }
}

</style>
