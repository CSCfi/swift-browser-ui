<template>
  <div 
    id="shared-out-table"
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
      detailed
      default-sort="name"
      :data="sharedOutList"
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
            {{ props.row }}
          </span>
        </b-table-column>
      </template>
      <template 
        slot="detail"
        slot-scope="props"
      >
        <SharedDetails
          :container="props.row"
        />
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
#shared-out-table {
  width: 100%;
}
</style>

<script>
import SharedDetails from "@/components/SharedDetails";
import delay from "lodash/delay";

export default {
  name: "SharedOutTable",
  components: {
    SharedDetails,
  },
  data: function () {
    return {
      sharedOutList: [],
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
        this.$store.state.client.getShare(
          this.$route.params.project
        ).then(
          (ret) => {this.sharedOutList = ret;}
        );
      }
      else {
        delay(this.getSharedContainers, 100);
      }
    },
  },
};
</script>
