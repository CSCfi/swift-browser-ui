<template>
  <div id="object-table">
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
          v-if="oList.length < 500"
          v-model="isPaginated"
        >
          {{ $t('message.table.paginated') }}
        </b-switch>
      </div>
      <div class="control is-flex">
        <b-switch v-model="renderFolders">
          {{ $t('message.renderFolders') }}
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
          <FolderUploadForm dropelement="object-table" />
        </p>
        <p class="control">
          <DeleteObjectsButton
            size="is-normal"
            :inverted="false"
            :disabled="checkedRows.length == 0 ? true : false"
            :objects="checkedRows"
          />
        </p>
        <p class="control">
          <ContainerDownloadLink />
        </p>
        <p class="control">
          <ReplicateContainerButton />
        </p>
        <p class="control">
          <b-button
            label="Clear checked"
            type="is-primary"
            outlined
            @click="checkedRows = []"
          />
        </p>
      </div>
    </b-field>
    <b-table
      class="objectTable"
      focusable
      detailed
      hoverable
      narrowed
      header-checkable
      checkable
      checkbox-position="right"
      :checked-rows.sync="checkedRows"
      :is-row-checkable="isRowCheckable"
      default-sort="name"
      :data="oList"
      :selected.sync="selected"
      :current-page.sync="currentPage"
      :paginated="isPaginated"
      :per-page="perPage"
      :pagination-simple="isPaginated"
      :default-sort-direction="defaultSortDirection"
      @page-change="( page ) => addPageToURL( page )"
      @dblclick="(row) => {if (
        renderFolders &&
        !isFile(row.name)
      ) {changeFolder(
        getFolderName(row.name)
      )}}"
      @keyup.native.enter="(row) => {if (
        renderFolders &&
        !isFile(row.name)
      ) {changeFolder(
        getFolderName(row.name)
      )}}"
      @keyup.native.space="(row) => {if (
        renderFolders &&
        !isFile(row.name)
      ) {changeFolder(
        getFolderName(row.name)
      )}}"
    >
      <!-- Alt name column for case pseudo folders enabled  -->
      <b-table-column
        v-slot="props"
        sortable
        field="name"
        :label="$t('message.table.name')"
      >
        <span v-if="renderFolders && !isFile(props.row.name)">
          <b-icon
            icon="folder"
            size="is-small"
          /> <b>{{ getFolderName(props.row.name) }}</b>
        </span>
        <span v-else-if="renderFolders">
          {{ props.row.name.replace(getPrefix(), '') }}
        </span>
        <span v-else>
          {{ props.row.name }}
        </span>
      </b-table-column>
      <b-table-column
        v-slot="props"
        sortable
        field="last_modified"
        :label="$t('message.table.modified')"
      >
        <span v-if="renderFolders && !isFile(props.row.name)" />
        <span v-else>
          {{ getHumanReadableDate(props.row.last_modified) }}
        </span>
      </b-table-column>
      <b-table-column
        v-slot="props"
        sortable
        field="bytes"
        :label="$t('message.table.size')"
      >
        <span v-if="renderFolders && !isFile(props.row.name)" />
        <span v-else>
          {{ localHumanReadableSize(props.row.bytes) }}
        </span>
      </b-table-column>
      <b-table-column
        field="functions"
        label=""
        width="150"
      >
        <template #default="props">
          <div class="field has-addons">
            <span v-if="renderFolders && !isFile(props.row.name)" />
            <p
              v-else
              class="control"
            >
              <b-button
                v-if="props.row.bytes < 1073741824"
                :href="props.row.url"
                target="_blank"
                :inverted="props.row == selected ? true : false"
                :alt="$t('message.downloadAlt') + ' ' + props.row.name"
                type="is-primary"
                outlined
                size="is-small"
                tag="a"
              >
                <b-icon
                  icon="download"
                  size="is-small"
                /> {{ $t('message.download') }}
              </b-button>
              <b-button
                v-else-if="allowLargeDownloads"
                :href="props.row.url"
                target="_blank"
                :inverted="props.row == selected ? true : false"
                :alt="$t('message.downloadAlt') + ' ' + props.row.name"
                type="is-primary"
                outlined
                size="is-small"
                tag="a"
              >
                <b-icon
                  icon="download"
                  size="is-small"
                /> {{ $t('message.download') }}
              </b-button>
              <b-button
                v-else
                :alt="$t('message.downloadAltLarge') + ' ' + props.row.name"
                type="is-primary"
                outlined
                :inverted="props.row === selected ? true : false"
                size="is-small"
                tag="a"
                @click="confirmDownload ()"
              >
                <b-icon
                  icon="download"
                  size="is-small"
                /> {{ $t('message.download') }}
              </b-button>
            </p>
            <span v-if="renderFolders && !isFile(props.row.name)" />
            <p
              v-else
              class="control"
            >
              <DeleteObjectsButton
                size="is-small"
                :inverted="props.row === selected ? true : false"
                :disabled="false"
                :objects="props.row.name"
              />
            </p>
          </div>
        </template>
      </b-table-column>
      <template
        #detail="props"
      >
        <span v-if="renderFolders && !isFile(props.row.name)">
          {{ $t('message.table.folderDetails') }}
        </span>
        <span v-else>
          <ul>
            <li>
              <b>{{ $t('message.table.fileHash') }}: </b>{{ props.row.hash }}
            </li>
            <li>
              <b>{{ $t('message.table.fileType') }}: </b>
              {{ props.row.content_type }} 
            </li>
            <li>
              <b>{{ $t('message.table.fileDown') }}: </b>
              <a
                v-if="props.row.bytes < 1073741824"
                :href="props.row.url"
                target="_blank"
                :alt="$t('message.downloadAlt') + ' ' + props.row.name"
              >
                <b-icon
                  icon="download"
                  size="is-small"
                /> {{ $t('message.downloadLink') }}
              </a>
              <a
                v-else-if="allowLargeDownloads"
                :href="props.row.url"
                target="_blank"
                :alt="$t('message.downloadAlt') + ' ' + props.row.name"
              >
                <b-icon
                  icon="download"
                  size="is-small"
                /> {{ $t('message.downloadLink') }}
              </a>
              <a
                v-else
                :alt="$t('message.downloadAltLarge') + ' ' + props.row.name"
                @click="confirmDownload ()"
              >
                <b-icon
                  icon="download"
                  size="is-small"
                /> {{ $t('message.downloadLink') }}
              </a>
            </li>
          </ul>
        </span>
      </template>
      <template #empty>
        <p class="emptyTable">
          {{ $t('message.emptyContainer') }}
        </p>
      </template>
    </b-table>
  </div>
