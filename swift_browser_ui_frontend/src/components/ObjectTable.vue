<template>
  <div
    id="object-table"
  >
    <BreadcrumbNav />
    <div class="folder-info">
      <div class="folder-info-heading">
        <i class="mdi mdi-folder-outline" />
        <span>{{ containerName }}</span>
      </div>
      <ul class="folder-details">
        <li>
          <b>{{ $t("message.table.shared_status") }}: </b>
          {{ sharedStatus }}&nbsp;
          <c-link
            v-show="!isSharedFolder"
            underline
            tabindex="0"
            @click="toggleShareModal"
            @keydown.enter="toggleShareModal"
          >
            {{ $t("message.table.edit_sharing") }}
          </c-link>
        </li>
        <li v-show="isSharedFolder">
          <b>{{ $t("message.table.source_project_id") }}: </b>
          {{ ownerProject }}
        </li>
        <li v-show="isSharedFolder">
          <b>{{ $t("message.table.date_of_sharing") }}: </b>
          {{ dateOfSharing }}
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
          @keyup.enter="button.action"
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
      <c-text-field
        id="search"
        v-model="searchQuery"
        v-csc-control
        name="search"
        :placeholder="$t('message.objects.filterBy')"
        type="search"
      >
        <i
          slot="pre"
          class="mdi mdi-filter-variant mdi-24px"
        />
      </c-text-field>
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
      :objs="filteredObjects.length ? filteredObjects : oList"
      :disable-pagination="hidePagination"
      :hide-tags="hideTags"
      :render-folders="renderFolders"
      :checked-rows="checkedRows"
      @selected-rows="handleSelection"
      @delete-object="confirmDelete"
    />
    <c-toasts
      id="objects-toasts"
      data-testid="objects-toasts"
    />
    <c-toasts
      id="largeDownload-toasts"
      data-testid="largeDownload-toasts"
    >
      <p>{{ $t("message.largeDownMessage") }}</p>
      <c-button
        text
        @click="removeToast"
      >
        {{ $t("message.largeDownAction") }}
      </c-button>
    </c-toasts>
  </div>
</template>

<script>
import {
  getHumanReadableSize,
  truncate,
  parseDateTime,
} from "@/common/conv";
import {
  getSharedContainers,
  getAccessDetails,
  toggleDeleteModal,
  isFile,
} from "@/common/globalFunctions";
import { getDB } from "@/common/db";
import { liveQuery } from "dexie";
import { useObservable } from "@vueuse/rxjs";
import CObjectTable from "@/components/CObjectTable.vue";
import debounce from "lodash/debounce";
import escapeRegExp from "lodash/escapeRegExp";
import BreadcrumbNav from "@/components/BreadcrumbNav.vue";
import { toRaw } from "vue";

