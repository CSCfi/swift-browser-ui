<template>
  <div id="shared-table">
    <b-field
      grouped
      group-multiline
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
      hoverable
      narrowed
      default-sort="name"
      :data="sharedList"
      :selected.sync="selected"
      :current-page.sync="currentPage"
      :paginated="true"
      :per-page="perPage"
      :pagination-simple="true"
      :default-sort-direction="defaultSortDirection"
      @dblclick="(row) => $router.push(getConAddr(row))"
      @keyup.native.enter="$router.push(getConAddr(selected))"
      @keyup.native.space="$router.push(getConAddr(selected))"
    >
      <template slot-scope="props">
        <b-table-column
          sortable
          field="name"
          :label="$t('message.table.name')"
        >
          <span clss="has-text-weight-bold">
            <b-icon
              icon="folder"
              size="is-small"
            />
            {{ props.row.container }}
          </span>
        </b-table-column>
        <b-table-column
          field="owner"
          :label="$t('message.table.owner')"
          sortable
        >
          {{ props.row.owner }}
        </b-table-column>
      </template>
      <template slot="empty">
        <p
          style="text-align:center;margin-top:5%;margin-bottom:5%"
        >
          {{ $t('message.emptyShared') }}
        </p>
      </template>
    </b-table>
  </div>
</template>

<script>
export default {
  data: function () {
    return {
      sharedList: [],
      selected: undefined,
      perPage: 15,
      defaultSortDirection: "asc",
      currentPage: 1,
    };
  },
  beforeMount () {
    this.getSharedContainers();
  },
  methods: {
    getSharedContainers: function () {
      this.$store.state.client.get_access(
        this.$route.params.user
      ).then(
        (ret) => {this.sharedList = ret;}
      );
    },
    getConAddr: function (row) {
      return "/shared/".concat(
        this.$route.params.user,
        "/", row.owner,
        "/", row.container
      );
    },
  },
};
</script>
