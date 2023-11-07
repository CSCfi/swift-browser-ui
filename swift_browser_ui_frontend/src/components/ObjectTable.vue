<template>
  <div
    id="object-table"
  >
    <BreadcrumbNav @breadcrumbClicked="breadcrumbClickHandler" />
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
            v-show="!owner"
            underline
            tabindex="0"
            @click="toggleShareModal"
            @keydown.enter="toggleShareModal"
          >
            {{ $t("message.table.edit_sharing") }}
          </c-link>
        </li>
        <li v-show="owner">
          <b>{{ $t("message.table.source_project_id") }}: </b>
          {{ ownerProject }}
        </li>
        <li v-show="owner">
          <b>{{ $t("message.table.date_of_sharing") }}: </b>
          {{ dateOfSharing }}
        </li>
      </ul>
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
          :id="`${button.label.toLowerCase()}-selections`"
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
    <div id="obj-table-wrapper">
      <CObjectTable
        :breadcrumb-clicked-prop="breadcrumbClicked"
        :objs="filtering ? filteredObjects : oList"
        :disable-pagination="hidePagination"
        :hide-tags="hideTags"
        :render-folders="renderFolders"
        :show-timestamp="showTimestamp"
        :access-rights="accessRights"
        :no-data-text="filtering ?
          $t('message.search.empty') : $t('message.emptyContainer')"
        @selected-rows="handleSelection"
        @delete-object="confirmDelete"
      />
      <c-loader v-show="objsLoading" />
    </div>
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
  updateObjectsAndObjectTags,
} from "@/common/globalFunctions";
import {
  setPrevActiveElement,
  disableFocusOutsideModal,
  addFocusClass,
} from "@/common/keyboardNavigation";
import { getDB } from "@/common/db";
import { liveQuery } from "dexie";
import { useObservable } from "@vueuse/rxjs";
import CObjectTable from "@/components/CObjectTable.vue";
import { debounce, escapeRegExp } from "lodash";
import BreadcrumbNav from "@/components/BreadcrumbNav.vue";
import { toRaw } from "vue";
import { DEV } from "@/common/conv";

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
      accessRights: [],
      sharedStatus: "",
      sharedContainers: [],
      ownerProject: "",
      dateOfSharing: "",
      oList: [],
      showTimestamp: false,
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
      breadcrumbClicked: false,
      objsLoading: false,
      filtering: false,
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
    openCreateFolderModal() {
      return this.$store.state.openCreateFolderModal;
    },
    locale () {
      return this.$i18n.locale;
    },
    isFolderUploading() {
      return this.$store.state.isUploading;
    },
    owner() {
      return this.$route.params.owner;
    },
    shareModal() {
      return this.$store.state.openShareModal;
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
    queryPage: function () {
      this.currentPage = this.queryPage;
    },
    currentContainer: async function() {
      if (this.currentContainer === undefined) return;
      const savedDisplayOptions = toRaw(this.currentContainer.displayOptions);
      if (savedDisplayOptions) {
        this.renderFolders = savedDisplayOptions.renderFolders;
        this.showTimestamp = savedDisplayOptions.showTimestamp;
        this.hideTags = savedDisplayOptions.hideTags;
        this.hidePagination = savedDisplayOptions.hidePagination;
        this.setTableOptionsMenu();
      }
    },
    locale () {
      this.setLocalizedContent();
      this.getFolderSharedStatus();
    },
    isFolderUploading: function () {
      if (!this.isFolderUploading) {
        setTimeout(async () => {
          this.updateAfterUpload();
        }, 3000);
      }
    },
    shareModal: async function(){
      if (!this.shareModal) await this.getFolderSharedStatus();
    },
    oList() {
      if (this.objsLoading) setTimeout(() => this.objsLoading = false, 100);
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
    this.objsLoading = true;
    await this.getSharedContainers();
    await this.getFolderSharedStatus();
    this.updateObjects();
  },
  beforeUnmount () {
    this.abortController.abort();
  },
  updated () {
    if (this.breadcrumbClicked) this.breadcrumbClicked = false;
  },
  methods: {
    breadcrumbClickHandler(value) {
      this.breadcrumbClicked = value;
    },
    getSharedContainers: async function () {
      this.sharedContainers =
        await getSharedContainers(this.active.id, this.abortController.signal);
    },
    getFolderSharedStatus: async function() {
      if (this.client) {
        await this.client.getShareDetails(
          this.project,
          this.containerName,
          this.abortController.signal,
        ).then(
          async (ret) => {
            if (ret.length > 0) {
              ret.length === 1
                ? this.sharedStatus
                  = this.$t("message.folderDetails.sharing_to_one_project")
                : this.sharedStatus
                  = this.$t("message.folderDetails.sharing_to_many_projects");
            }
            else if (ret.length === 0) {
              if (this.sharedContainers.findIndex(
                cont => cont.container === this.containerName) > -1) {

                const sharedDetails
                  = await getAccessDetails(
                    this.project,
                    this.containerName,
                    this.owner,
                    this.abortController.signal,
                  );

                this.accessRights = sharedDetails.access;
                switch (this.accessRights.length) {
                  case 0:
                    this.sharedStatus
                      = this.$t("message.folderDetails.shared_with_view");
                    break;
                  case 1:
                    this.sharedStatus
                      = this.$t("message.folderDetails.shared_with_read");
                    break;
                  case 2:
                    this.sharedStatus
                      = this.$t("message.folderDetails.shared_with_read_write");
                    break;
                }
                this.ownerProject = sharedDetails.owner;
                this.dateOfSharing =
                  parseDateTime(
                    this.locale, sharedDetails.sharingDate, this.$t, true);
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
    confirmDelete: function(item, keypress) {
      if (isFile(item.name, this.$route) || !this.renderFolders) {
        toggleDeleteModal([item]);
        if (keypress) this.moveFocusToDeleteModal();
      } else {
        document.querySelector("#container-error-toasts").addToast(
          {
            progress: false,
            type: "error",
            duration: 6000,
            message: this.$t("message.subfolders.deleteNote"),
          });
      }
    },
    getCurrentContainer: function () {
      return getDB().containers
        .get({
          projectID: this.project,
          name: this.containerName,
        });
    },
    updateAfterUpload: async function () {
      const containersToUpdateObjs = {
        key: this.currentContainer.id,
        container: {...this.currentContainer},
      };

      await updateObjectsAndObjectTags(
        [containersToUpdateObjs],
        this.active.id,
        this.abortController.signal,
        false, // No need to update object tags in this case
      );
    },
    updateObjects: async function () {
      if (
        this.containerName === undefined
        || (
          this.active.id === undefined
          && this.project
        )
      ) {
        return;
      }

      this.currentContainer = await this.getCurrentContainer();

      if (this.currentContainer === undefined) {
        //container not in DB when clicking "view destination"
        // while / right after uploading
        await this.$store.dispatch("updateContainers", {
          projectID: this.active.id,
          signal: this.abortController.signal,
        });
        this.currentContainer = await this.getCurrentContainer();
        if (this.currentContainer === undefined) {
          if (DEV) console.log("Error with uploaded container");
          return;
        }
        await this.updateAfterUpload();
      }
      else {
        let params = {
          projectID: this.project,
          container: this.currentContainer,
          signal: this.abortController.signal,
        };

        if (this.owner) params.owner = this.owner;

        await this.$store.dispatch("updateObjects", params);
      }

      this.oList = useObservable(
        liveQuery(() =>
          getDB().objects
            .where({"containerID": this.currentContainer.id})
            .toArray(),
        ),
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
            owner: this.owner,
            container: this.containerName,
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
            project: this.project,
            container: this.containerName,
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
        this.filtering = false;
        this.filteredObjects = [];
        return;
      }
      this.filtering = true;
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
        prev.push(element.name);
        return prev;
      }

      const filteredNames = this.oList.reduce(search, []);

      this.filteredObjects = this.oList.
        filter(obj => filteredNames.indexOf(obj.name) === -1);
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
      const dataTable = document.getElementById("obj-table");
      dataTable.clearSelections();
    },
    setTableOptionsMenu() {
      this.$store.commit("toggleRenderedFolders", this.renderFolders);
      const displayOptions = {
        renderFolders: this.renderFolders,
        showTimestamp: this.showTimestamp,
        hideTags: this.hideTags,
        hidePagination: this.hidePagination,
      };

      this.tableOptions = [
        {
          name: this.renderFolders
            ? this.$t("message.tableOptions.text")
            : this.$t("message.tableOptions.render"),
          action: async () => {
            this.renderFolders = !(this.renderFolders);

            const newContainer = {
              ...toRaw(this.currentContainer),
              displayOptions: {
                ...displayOptions, renderFolders: this.renderFolders }};
            await getDB().containers.put(newContainer);

            this.setTableOptionsMenu();
          },
        },
        {
          name: this.showTimestamp
            ? this.$t("message.tableOptions.fromNow")
            : this.$t("message.tableOptions.timestamp"),
          action: async () => {
            this.showTimestamp = !(this.showTimestamp);

            const newContainer = {
              ...toRaw(this.currentContainer),
              displayOptions: {
                ...displayOptions, showTimestamp: this.showTimestamp }};
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

            const newContainer = {
              ...toRaw(this.currentContainer),
              displayOptions: {
                ...displayOptions, hideTags: this.hideTags }};
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

            const newContainer = {
              ...toRaw(this.currentContainer),
              displayOptions: {
                ...displayOptions, hidePagination: this.hidePagination }};
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
          action: () => {
            this.onOpenDeleteModal(this.checkedRows);
            const deleteSelectionsBtn = document
              .querySelector("#delete-selections");
            deleteSelectionsBtn.addEventListener("keydown", (e) =>{
              if (e.keyCode === 13) {
                this.onOpenDeleteModal(this.checkedRows, true);
              }
            });
          },
        },
      ];
    },
    setLocalizedContent() {
      this.setTableOptionsMenu();
      this.setSelectionActionButtons();
    },
    onOpenDeleteModal(checkedRows, keypress) {
      toggleDeleteModal(checkedRows);
      if (keypress) this.moveFocusToDeleteModal();
    },
    moveFocusToDeleteModal() {
      const deleteObjsModal = document.getElementById("delete-objs-modal");
      setPrevActiveElement();
      disableFocusOutsideModal(deleteObjsModal);

      setTimeout(() => {
        const deleteObjsBtn = document.getElementById("delete-objs-btn");
        deleteObjsBtn.tabIndex = "0";
        deleteObjsBtn.focus();
        addFocusClass(deleteObjsBtn);
      }, 300);
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
  color: $csc-dark;

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

#obj-table-wrapper {
  position: relative;
}

</style>
