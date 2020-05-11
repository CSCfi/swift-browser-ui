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
          Render Folders
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
          <ContainerDownloadLink />
        </p>
        <p class="control">
          <ReplicateContainerButton />
        </p>
      </div>
    </b-field>
    <b-table
      focusable
      detailed
      hoverable
      narrowed
      header-checkable
      style="width: 90%;margin-left: 5%; margin-right: 5%;"
      default-sort="name"
      :data="oList"
      :selected.sync="selected"
      :current-page.sync="currentPage"
      :paginated="isPaginated"
      :per-page="perPage"
      :pagination-simple="isPaginated"
      :default-sort-direction="defaultSortDirection"
      @page-change="( page ) => addPageToURL( page )"
      @dblclick="(row) => {if (renderFolders) {changeFolder(
        getFolderName(row.name)
      )}}"
    >
      <template slot-scope="props">
        <!-- Alt name column for case pseudo folders enabled  -->
        <b-table-column
          v-if="renderFolders && !isFile(props.row.name)"
          sortable
          field="name"
          :label="$t('message.table.name')"
        >
          <b>{{ getFolderName(props.row.name) }}</b>
        </b-table-column>
        <b-table-column
          v-else-if="renderFolders"
        >
          {{ props.row.name.replace(getPrefix(), '') }}
        </b-table-column>
        <b-table-column
          v-else
          sortable
          field="name"
          :label="$t('message.table.name')"
        >
          {{ props.row.name }}
        </b-table-column>
        <b-table-column
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
          field="url"
          label=""
          width="110"
        >
          <span v-if="renderFolders && !isFile(props.row.name)" />
          <span v-else>
            <b-button
              v-if="props.row.bytes < 1073741824"
              :href="props.row.url"
              target="_blank"
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
              size="is-small"
              tag="a"
              @click="confirmDownload ()"
            >
              <b-icon
                icon="download"
                size="is-small"
              /> {{ $t('message.download') }}
            </b-button>
          </span>
        </b-table-column>
      </template>
      <template
        slot="detail"
        slot-scope="props"
      >
        <span v-if="renderFolders && !isFile(props.row.name)">
          No details for folders
        </span>
        <span v-else>
          <ul>
            <li>
              <b>{{ $t('message.table.fileHash') }}: </b>{{ props.row.hash }}
            </li>
            <li>
              <b>{{ $t('message.table.fileType') }}: </b>
              {{ props.row.content_type }} 
            {{ props.row.content_type }} 
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
      <template slot="empty">
        <p
          style="width:100%;text-align:center;margin-top:5%;margin-bottom:5%"
        >
          {{ $t('message.emptyContainer') }}
        </p>
      </template>
    </b-table>
  </div>
</template>

<script>
import {
  getObjects,
  getSharedObjects,
} from "@/common/api";
import { getHumanReadableSize } from "@/common/conv";
import debounce from "lodash/debounce";
import ContainerDownloadLink from "@/components/ContainerDownloadLink";
import FolderUploadForm from "@/components/FolderUpload";
import ReplicateContainerButton from "@/components/ReplicateContainer";

export default {
  name: "ObjectTable",
  components: {
    ContainerDownloadLink,
    FolderUploadForm,
    ReplicateContainerButton,
  },
  data: function () {
    return {
      oList: [],
      objects: [],
      selected: undefined,
      isPaginated: true,
      renderFolders: false,
      perPage: 15,
      defaultSortDirection: "asc",
      searchQuery: "",
      currentPage: 1,
    };
  },
  watch: {
    searchQuery: function () {
      // Run debounced search every time the search box input changes
      this.debounceFilter();
    },
    objects: function () {
      if (!this.renderFolders) {
        this.oList = this.objects;
      } else {
        this.oList = this.getFolderContents();
      }
    },
    renderFolders: function () {
      if (this.renderFolders) {
        this.oList = this.getFolderContents();
      } else {
        this.oList = this.objects;
      }
    },
  },
  created: function () {
    // Lodash debounce to prevent the search execution from executing on
    // every keypress, thus blocking input
    this.debounceFilter = debounce(this.filter, 400);
  },
  beforeMount () {
    this.fetchObjects();
    this.getDirectCurrentPage();
    this.checkLargeDownloads();
  },
  methods: {
    fetchObjects: function () {
      // Get the object listing from the API if the listing hasn't yet 
      // been cached
      if (this.$route.name == "SharedObjects") {
        this.$store.state.client.getAccessDetails(
          this.$route.params.project,
          this.$route.params.container,
          this.$route.params.owner,
        ).then(
          (ret) => {
            return getSharedObjects(
              this.$route.params.owner,
              this.$route.params.container,
              ret.address,
            );
          },
        ).then(
          (ret) => {
            this.objects = ret;
          },
        );
      }
      else {
        let container = this.$route.params.container;
        if(this.$store.state.objectCache[container] == undefined) {
          this.$store.commit("setLoading", true);
          getObjects(container).then((ret) => {
            if (ret.status != 200) {
              this.$store.commit("setLoading", false);
            }
            this.$store.commit("updateObjects", [container, ret]);
            this.objects = ret;
            this.$store.commit("setLoading", false);
          }).catch(() => {
            this.$store.commit("setLoading", false);
          });
        } else {
          this.objects = this.$store.state.objectCache[container];
        }
      }
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
      // Get folderized view of the objects
      let pre_re = new RegExp(this.getPrefix());
      this.oList = this.objects.filter(
        element => element.name.match(pre_re),
      );
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
        this.$route.push({
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
        this.$route.push({
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

      this.getFolderContents();
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
      let name_re = new RegExp(this.searchQuery, "i");
      this.oList = this.objects.filter(
        element => element.name.match(name_re),
      );
    },
  },
};
</script>
