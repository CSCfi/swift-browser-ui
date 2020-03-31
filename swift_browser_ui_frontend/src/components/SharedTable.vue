<template>
  <div 
    id="shared-table"
    class="column"
  >
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
        <b-table-column
          field="download"
          label=""
          width="40"
        >
          <ContainerDownloadLink 
            class="is-small"
            :project="props.row.owner"
            :container="props.row.container"
          />
        </b-table-column>
        <b-table-column
          field="copy"
          label=""
          width="40"
        >
          <ReplicateContainerButton
            :container="props.row.container"
            :smallsize="true"
          />
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

<style scoped>
#shared-table {
  width: 100%;
}
</style>

<script>
import delay from "lodash/delay";
import ContainerDownloadLink from "@/components/ContainerDownloadLink";
import ReplicateContainerButton from "@/components/ReplicateContainer";

export default {
  name: "SharedTable",
  components: {
    ContainerDownloadLink,
    ReplicateContainerButton,
  },
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
      if (this.$store.state.client) {
        this.$store.state.client.getAccess(
          this.$route.params.project
        ).then(
          (ret) => {this.sharedList = ret;}
        );
      }
      else {
        delay(this.getSharedContainers, 100);
      }
    },
    getConAddr: function (row) {
      return "/browse/shared/".concat(
        this.$route.params.project,
        "/", row.owner,
        "/", row.container
      );
    },
  },
};
</script>
