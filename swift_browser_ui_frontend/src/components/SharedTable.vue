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
        data-testid="containersPerPage"
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
      <b-table-column
        sortable
        field="name"
        :label="$t('message.table.name')"
      >
        <template #default="props">
          <span clss="has-text-weight-bold">
            <b-icon
              icon="folder"
              size="is-small"
            />
            {{ props.row.container | truncate(80) }}
          </span>
        </template>
      </b-table-column>
      <b-table-column
        field="owner"
        :label="$t('message.table.owner')"
        sortable
      >
        <template #default="props">
          {{ props.row.owner }}
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
                :project="props.row.owner"
                :inverted="true"
                :container="props.row.container"
              />
              <ContainerDownloadLink
                v-else
                class="is-small"
                :project="props.row.owner"
                :container="props.row.container"
              />
            </p>
            <p class="control">
              <ReplicateContainerButton
                v-if="selected==props.row"
                :inverted="true"
                :project="props.row.owner"
                :container="props.row.container"
                :smallsize="true"
              />
              <ReplicateContainerButton
                v-else
                :project="props.row.owner"
                :container="props.row.container"
                :smallsize="true"
              />
            </p>
          </div>
        </template>
      </b-table-column>
      <template #empty>
        <p class="emptyTable">
          {{ $t('message.emptyShared') }}
        </p>
      </template>
    </b-table>
  </div>
</template>

<script>
import { truncate } from "@/common/conv";
import delay from "lodash/delay";
import ContainerDownloadLink from "@/components/ContainerDownloadLink";
import ReplicateContainerButton from "@/components/ReplicateContainer";

export default {
  name: "SharedTable",
  components: {
    ContainerDownloadLink,
    ReplicateContainerButton,
  },
  filters: {
    truncate,
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
          this.$route.params.project,
        ).then(
          (ret) => {this.sharedList = ret;},
        );
      }
      else {
        delay(this.getSharedContainers, 100);
      }
    },
    getConAddr: function (row) {
      return {
        name: "SharedObjects",
        params: {
          project: this.$route.params.project,
          owner: row.owner,
          container: row.container,
        },
      };
    },
  },
};
</script>

<style scoped>
#shared-table {
  width: 100%;
}
.emptyTable {
  text-align: center;
  margin-top: 5%;
  margin-bottom: 5%;
}
</style>
