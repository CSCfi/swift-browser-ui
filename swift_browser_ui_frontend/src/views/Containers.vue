<template>
  <div
    id="container-table"
    class="contents"
  >
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
        <option value="5">
          5 {{ $t('message.table.pageNb') }}
        </option>
        <option value="10">
          10 {{ $t('message.table.pageNb') }}
        </option>
        <option value="15">
          15 {{ $t('message.table.pageNb') }}
        </option>
        <option value="25">
          25 {{ $t('message.table.pageNb') }}
        </option>
        <option value="50">
          50 {{ $t('message.table.pageNb') }}
        </option>
        <option value="100">
          100 {{ $t('message.table.pageNb') }}
        </option>
      </b-select>
      <div class="control is-flex">
        <b-switch
          v-if="(containers.value || []).length < 500"
          v-model="isPaginated"
          data-testid="paginationSwitch"
        >
          {{ $t('message.table.paginated') }}
        </b-switch>
        <b-switch
          v-model="showTags"
        >
          {{ $t('message.table.showTags') }}
        </b-switch>
      </div>
      <b-field class="control searchBox">
        <b-input
          v-model="searchQuery"
          :placeholder="$t('message.searchBy')"
        />
      </b-field>
      <div class="field has-addons uploadGroup">
        <p class="control">
          <b-button
            tag="router-link"
            :to="{name: 'AddContainer'}"
            type="is-primary"
            outlined
            icon-left="folder-plus"
          >
            {{ $t('message.createContainerButton') }}
          </b-button>
        </p>
        <p class="control">
          <b-button
            :label="$t('message.upload')"
            type="is-primary"
            outlined
            icon-left="upload"
            tag="router-link"
            :to="{name: 'UploadView', params: {
              project: $route.params.project,
              container: 'upload-'.concat(Date.now().toString()),
            }}"
          />
        </p>
      </div>
    </b-field>
    <b-table
      class="containerTable"
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
      @page-change="(page) => addPageToURL ( page )"
      @dblclick="(row) => $router.push( getConAddr ( row['name'] ) )"
      @keyup.native.enter="$router.push( getConAddr ( selected['name'] ))"
      @keyup.native.space="$router.push( getConAddr ( selected['name'] ))"
    >
      <b-table-column
        sortable
        field="name"
        :label="$t('message.table.name')"
      >
        <template #default="props">
          <span 
            :class="props.row.count ? 'has-text-weight-bold' : ''"
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
              :type="selected==props.row ? 'is-primary-invert' : 'is-primary'"
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
                v-if="selected==props.row"
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
                v-if="selected==props.row"
                type="is-primary"
                outlined
                size="is-small"
                disabled
                inverted
                icon-left="share"
              >
                {{ $t('message.share.share') }}
              </b-button>
              <b-button
                v-else
                type="is-primary"
                outlined
                size="is-small"
                disabled
                icon-left="share"
              >
                {{ $t('message.share.share') }}
              </b-button>
            </p>
            <p
              v-else
              class="control"
            >
              <b-button
                v-if="selected==props.row"
                type="is-primary"
                outlined
                size="is-small"
                inverted
                icon-left="share"
                @click="$router.push({
                  name: 'SharingView',
                  query: {container: props.row.name}
                })"
              >
                {{ $t('message.share.share') }}
              </b-button>
              <b-button
                v-else
                type="is-primary"
                outlined
                size="is-small"
                icon-left="share"
                @click="$router.push({
                  name: 'SharingView',
                  query: {container: props.row.name}
                })"
              >
                {{ $t('message.share.share') }}
              </b-button>
            </p>
            <p class="control">
              <ReplicateContainerButton
                v-if="selected==props.row"
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
                tag="router-link"
                type="is-primary"
                outlined
                size="is-small"
                icon-left="pencil"
                :inverted="selected==props.row ? true : false"
                :to="{
                  name: 'EditContainer',
                  params: {container: props.row.name}
                }"
              >
                {{ $t('message.edit') }}
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
            v-if="selected==props.row"
            :inverted="true"
            :objects="props.row.count"
            :container="props.row.name"
          />
          <DeleteContainerButton
            v-else
            :inverted="false"
            :objects="props.row.count"
            :container="props.row.name"
          />
        </template>
      </b-table-column>

      <template #empty>
        <p class="emptyTable">
          {{ $t('message.emptyProject') }}
        </p>
      </template>
    </b-table>
  </div>
</template>

<script>
import { 
  getHumanReadableSize, 
  truncate, 
} from "@/common/conv";
import debounce from "lodash/debounce";
import { liveQuery } from "dexie";
import { useObservable } from "@vueuse/rxjs";
import escapeRegExp from "lodash/escapeRegExp";
import ContainerDownloadLink from "@/components/ContainerDownloadLink";
import ReplicateContainerButton from "@/components/ReplicateContainer";
import DeleteContainerButton from "@/components/ContainerDeleteButton";

export default {
  name: "ContainersView",
  components: {
    ContainerDownloadLink,
    ReplicateContainerButton,
    DeleteContainerButton,
  },
  filters:{
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
      currentPage: 1,
      shareModalIsActive: false,
      showTags: true,
      abortController: null,
      containers: {value: []},
    };
  },
  computed: {
    active () {
      return this.$store.state.active;
    },
  },
  watch: {
    searchQuery: function () {
      // Run debounced search every time the search box input changes
      this.debounceFilter();
    },
    active: function () {
      this.fetchContainers();
    },
  },
  created: function () {
    // Lodash debounce to prevent the search execution from executing on
    // every keypress, thus blocking input
    this.debounceFilter = debounce(this.filter, 400);
  },
  beforeMount () {
    this.abortController = new AbortController();
    this.getDirectCurrentPage();
  },
  mounted() {
    this.fetchContainers();
  },
  beforeDestroy () {
    this.abortController.abort();
  },
  methods: {
    fetchContainers: async function () {
      if (this.active.id === undefined) {
        return;
      }
      this.containers = useObservable(
        liveQuery(() => 
          this.$store.state.db.containers
            .where({projectID: this.active.id})
            .toArray(),
        ),
      );
      await this.$store.dispatch(
        "updateContainers", 
        {projectID: this.active.id, signal: null},
      );
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
      this.currentPage = this.$route.query.page ?
        parseInt(this.$route.query.page) :
        1;
    },
    addPageToURL: function (pageNumber) {
      // Add pagination current page number to the URL in query string
      this.$router.push("?page=" + pageNumber);
    },
    localHumanReadableSize: function (size) {
      // Make getHumanReadableSize usable in instance namespace
      return getHumanReadableSize(size);
    },
    filter: function() {
      // request parameter should be sanitized first
      var safeKey = escapeRegExp(this.searchQuery);
      var name_cmp = new RegExp(safeKey, "i");
      this.cList = this.containers.filter(
        element => 
          element.name.match(name_cmp)
          || this.tags[element.name].join("\n").match(name_cmp),
      );
    },
  },
};
</script>

<style scoped>
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
</style>
