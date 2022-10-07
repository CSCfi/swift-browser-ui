<template>
  <div
    class="containers"
  >
    <c-modal
      v-control
      v-csc-model="openShareModal"
      width="50vw"
    >
      <ShareModal />
    </c-modal>

    <div class="contents">
      <c-row
        id="optionsbar"
        justify="space-between"
      >
        <SearchBox />
        <c-menu
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
        :conts="containers.value"
        :disable-pagination="disablePagination"
        :hide-tags="hideTags"
      />
    </div>
  </div>
</template>

<script>
import { liveQuery } from "dexie";
import { useObservable } from "@vueuse/rxjs";
import ContainerTable from "@/components/ContainerTable";
import SearchBox from "@/components/SearchBox";
import ShareModal from "@/components/ShareModal";

export default {
  name: "ContainersView",
  components: {
    ContainerTable,
    SearchBox,
    ShareModal,
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
      shareModalIsActive: false,
      showTags: true,
      abortController: null,
      containers: { value: [] },
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
  },
  watch: {
    active: function () {
      this.fetchContainers();
    },
    project: function () {
      this.fetchContainers();
    },
  },
  created() {
    this.tableOptions = [
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

.containers {
   margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
}

c-modal {
  position: relative;
  margin: 0 auto;
  display: inline-flex;
}

#optionsbar {
  margin: 0.5em;
  background: #fff;
  box-shadow: rgba(0, 0, 0, 0.15) 0px 5px 15px 0px;
}
</style>