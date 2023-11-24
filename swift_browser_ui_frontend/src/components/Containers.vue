<template>
  <div class="contents">
    <c-row
      id="optionsbar"
      justify="space-between"
    >
      <SearchBox :containers="renderingContainers" />
      <div class="row-end">
        <c-button
          size="small"
          outlined
          data-testid="create-folder"
          @click="toggleCreateFolderModal(false)"
          @keyup.enter="toggleCreateFolderModal(true)"
        >
          <c-icon :path="mdiPlus" />
          {{ $t("message.createFolder") }}
        </c-button>
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
      </div>
    </c-row>
    <div id="cont-table-wrapper">
      <ContainerTable
        ref="containerTable"
        :conts="renderingContainers"
        :show-timestamp="showTimestamp"
        :disable-pagination="hidePagination"
        :hide-tags="hideTags"
        @delete-container="(cont) => removeContainer(cont)"
      />
      <c-loader v-show="contsLoading" />
    </div>
    <c-toasts
      id="container-toasts"
      data-testid="container-toasts"
    />
  </div>
</template>

<script>
import { liveQuery } from "dexie";
import { getDB } from "@/common/db";
import { useObservable } from "@vueuse/rxjs";
import { mdiPlus } from "@mdi/js";
import {
  getSharingContainers,
  updateObjectsAndObjectTags,
  toggleCreateFolderModal,
} from "@/common/globalFunctions";
import ContainerTable from "@/components/ContainerTable.vue";
import SearchBox from "@/components/SearchBox.vue";
import { setPrevActiveElement } from "@/common/keyboardNavigation";

