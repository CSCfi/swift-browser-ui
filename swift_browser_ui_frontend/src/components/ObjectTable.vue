<template>
  <div
    id="object-table"
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
          v-if="oList.value && oList.value.length < 500"
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
      <div class="control is-flex">
        <b-switch v-model="showTags">
          {{ $t('message.table.showTags') }}
        </b-switch>
      </div>
      <b-field class="control searchBox">
        <b-input
          v-model="searchQuery"
          :placeholder="$t('message.objects.filterBy')"
        />
      </b-field>
      <div class="field has-addons uploadGroup">
        <p class="control">
          <b-button
            :label="$t('message.upload')"
            type="is-primary"
            outlined
            icon-left="upload"
            tag="router-link"
            :to="{name: 'UploadView', params: {
              project: ($route.params.owner ? $route.params.owner
                : $route.params.project),
              container: $route.params.container,
            }}"
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
            :label="$t('message.table.clearChecked')"
            type="is-primary"
            outlined
            @click="checkedRows = []"
          />
        </p>
      </div>
      <div>
        <DeleteObjectsButton
          size="is-normal"
          :inverted="false"
          :disabled="checkedRows.length == 0 ? true : false"
          :objects="checkedRows"
        />
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
      :data="oList.value"
      :selected.sync="selected"
      :current-page.sync="currentPage"
      :paginated="isPaginated"
      :per-page="perPage"
      :pagination-simple="isPaginated"
      :default-sort-direction="defaultSortDirection"
      :row-class="row => !isVisible(row.id) ? 'is-hidden' : ''"
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
          /> <b>{{ getFolderName(props.row.name) | truncate(100) }}</b>
        </span>
        <span v-else-if="renderFolders">
          {{ props.row.name.replace(getPrefix(), '') | truncate(100) }}
        </span>
        <span v-else>
          {{ props.row.name | truncate(100) }}
        </span>
        <b-taglist v-if="displayTags(props.row.name)">
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
        width="90"
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
                icon-left="download"
              >
                {{ $t('message.download') }}
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
                icon-left="download"
              >
                {{ $t('message.download') }}
              </b-button>
              <b-button
                v-else
                :alt="$t('message.downloadAltLarge') + ' ' + props.row.name"
                type="is-primary"
                outlined
                :inverted="props.row === selected ? true : false"
                size="is-small"
                tag="a"
                icon-left="download"
                @click="confirmDownload ()"
              >
                {{ $t('message.download') }}
              </b-button>
            </p>
            <p
              v-if="displayTags(props.row.name)" 
              class="control"
            >
              <b-button 
                tag="router-link"
                type="is-primary"
                outlined
                size="is-small"
                icon-left="pencil"
                :inverted="selected==props.row ? true : false"
                :to="getEditRoute(container, props.row.name)"
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
          <span v-if="renderFolders && !isFile(props.row.name)" />
          <DeleteObjectsButton
            v-else 
            size="is-small"
            :inverted="props.row === selected ? true : false"
            :disabled="false"
            :objects="[props.row]"
          />
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
import { getHumanReadableSize, truncate } from "@/common/conv";
import { liveQuery } from "dexie";
import { useObservable } from "@vueuse/rxjs";
import debounce from "lodash/debounce";
import escapeRegExp from "lodash/escapeRegExp";
import ContainerDownloadLink from "@/components/ContainerDownloadLink";
import ReplicateContainerButton from "@/components/ReplicateContainer";
import DeleteObjectsButton from "@/components/ObjectDeleteButton";

