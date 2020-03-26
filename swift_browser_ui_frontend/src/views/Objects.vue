<template>
  <div
    id="object-table"
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
          v-if="oList.length < 500"
          v-model="isPaginated"
        >
          {{ $t('message.table.paginated') }}
        </b-switch>
      </div>
      <FolderUploadForm dropelement="object-table" />
      <ContainerDownloadLink />
      <b-field class="control searchBox">
        <b-input
          v-model="searchQuery"
          :placeholder="$t('message.searchBy')"
        />
      </b-field>
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
    >
      <template slot-scope="props">
        <b-table-column
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
          {{ getHumanReadableDate(props.row.last_modified) }}
        </b-table-column>
        <b-table-column
          sortable
          field="bytes"
          :label="$t('message.table.size')"
        >
          {{ localHumanReadableSize(props.row.bytes) }}
        </b-table-column>
        <b-table-column
          field="url"
          label=""
          width="110"
        >
          <a
            v-if="props.row.bytes < 1073741824"
            :href="props.row.url"
            target="_blank"
            :alt="$t('message.downloadAlt') + ' ' + props.row.name"
          >
            <b-icon
              icon="cloud-download"
              size="is-small"
            /> {{ $t('message.download') }}
          </a>
          <a
            v-else-if="allowLargeDownloads"
            :href="props.row.url"
            target="_blank"
            :alt="$t('message.downloadAlt') + ' ' + props.row.name"
          >
            <b-icon
              icon="cloud-download"
              size="is-small"
            /> {{ $t('message.download') }}
          </a>
          <a
            v-else
            :alt="$t('message.downloadAltLarge') + ' ' + props.row.name"
            @click="confirmDownload ()"
          >
            <b-icon
              icon="cloud-download"
              size="is-small"
            /> {{ $t('message.download') }}
          </a>
        </b-table-column>
      </template>
      <template
        slot="detail"
        slot-scope="props"
      >
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
                icon="cloud-download"
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
                icon="cloud-download"
                size="is-small"
              /> {{ $t('message.downloadLink') }}
            </a>
            <a
              v-else
              :alt="$t('message.downloadAltLarge') + ' ' + props.row.name"
              @click="confirmDownload ()"
            >
              <b-icon
                icon="cloud-download"
                size="is-small"
              /> {{ $t('message.downloadLink') }}
            </a>
          </li>
        </ul>
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
import { getObjects } from "@/common/api";
import { getHumanReadableSize } from "@/common/conv";
import debounce from "lodash/debounce";
import ContainerDownloadLink from "@/components/ContainerDownloadLink";
import FolderUploadForm from "@/components/FolderUpload";

export default {
  name: "Objects",
  components: {
    ContainerDownloadLink,
    FolderUploadForm,
  },
  data: function () {
    return {
      oList: [],
      objects: [],
      selected: undefined,
      isPaginated: true,
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
      this.oList = this.objects;
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
    },
    checkLargeDownloads: function () {
      if (document.cookie.match("ENA_DL")) {
        this.allowLargeDownloads = true;
      }
    },
    addPageToURL: function (pageNumber) {
      this.$router.push("?page=" + pageNumber);
    },
    confirmDownload: function () {
      // Snackbar for enabling large downloads for the duration of the
      // session
      this.$snackbar.open({
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
    filter: function () {
      var name_re = new RegExp(this.searchQuery, "i");
      this.oList = this.objects.filter(
        element => element.name.match(name_re)
      );
    },
  },
};
</script>