export default {
  name: "ObjectTable",
  components: {
    CObjectTable,
    BreadcrumbNav,
  },
  filters: {
    truncate,
  },
  data: function () {
    return {
      isSharingFolder: false,
      isSharedFolder: false,
      sharedStatus: "",
      sharedContainers: [],
      ownerProject: "",
      dateOfSharing: "",
      oList: [],
      selected: undefined,
      hidePagination: false,
      renderFolders: true,
      hideTags: false,
      searchQuery: "",
      currentPage: 1,
      checkedRows: [],
      optionsKey: 1,
      abortController: null,
      filteredObjects: [],
      inCurrentFolder: [],
      tableOptions: [],
      currentContainer: {},
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
    containerName () {
      return this.$route.params.container;
    },
    client () {
      return this.$store.state.client;
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
    active: async function() {
      await this.getSharedContainers();
      await this.getFolderSharedStatus();
      await this.updateObjects();
    },
    client: async function() {
      await this.getSharedContainers();
      await this.getFolderSharedStatus();
      await this.updateObjects();
    },
    searchQuery: function () {
      // Run debounced search every time the search box input changes
      this.debounceFilter();
    },
    sharedObjects: function () {
      if(this.$route.name !== "SharedObjects") {
        return;
      }
      this.oList = this.sharedObjects;
    },
    queryPage: function () {
      this.currentPage = this.queryPage;
    },
    currentContainer: function() {
      const savedDisplayOptions = this.currentContainer.displayOptions;
      if (savedDisplayOptions) {
        this.renderFolders = savedDisplayOptions.renderFolders;
        this.hideTags = savedDisplayOptions.hideTags;
        this.hidePagination = savedDisplayOptions.hidePagination;
        this.setTableOptionsMenu();
      }
    },
    oList: function() {
      if (this.oList !== undefined && this.$route.query.selected) {
        const selected = this.$route.query.selected;
        const obj = this.oList.find(o => {
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
  async mounted () {
    await this.getSharedContainers();
    await this.getFolderSharedStatus();
    this.updateObjects();
  },
  beforeUnmount () {
    this.abortController.abort();
  },
  methods: {
    getSharedContainers: async function () {
      this.sharedContainers = await getSharedContainers(this.active.id);
    },
    getFolderSharedStatus: async function() {
      if (this.client) {
        await this.client.getShareDetails(
          this.project,
          this.containerName,
        ).then(
          async (ret) => {
            if (ret.length > 0) {
              this.isSharingFolder = true;
              ret.length === 1
                ? this.sharedStatus
                  = this.$t("message.folderDetails.sharing_to_one_project")
                : this.sharedStatus
                  = this.$t("message.folderDetails.sharing_to_many_projects");
            }
            else if (ret.length === 0) {
              if (this.sharedContainers.findIndex(
                cont => cont.container === this.containerName) > -1) {
                this.isSharedFolder = true;
                const sharedDetails
                  = await getAccessDetails(
                    this.project,
                    this.containerName,
                    this.$route.params.owner,
                  );

                const accessRights = sharedDetails.access;
                if (accessRights.length === 1) {
                  this.sharedStatus
                    = this.$t("message.folderDetails.shared_with_read");
                }
                else if (accessRights.length > 1) {
                  this.sharedStatus
                    = this.$t("message.folderDetails.shared_with_read_write");
                }
                this.ownerProject = sharedDetails.owner;
                this.dateOfSharing =
                  parseDateTime(this.locale, sharedDetails.sharingDate, true);
              }
              else this.sharedStatus
                = this.$t("message.folderDetails.notShared");
            }
          },
        );
      }
    },
    toggleShareModal: function () {
      this.$store.commit("toggleShareModal", true);
      this.$store.commit("setFolderName", this.containerName);
    },
    confirmDelete: function(item) {
      if (isFile(item.name, this.$route)) {
        toggleDeleteModal([item]);
      } else {
        document.querySelector("#container-error-toasts").addToast(
          {
            progress: false,
            type: "error",
            duration: 30000,
            message: this.$t("message.container_ops.deleteNote"),
          });
      }
    },
    updateObjects: async function () {
      if (
        this.containerName === undefined
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

      this.currentContainer = await getDB().containers
        .get({
          projectID: this.$route.params.project,
          name: this.containerName,
        });

      this.oList = useObservable(
        liveQuery(() =>
          getDB().objects
            .where({"containerID": this.currentContainer.id})
            .toArray(),
        ),
      );

      this.$store.dispatch(
        "updateObjects",
        {
          projectID: this.$route.params.project,
          container: this.currentContainer,
          signal: this.abortController.signal,
        },
      );
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
    removeToast: function() {
      this.enableDownload();
      document.querySelector("#largeDownload-toasts")
        .removeToast("largeDownload");
    },
    confirmDownload: function () {
      document.querySelector("#largeDownload-toasts").addToast(
        { type: "info",
          message: "",
          id: "largeDownload",
          progress: false,
          custom: true },
      );
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
    getPrefix: function () {
      // Get current pseudofolder prefix
      if (this.$route.query.prefix == undefined) {
        return "";
      }
      return this.$route.query.prefix;
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

      const filteredObjectsIds = this.oList.reduce(search, []);

      this.filteredObjects = this.oList.
        filter(obj => filteredObjectsIds.indexOf(obj.id) === -1);
    },
    handleSelection(selection) {
      const objects = this.oList;
      this.checkedRows = objects.filter(
        item => selection.indexOf(item.name) > -1,
      );

      /* Subfolders should also be selected and then filtered out from
        deletableObjects later
      */
      if (this.checkedRows.length < selection.length) {
        for (let i = 0; i < selection.length; i++) {
          if(!this.checkedRows.some(row => row && row.name === selection[i])) {
            const obj = objects.find(obj => !this.checkedRows.some(row => row.name === selection[i]) && obj.name.includes(`${selection[i]}/`));
            this.checkedRows.push(obj);
          }
        }
      }
    },
    clearSelections() {
      const dataTable = document.getElementById("objtable");
      dataTable.clearSelections();
    },
    setTableOptionsMenu() {
      const renderFolders = toRaw(this.renderFolders);
      const hideTags = toRaw(this.hideTags);
      const hidePagination = toRaw(this.hidePagination);
      const currentContainer = toRaw(this.currentContainer);
      const displayOptions = {
        renderFolders: renderFolders,
        hideTags: hideTags,
        hidePagination: hidePagination,
      };

      this.tableOptions = [
        {
          name: this.renderFolders
            ? this.$t("message.tableOptions.text")
            : this.$t("message.tableOptions.render"),
          action: async () => {
            this.renderFolders = !(this.renderFolders);
            const renderFolders = toRaw(this.renderFolders);

            const newContainer = {
              ...currentContainer,
              displayOptions: {...displayOptions, renderFolders}};
            await getDB().containers.put(newContainer);

            this.setTableOptionsMenu();
          },
        },
        {
          name: this.hideTags
            ? this.$t("message.tableOptions.showTags")
            : this.$t("message.tableOptions.hideTags"),
          action: async () => {
            this.hideTags = !(this.hideTags);
            const hideTags = toRaw(this.hideTags);

            const newContainer = {
              ...currentContainer,
              displayOptions: { ...displayOptions, hideTags}};
            await getDB().containers.put(newContainer);

            this.setTableOptionsMenu();
          },
        },
        {
          name: this.hidePagination
            ? this.$t("message.tableOptions.showPagination")
            : this.$t("message.tableOptions.hidePagination"),
          action: async () => {
            this.hidePagination = !(this.hidePagination);
            const hidePagination = toRaw(this.hidePagination);

            const newContainer = {
              ...currentContainer,
              displayOptions: {
                ...displayOptions, hidePagination}};
            await getDB().containers.put(newContainer);

            this.setTableOptionsMenu();
          },
        },
      ];

      this.optionsKey++;
    },
    setSelectionActionButtons() {
      this.selectionActionButtons = [
        {
          label: this.$t("message.table.clearSelected"),
          icon: "mdi-refresh",
          action: () => this.clearSelections(),
        },
        {
          label: this.$t("message.table.deleteSelected"),
          icon: "mdi-trash-can-outline",
          action: () => toggleDeleteModal(this.checkedRows),
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

#search {
  flex: 0.4;
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

#objects-toasts {
  bottom: 40vh;
}
</style>
