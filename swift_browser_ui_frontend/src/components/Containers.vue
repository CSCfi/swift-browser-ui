<template>
  <div class="contents">
    <c-row
      id="optionsbar"
      justify="space-between"
    >
      <SearchBox :containers="renderingContainers" />
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
    <ContainerTable
      :conts="renderingContainers"
      :disable-pagination="hidePagination"
      :hide-tags="hideTags"
      @delete-container="(cont) => removeContainer(cont)"
    />
    <c-toasts
      id="container-toasts"
      data-testid="container-toasts"
    />
  </div>
</template>

<script>
import { liveQuery } from "dexie";
import { delay } from "lodash";
import { getDB } from "@/common/db";
import { useObservable } from "@vueuse/rxjs";
import { getSharingContainers } from "@/common/globalFunctions";
import ContainerTable from "@/components/ContainerTable.vue";
import SearchBox from "@/components/SearchBox.vue";

export default {
  name: "ContainersView",
  components: {
    ContainerTable,
    SearchBox,
  },
  data: function () {
    return {
      currentProject: {},
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
    };
  },
  computed: {
    active() {
      return this.$store.state.active;
    },
    openShareModal: {
      get() {
        return this.$store.state.openShareModal;
      },
      set() {},
    },
    isFolderUploading() {
      return this.$store.state.isUploading;
    },
    isFolderCopied() {
      return this.$store.state.isFolderCopied;
    },
    locale() {
      return this.$i18n.locale;
    },
  },
  watch: {
    active: function () {
      this.fetchContainers();
    },
    openShareModal: function () {
      if(!this.openShareModal) {
        this.fetchContainers();
      }
    },
    currentProject: function() {
      const savedDisplayOptions = this.currentProject.displayOptions;
      if (savedDisplayOptions) {
        this.hideTags = savedDisplayOptions.hideTags;
        this.hidePagination = savedDisplayOptions.hidePagination;
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
      }
    },
    isFolderUploading: function () {
      if (!this.isFolderUploading) {
        delay(() => {
          this.fetchContainers();
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
  },
  created() {
    this.updateTableOptions();
  },
  beforeMount() {
    this.abortController = new AbortController();
    this.getDirectCurrentPage();
  },
  mounted() {
    this.fetchContainers();
  },
  beforeUnmount() {
    this.abortController.abort();
  },
  methods: {
    updateTableOptions: function () {
      const displayOptions = {
        hideTags: this.hideTags,
        hidePagination: this.renderFolders,
      };
      this.tableOptions = [
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
    fetchContainers: async function () {
      if (this.active.id === undefined) {
        return;
      }

      this.currentProject = await getDB().projects.get({
        id: this.active.id,
      });

      this.containers = useObservable(
        liveQuery(() =>
          getDB().containers
            .where({ projectID: this.active.id })
            .toArray(),
        ),
      );

      await this.$store.dispatch("updateContainers", {
        projectID: this.active.id,
        signal: this.abortController.signal,
      });
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
    toggleCreateFolderModal: function (folderName) {
      this.$store.commit("toggleCreateFolderModal", true);
      if (folderName) {
        this.$store.commit("setFolderName", folderName);
      }
    },
  },
};
</script>

<style scoped>

#optionsbar {
  margin: 0.5em 0;
  background: #fff;
}
</style>
