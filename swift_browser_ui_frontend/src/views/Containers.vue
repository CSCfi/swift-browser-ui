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
          v-if="bList.length < 500"
          v-model="isPaginated"
        >
          {{ $t('message.table.paginated') }}
        </b-switch>
      </div>
      <b-field class="control searchBox">
        <b-input
          v-model="searchQuery"
          :placeholder="$t('message.searchBy')"
        />
      </b-field>
      <div class="field has-addons uploadGroup">
        <FolderUploadForm dropelement="container-table" />
      </div>
    </b-field>
    <b-table
      class="containerTable"
      focusable
      hoverable
      narrowed
      default-sort="name"
      :data="bList"
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
          <span v-if="!props.row.bytes">
            <b-icon
              icon="folder-outline"
              size="is-small"
            /> 
            {{ props.row.name }}
          </span>
          <span
            v-else
            class="has-text-weight-bold"
          >
            <b-icon
              icon="folder"
              size="is-small"
            /> 
            {{ props.row.name }}
          </span>
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
              >
                <b-icon
                  icon="share"
                  size="is-small"
                /> {{ $t('message.share.share') }}
              </b-button>
              <b-button
                v-else
                type="is-primary"
                outlined
                size="is-small"
                disabled
              >
                <b-icon
                  icon="share"
                  size="is-small"
                /> {{ $t('message.share.share') }}
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
                @click="$router.push({
                  name: 'Sharing',
                  query: {container: props.row.name}
                })"
              >
                <b-icon
                  icon="share"
                  size="is-small"
                /> {{ $t('message.share.share') }}
              </b-button>
              <b-button
                v-else
                type="is-primary"
                outlined
                size="is-small"
                @click="$router.push({
                  name: 'Sharing',
                  query: {container: props.row.name}
                })"
              >
                <b-icon
                  icon="share"
                  size="is-small"
                /> {{ $t('message.share.share') }}
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
          </div>
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
import { getHumanReadableSize } from "@/common/conv";
import debounce from "lodash/debounce";
import FolderUploadForm from "@/components/FolderUpload";
import ContainerDownloadLink from "@/components/ContainerDownloadLink";
import ReplicateContainerButton from "@/components/ReplicateContainer";

export default {
  name: "Containers",
  components: {
    FolderUploadForm,
    ContainerDownloadLink,
    ReplicateContainerButton,
  },
  data: function () {
    return {
      files: [],
      folders: [],
      bList: [],
      selected: undefined,
      isPaginated: true,
      perPage: 15,
      defaultSortDirection: "asc",
      searchQuery: "",
      currentPage: 1,
      shareModalIsActive: false,
    };
  },
  computed: {
    active () {
      return this.$store.state.active;
    },
    containers () {
      return this.$store.state.containerCache;
    },
  },
  watch: {
    searchQuery: function () {
      // Run debounced search every time the search box input changes
      this.debounceFilter();
    },
    containers: function () {
      this.bList = this.containers;
    },
  },
  created: function () {
    // Lodash debounce to prevent the search execution from executing on
    // every keypress, thus blocking input
    this.debounceFilter = debounce(this.filter, 400);
  },
  beforeMount () {
    this.getDirectCurrentPage();
  },
  mounted() {
    this.fetchContainers();
  },
  methods: {
    fetchContainers: function () {
      // Get the container listing from the API if the listing hasn't yet
      // been cached.
      if(this.bList.length < 1) {
        this.$store.commit("updateContainers");
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
      var name_cmp = new RegExp(this.searchQuery, "i");
      this.bList = this.containers.filter(
        element => element.name.match(name_cmp),
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
