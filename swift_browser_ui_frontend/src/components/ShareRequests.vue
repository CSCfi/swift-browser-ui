<template>
  <div id="requested-shares-table">
    <b-field
      grouped
      grouped-multiline
    >
      <b-select
        v-model="perPage"
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
    </b-field>
    <b-table
      focusable
      narrowed
      detailed
      default-sort="name"
      :data="requestedSharesList"
      :selected.sync="selected"
      :current-page.sync="currentPage"
      :paginated="true"
      :per-page="perPage"
      :pagination-simple="true"
      :default-sort-direction="defaultSortDirection"
    >
      <template slot-scope="props">
        <b-table-column
          sortable
          field="container"
          label="container"
        >
          {{ props.row.container }}
        </b-table-column>
        <b-table-column
          sortable
          field="owner"
          label="owner"
        >
          {{ props.row.owner }}
        </b-table-column>
        <b-table-column
          sortable
          field="created"
          label="created"
        >
          {{ getHumanReadableDate( props.row.date ) }}
        </b-table-column>
        <b-table-column
          field="delete"
          label=""
          width="40"
        >
          <b-button
            type="is-danger"
            @click="deleteShareRequest(props.row.container, props.row.owner)"
            outlined
            size="is-small"
          >
            Cancel
          </b-button>
        </b-table-column>
      </template>
    </b-table>
  </div>
</template>

<script>
export default {
  name: "ShareRequests",
  data () {
    return {
      perPage: 10,
      requestedSharesList: [],
      selected: undefined,
      currentPage: 0,
      defaultSortDirection: "asc",
    };
  },
  beforeMount () {
    this.getShareRequests();
  },
  methods: {
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
    getShareRequests: function () {
      this.$store.state.requestClient.listMadeRequests(
        this.$route.params.user
      ).then(
        (ret) => {this.requestedSharesList = ret;}
      );
    },
    deleteShareRequest: function(
      container,
      owner
    ) {
      this.$store.state.requestClient.shareDeleteAccess(
        this.$route.params.user,
        container,
        owner,
      );
    },
  },
};
</script>
