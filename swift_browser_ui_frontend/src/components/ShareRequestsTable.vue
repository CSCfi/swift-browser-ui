<template>
  <div id="requested-shares-table">
    <hr>
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
          :label="$t('message.share.container')"
        >
          {{ props.row.container }}
        </b-table-column>
        <b-table-column
          sortable
          field="owner"
          :label="$t('message.share.owner')"
        >
          {{ props.row.owner }}
        </b-table-column>
        <b-table-column
          sortable
          field="created"
          :label="$t('message.share.created')"
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
            outlined
            size="is-small"
            @click="deleteShareRequest(props.row.container, props.row.owner)"
          >
            {{ $t('message.share.cancel') }}
          </b-button>
        </b-table-column>
      </template>
      <template slot="empty">
        <p
          style="text-align:center;margin-top:5%;margin-bottom:5%"
        >
          {{ $t('message.emptyRequested') }}
        </p>
      </template>
    </b-table>
  </div>
</template>

<style scoped>
#requested-shares-table {
  margin-top: 20px;
}
</style>


<script>
import delay from "lodash/delay";

export default {
  name: "ShareRequestsTable",
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
      if (this.$store.state.client) {
        this.$store.state.requestClient.listMadeRequests(
          this.$route.params.project
        ).then(
          (ret) => {this.requestedSharesList = ret;}
        );
      }
      else {
        delay(this.getShareRequests, 100);
      }
    },
    deleteShareRequest: function(
      container,
      owner
    ) {
      this.$store.state.requestClient.shareDeleteAccess(
        this.$route.params.project,
        container,
        owner,
      ).then(() => {
        this.$router.go();
      });
    },
  },
};
</script>