export default {
  name: "ContainersView",
  components: {
    ContainerTable,
    SearchBox,
  },
  data: function () {
    return {
      mdiPlus,
      currentProject: {},
      showTimestamp: false,
      hidePagination: false,
      hideTags: false,
      selected: undefined,
      isPaginated: true,
      perPage: 15,
      direction: "asc",
      currentPage: 1,
      showTags: true,
      optionsKey: 1,
      abortController: null,
      containers: [],
      renderingContainers: [],
      containersToUpdateObjs: [],
      contsLoading: false,
    };
  },
  computed: {
    active() {
      return this.$store.state.active;
    },
    isFolderUploading() {
      return this.$store.state.isUploading;
    },
    isFolderCopied() {
      return this.$store.state.isFolderCopied;
    },
    newFolder() {
      return this.$store.state.newFolder;
    },
    locale() {
      return this.$i18n.locale;
    },
  },
  watch: {
    active: function () {
      this.fetchContainers(true);
    },
    currentProject: function() {
      const savedDisplayOptions = this.currentProject.displayOptions;
      if (savedDisplayOptions) {
        this.hideTags = savedDisplayOptions.hideTags;
        this.hidePagination = savedDisplayOptions.hidePagination;
        this.showTimestamp = savedDisplayOptions.showTimestamp;
        this.updateTableOptions();
      }
    },
    containers: function() {
      if (this.$route.name === "SharedFrom") {
        getSharingContainers(
          this.$route.params.project,
          this.abortController.signal,
        ).then(sharingContainers => {
          this.renderingContainers = this.containers.filter(
            cont => sharingContainers.some(item =>
              item === cont.name,
            ),
          );
        });
      }
      else if (this.$route.name === "SharedTo") {
        this.renderingContainers = this.containers ?
          this.containers.filter(cont => cont.owner) : [];
      } else {
        this.renderingContainers = this.containers;

        if (this.containers && this.newFolder) {
          const idx = this.containers.findIndex(c => c.name === this.newFolder);
          if (idx > 0) {
            this.containers.unshift(this.containers.splice(idx, 1)[0]);
            this.$refs.containerTable.toFirstPage();
          }
        }
      }
    },
    $route: function(to) {
      if (to.name !== "AllFolders") {
        this.$store.commit("setNewFolder", "");
      }
    },
    isFolderUploading: function () {
      if (!this.isFolderUploading) {
        this.contsLoading = true;
        setTimeout(() => {
          this.fetchContainers();
          this.contsLoading = false;
        }, 3000);
      }
    },
    isFolderCopied: function () {
      if (this.isFolderCopied) {
        this.fetchContainers();
        this.$store.commit("setFolderCopiedStatus", false);
      }
    },
    locale: function () {
      this.updateTableOptions();
    },
    containersToUpdateObjs: async function () {
      if (this.contsLoading) setTimeout(() => this.contsLoading = false, 100);
      await updateObjectsAndObjectTags(
        this.containersToUpdateObjs,
        this.active.id,
        this.abortController.signal,
      );
    },
  },
  created() {
    this.updateTableOptions();
  },
  beforeMount() {
    this.abortController = new AbortController();
    this.getDirectCurrentPage();
  },
  mounted() {
    this.fetchContainers(true);
  },
  beforeUnmount() {
    this.abortController.abort();
  },
  methods: {
    updateTableOptions: function () {
      const displayOptions = {
        showTimestamp: this.showTimestamp,
        hideTags: this.hideTags,
        hidePagination: this.renderFolders,
      };
      this.tableOptions = [
        {
          name: this.showTimestamp
            ? this.$t("message.tableOptions.fromNow")
            : this.$t("message.tableOptions.timestamp"),
          action: async () => {
            this.showTimestamp = !(this.showTimestamp);

            const newProject = {
              ...this.currentProject,
              displayOptions: {
                ...displayOptions,
                showTimestamp: this.showTimestamp,
              },
            };
            await getDB().projects.put(newProject);

            this.updateTableOptions();
          },
        },
        {
          name: this.hideTags
            ? this.$t("message.tableOptions.showTags")
            : this.$t("message.tableOptions.hideTags"),
          action: async () => {
            this.hideTags = !(this.hideTags);

            const newProject = {
              ...this.currentProject,
              displayOptions: {
                ...displayOptions,
                hideTags: this.hideTags,
              },
            };
            await getDB().projects.put(newProject);

            this.updateTableOptions();
          },
        },
        {
          name: this.hidePagination
            ? this.$t("message.tableOptions.showPagination")
            : this.$t("message.tableOptions.hidePagination"),
          action: async () => {
            this.hidePagination = !(this.hidePagination);

            const newProject = {
              ...this.currentProject,
              displayOptions: {
                ...displayOptions,
                hidePagination: this.hidePagination,
              },
            };
            await getDB().projects.put(newProject);
            this.updateTableOptions();
          },
        },
      ];
      this.optionsKey++;
    },
    fetchContainers: async function (withLoader = false) {
      if (this.active.id === undefined
        || this.abortController.signal?.aborted) {
        return;
      }
      if (withLoader) this.contsLoading = true;

      this.currentProject = await getDB().projects.get({
        id: this.active.id,
      });

      this.containersToUpdateObjs = await this.$store
        .dispatch("updateContainers", {
          projectID: this.active.id,
          signal: this.abortController.signal,
        });

      this.containers = useObservable(
        liveQuery(() =>
          getDB().containers
            .where({ projectID: this.active.id })
            .toArray(),
        ),
      );
    },
    removeContainer: async function(container) {
      await getDB().containers.where({
        projectID: this.active.id,
        name: container,
      }).delete();

      await getDB().containers.where({
        projectID: this.active.id,
        name: `${container}_segments`,
      }).delete();
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
    toggleCreateFolderModal: function (keypress) {
      toggleCreateFolderModal();
      if (keypress) {
        setPrevActiveElement();
      }
      setTimeout(() => {
        const newFolderInput = document
          .querySelector("#newFolder-input input");
        newFolderInput.tabIndex = "0";
        newFolderInput.focus();
      }, 300);
    },
  },
};
</script>

<style scoped>

#optionsbar {
  margin: 0.5em 0;
  background: #fff;
}

#cont-table-wrapper {
  position: relative;
}

.row-end {
  display: flex;
  flex-direction: row;
  gap: 1.5rem;
}
.row-end > * {
  align-self: center;
}

</style>