export default {
  name: "ObjectTable",
  components: {
    ContainerDownloadLink,
    ReplicateContainerButton,
    DeleteObjectsButton,
  },
  filters: {
    truncate,
  },
  data: function () {
    return {
      oList: {value: []},
      selected: undefined,
      isPaginated: true,
      renderFolders: false,
      showTags: true,
      perPage: 15,
      defaultSortDirection: "asc",
      searchQuery: "",
      currentPage: 1,
      checkedRows: [],
      abortController: null,
      filteredObjects: [],
      inCurrentFolder: [],
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
    container () {
      return this.$route.params.container;
    },
    active () {
      return this.$store.state.active;
    },
    sharedObjects() {
      return this.$store.state.objectCache;
    },
  },
  watch: {
    active: function() {
      this.updateObjects(); 
    },
    searchQuery: function () {
      // Run debounced search every time the search box input changes
      this.debounceFilter();
    },
    renderFolders: function () {
      this.selected = undefined;
      this.checkedRows = [];
      if (this.renderFolders) {
        this.inCurrentFolder = this.getFolderContents();
      } else {
        this.inCurrentFolder = [];
        this.$route.query.prefix = "";
      }
    },
    sharedObjects: function () {
      if(this.$route.name !== "SharedObjects") {
        return;
      }
      this.oList = {value: this.sharedObjects};
    },
    prefix: function () {
      if (this.renderFolders) {
        this.inCurrentFolder = this.getFolderContents();
        this.$store.commit("setPrefix", this.prefix);
      }
    },
    queryPage: function () {
      this.currentPage = this.queryPage;
    },
    ["oList.value"]: async function() {
      if (this.oList.value !== undefined && this.$route.query.selected) {
        const selected = this.$route.query.selected;
        const obj = this.oList.value.find(o => {
          return o.name === selected;
        });
        if (obj) {
          this.selected = obj;
        }
      }
    },
  },
  created: function () {
    // Lodash debounce to prevent the search execution from executing on
    // every keypress, thus blocking input
    this.debounceFilter = debounce(this.filter, 400);
    this.$store.commit("erasePrefix");
  },
  beforeMount () {
    this.abortController = new AbortController();
    this.getDirectCurrentPage();
    this.checkLargeDownloads();
  },
  mounted () {
    this.updateObjects();
  },
  beforeDestroy () {
    this.abortController.abort();
  },
  methods: {
    updateObjects: async function () {
      if (
        this.container === undefined 
        || (
          this.active.id === undefined
          && this.$route.params.project
        )
      ) {
        return;
      }

      if(this.$route.name === "SharedObjects") {
        await this.$store.dispatch(
          "updateSharedObjects", 
          {
            project: this.$route.params.project,
            owner: this.$route.params.owner,
            container: {
              id: 0,
              name: this.$route.params.container,
            },
            signal: this.abortController.signal,
          },
        );
        return;
      }

      const container = await this.$store.state.db.containers
        .get({
          projectID: this.$route.params.project, 
          name: this.container,
        });
      this.oList = useObservable(
        liveQuery(() =>
          this.$store.state.db.objects
            .where({"containerID": container.id})
            .toArray(),
        ),
      );
      this.$store.dispatch(
        "updateObjects", 
        {
          projectID: this.$route.params.project,
          container: container,
          signal: this.abortController.signal,
        },
      );
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
          name: "ObjectsView",
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

      let tmpList = this.oList.value.filter(
        el => el.name.match(pre_re),
      );

      let idList = [];
      let folders = new Set();

      tmpList.forEach(element => {
        let folderName = this.getFolderName(element.name);

        if (folders.has(folderName)) {
          return;
        }
        folders.add(folderName);
        idList.push(element.id);
      });
      
      return idList;
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
          name: "ObjectsView",
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

      this.inCurrentFolder = this.getFolderContents();
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
    isVisible: function(id) {
      let visible = true;
      if (
        this.renderFolders 
        && !this.inCurrentFolder.includes(id)
      ) {
        visible = false;
      }
      if (this.filteredObjects.includes(id)) {
        visible = false;
      }
      return visible;
    },
    filter: function () {
      if(this.searchQuery.length === 0) {
        this.filteredObjects = [];
        return;
      }
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
        prev.push(element.id);
        return prev;
      }
      this.filteredObjects = this.oList.value.reduce(search, []);
    },
    displayTags: function (name) {
      return this.showTags && !(this.renderFolders && !this.isFile(name));
    },
    getEditRoute: function(containerName, objectName) {
      if (this.$route.name == "SharedObjects") {
        return {
          name: "EditSharedObjectView",
          params: {
            container: containerName, 
            object: objectName, 
            owner: this.$route.params.owner,
          },
        };
      }
      return {
        name: "EditObjectView",
        params: {
          container: containerName, 
          object: objectName,
        },
      };
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