</template>

<script>
import { getHumanReadableSize } from "@/common/conv";
import debounce from "lodash/debounce";
import escapeRegExp from "lodash/escapeRegExp";
import ContainerDownloadLink from "@/components/ContainerDownloadLink";
import FolderUploadForm from "@/components/FolderUpload";
import ReplicateContainerButton from "@/components/ReplicateContainer";
import DeleteObjectsButton from "@/components/ObjectDeleteButton";

export default {
  name: "ObjectTable",
  components: {
    ContainerDownloadLink,
    FolderUploadForm,
    ReplicateContainerButton,
    DeleteObjectsButton,
  },
  data: function () {
    return {
      oList: [],
      selected: undefined,
      isPaginated: true,
      renderFolders: false,
      perPage: 15,
      defaultSortDirection: "asc",
      searchQuery: "",
      currentPage: 1,
      checkedRows: [],
    };
  },
  computed: {
    prefix () {
      return this.$route.query.prefix || "";
    },
    queryPage () {
      return this.$route.query.page || 1;
    },
    objects () {
      return this.$store.state.objectCache;
    },
  },
  watch: {
    searchQuery: function () {
      // Run debounced search every time the search box input changes
      this.debounceFilter();
    },
    renderFolders: function () {
      if (this.renderFolders) {
        this.oList = this.getFolderContents();
      } else {
        this.oList = this.objects;
      }
    },
    objects: function () {
      if (this.renderFolders) {
        this.oList = this.getFolderContents();
      } else {
        this.oList = this.objects;
      }
    },
    prefix: function () {
      if (this.renderFolders) {
        this.oList = this.getFolderContents();
      }
    },
    queryPage: function () {
      this.currentPage = this.queryPage;
    },
  },
  created: function () {
    // Lodash debounce to prevent the search execution from executing on
    // every keypress, thus blocking input
    this.debounceFilter = debounce(this.filter, 400);
  },
  beforeMount () {
    this.updateObjects();
    this.getDirectCurrentPage();
    this.checkLargeDownloads();
  },
  methods: {
    updateObjects: function () {
      // Update current object listing in Vuex if length is too little
      this.$store.commit({
        type: "updateObjects",
        route: this.$route,
      });
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
          name: "Objects",
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

      let tmpList = this.objects.filter(
        el => el.name.match(pre_re),
      );

      let retList = [];

      tmpList.forEach(element => {
        for (let i of retList) {
          if (this.getFolderName(i.name).match(
            this.getFolderName(element.name),
          )) {
            return;
          }
        }
        retList.push(element);
      });

      return retList;
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
          name: "Objects",
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

      this.oList = this.getFolderContents();
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
    filter: function () {
      // request parameter should be sanitized first
      var safeKey = escapeRegExp(this.searchQuery);
      var name_re = new RegExp(safeKey, "i");
      if (this.renderFolders) {
        this.oList = this.getFolderContents().filter(
          element => element.name.match(name_re),
        );
      } else {
        this.oList = this.objects.filter(
          element => element.name.match(name_re),
        );
      }
    },
  },
};
</script>

<style scoped>
.objectTable {
  width: 90%;
  margin-left: 5%;
  margin-right: 5%;
}

.emptyTable {
  width: 100%;
  text-align: center;
  margin-top: 5%;
  margin-bottom: 5%;
}
</style>
