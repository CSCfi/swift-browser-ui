<template>
  <div class="contents">
    <c-row
      id="optionsbar"
      justify="end"
    >
      <!--<SearchBox :containers="renderingContainers" />-->
      <div class="row-end">
        <c-button
          size="small"
          outlined
          data-testid="create-bucket"
          @click="toggleCreateBucketModal(false)"
          @keyup.enter="toggleCreateBucketModal(true)"
        >
          <c-icon :path="mdiPlus" />
          {{ $t("message.createBucket") }}
        </c-button>
        <c-menu
          :key="optionsKey"
          :items.prop="tableOptions"
          data-testid="table-options-selector"
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
        :conts="renderingContainers"
        :show-timestamp="showTimestamp"
        :disable-pagination="hidePagination"
        :hide-tags="true"
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
import { getDB } from "@/common/idb";
import { updateContainers } from "@/common/idbFunctions";
import { useObservable } from "@vueuse/rxjs";
import { mdiPlus } from "@mdi/js";
import { toggleCreateBucketModal } from "@/common/globalFunctions";
import { getAccessDetails, getSharingContainers } from "@/common/share";
import ContainerTable from "@/components/ContainerTable.vue";
//import SearchBox from "@/components/SearchBox.vue";
import { setPrevActiveElement } from "@/common/keyboardNavigation";

export default {
  name: "ContainersView",
  components: {
    ContainerTable,
    //SearchBox,
  },
  data: function () {
    return {
      mdiPlus,
      currentProject: {},
      showTimestamp: false,
      hidePagination: false,
      //hideTags: false,
      showTags: true,
      optionsKey: 1,
      abortController: null,
      abortRenderingController: null,
      containers: [], // idb bucket data
      renderingContainers: [], // enriched and filtered data for table
      contsLoading: false,
    };
  },
  computed: {
    readyToSetUp() {
      return (this.active?.id && this.$store.state.sharingClient);
    },
    active() {
      return this.$store.state.active;
    },
    isBucketUploading() {
      return this.$store.state.isUploading;
    },
    sharingUpdated() {
      return this.$store.state.sharingUpdated;
    },
    locale() {
      return this.$i18n.locale;
    },
  },
  watch: {
    readyToSetUp: function() {
      this.setUpIfReady();
    },
    currentProject: function() {
      const savedDisplayOptions = this.currentProject.displayOptions;
      if (savedDisplayOptions) {
        //this.hideTags = savedDisplayOptions.hideTags;
        this.hidePagination = savedDisplayOptions.hidePagination;
        this.showTimestamp = savedDisplayOptions.showTimestamp;
        this.updateTableOptions();
      }
    },
    containers: async function() {
      if (!this.containers?.length)  {
        this.renderingContainers = [];
        return;
      }

      // Abort previous update
      this.abortRenderingController?.abort({ reason: "Abort duplicate" });
      this.abortRenderingController = new AbortController();
      const { signal } = this.abortRenderingController;

      // Segment buckets are never displayed
      const bucketsNoSegments =  this.containers.filter(bucket =>
        !bucket.name.endsWith("_segments"));

      let finalBuckets = [];

      if (this.$route.name === "SharedTo") {
        // Shared to current project
        finalBuckets = await this.enrichSharedBuckets(bucketsNoSegments, signal);
      }
      else if (this.$route.name === "SharedFrom") {
        // Shared from current project
        const sharingBuckets = await getSharingContainers(
          this.$route.params.project,
          signal,
        );
        const sharingSet = new Set(sharingBuckets);
        finalBuckets = bucketsNoSegments
          .filter(
            bucket => sharingSet.has(bucket.name))
          .map((bucket) => ({...bucket, sharing: "sharing"}));
      }
      else {
        // All buckets
        const sharingBuckets = await getSharingContainers(
          this.$route.params.project,
          signal,
        );
        const sharingSet = new Set(sharingBuckets);

        const sharedBuckets = await this.enrichSharedBuckets(bucketsNoSegments, signal);
        const sharedMap = new Map(sharedBuckets.map(bucket => [bucket.name, bucket]));

        // Combine buckets
        finalBuckets = bucketsNoSegments.map(bucket => {
          if (sharedMap.has(bucket.name)) {
            return {
              ...bucket,
              ...sharedMap.get(bucket.name),
              sharing: "shared",
            };
          }

          else if (sharingSet.has(bucket.name)) {
            return {
              ...bucket,
              sharing: "sharing",
            };
          }

          return {
            ...bucket,
            sharing: "none",
          };
        });
      }

      if (!signal?.aborted) {
        // Assign once to prevent table re-renders
        this.renderingContainers = finalBuckets;
        this.contsLoading = false;
      }
    },
    isBucketUploading(newValue) {
      if (newValue === false) {
        this.contsLoading = true;
        setTimeout(() => {
          this.fetchContainers();
          this.contsLoading = false;
        }, 3000);
      }
    },
    sharingUpdated(newValue) {
      if (newValue) {
        this.fetchContainers(true);
        this.$store.commit("setSharingUpdated", false);
      }
    },
    locale: function () {
      this.updateTableOptions();
    },
  },
  created() {
    this.updateTableOptions();
    this.abortController = new AbortController();
    this.abortRenderingController = new AbortController();
    this.setUpIfReady();
  },
  beforeUnmount() {
    this.abortController.abort({ reason: "Unmounting component" });
    this.abortRenderingController.abort({ reason: "Unmounting component" });

  },
  methods: {
    setUpIfReady: async function () {
      // Check id: not available on created on page refresh
      if (this.readyToSetUp) {
        this.currentProject = await getDB().projects.get({
          id: this.active.id,
        });
        this.fetchContainers(true);
      }
    },
    enrichSharedBuckets: async function (buckets, signal) {
      try {
        let shared = await Promise.all(
          buckets
            .filter(bucket => bucket.owner)
            // Get access details for each bucket
            .map(async(bucket) => {
              if (signal?.aborted) throw signal?.reason;
              const sharedDetails = await getAccessDetails(
                this.$route.params.project,
                bucket.name,
                bucket.owner,
                signal);
              const accessRights = sharedDetails ? sharedDetails.access : null;
              if (accessRights !== null) return {...bucket, accessRights, sharing: "shared"};
            }),
        );
        // Remove buckets that share details don't exist for
        shared = shared.filter(bucket => !!bucket);
        return shared;
      } catch {
        return [];
      }
    },
    updateTableOptions: function () {
      const displayOptions = {
        showTimestamp: this.showTimestamp,
        //hideTags: this.hideTags,
        hidePagination: this.hidePagination,
      };
      this.tableOptions = [
        /*{
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
        },*/
        /*{
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
        },*/
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

      this.containers = useObservable(
        liveQuery(() =>
          getDB().containers
            .where({ projectID: this.active.id })
            .toArray(),
        ),
      );

      await updateContainers(this.active.id, this.abortController.signal);
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
    toggleCreateBucketModal: function (keypress) {
      toggleCreateBucketModal();
      if (keypress) {
        setPrevActiveElement();
      }
      setTimeout(() => {
        const newBucketInput = document
          .querySelector("#newBucket-input input");
        newBucketInput.tabIndex = "0";
        newBucketInput.focus();
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
