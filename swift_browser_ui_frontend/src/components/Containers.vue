<template>
  <div class="contents">
    <c-row
      id="optionsbar"
      justify="space-between"
    >
      <SearchBox :containers="renderingContainers"/>
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
      :disable-pagination="disablePagination"
      :hide-tags="hideTags"
    />
  </div>
</template>

<script>
import { liveQuery } from "dexie";
import { useObservable } from "@vueuse/rxjs";
import { getSharingContainers } from "@/common/globalFunctions";
import ContainerTable from "@/components/ContainerTable";
import SearchBox from "@/components/SearchBox";

export default {
  name: "ContainersView",
  components: {
    ContainerTable,
    SearchBox,
  },
  data: function () {
    return {
      disablePagination: false,
      hideTags: false,
      selected: undefined,
      isPaginated: true,
      perPage: 15,
      direction: "asc",
      currentPage: 1,
      showTags: true,
      optionsKey: 1,
      abortController: null,
      containers: { value: [] },
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
    locale() {
      return this.$i18n.locale;
    },
  },
  watch: {
    active: function () {
      this.fetchContainers();
    },
    project: function () {
      this.fetchContainers();
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
  beforeDestroy() {
    this.abortController.abort();
  },
  methods: {
    updateTableOptions: function () {
      this.tableOptions = [
        {
          name: this.hideTags
            ? this.$t("message.tableOptions.showTags")
            : this.$t("message.tableOptions.hideTags"),
          action: () => {
            this.hideTags = !(this.hideTags);
            this.updateTableOptions();
          },
        },
        {
          name: this.disablePagination
            ? this.$t("message.tableOptions.showPagination")
            : this.$t("message.tableOptions.hidePagination"),
          action: () => {
            this.disablePagination = !(this.disablePagination);
            this.updateTableOptions();
          },
        },
      ];
      this.optionsKey++;
    },
    fetchContainers: async function () {
      if (
        this.active.id === undefined &&
        this.$route.params.project === undefined
      ) {
        return;
      }

      const containers = useObservable(
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

      if (this.$route.name === "SharedFrom") {
        const sharingContainers
          = await getSharingContainers(this.$route.params.project);
        this.renderingContainers = containers.value.filter(
          cont => sharingContainers.some(item =>
            item === cont.name,
          ),
        );
      }

      else if (this.$route.name === "SharedTo") {
        this.renderingContainers = containers.value.filter(cont =>
          cont.owner,
        );
      } else {
        this.renderingContainers = containers.value;
      }
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
