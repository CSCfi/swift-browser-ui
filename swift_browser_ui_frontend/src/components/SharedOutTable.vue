<template>
  <div 
    id="shared-out-table"
    class="column"
  >
    <div class="field is-grouped">
      <p class="control">
        <b-select
          data-testid="bucketsPerPage"
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
      </p>
      <div class="field has-addons">
        <p class="control">
          <b-button
            type="is-primary"
            outlined
            @click="$router.push({
              name: 'Sharing'
            })"
          >
            {{ $t('message.share.new_share_button') }}
          </b-button>
        </p>
        <p class="control">
          <ACLDiscoverButton @synced="getSharedContainers()" />
        </p>
      </div>
    </div>
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
      <b-table-column
        sortable
        field="name"
        :label="$t('message.table.name')"
      >
        <template #default="props">
          <span class="has-text-weight-bold">
            <b-icon
              icon="folder"
              size="is-small"
            />
            {{ props.row }}
          </span>
        </template>
      </b-table-column>
      <b-table-column
        field="delete"
        label=""
        width="100"
      >
        <template #default="props">
          <b-button
            v-if="selected == props.row"
            type="is-danger"
            size="is-small"
            icon-left="delete"
            outlined
            inverted
            @click="deleteContainerShare(props.row)"
          >
            {{ $t('message.share.revoke') }}
          </b-button>
          <b-button
            v-else
            type="is-danger"
            size="is-small"
            icon-left="delete"
            outlined
            @click="deleteContainerShare(props.row)"
          >
            {{ $t('message.share.revoke') }}
          </b-button>
        </template>
      </b-table-column>
      <template 
        #detail="props"
      >
        <SharedDetails
          :container="props.row"
        />
      </template>
      <template #empty>
        <p class="emptyTable">
          {{ $t('message.emptyShared') }}
        </p>
      </template>
    </b-table>
  </div>
</template>

<script>
import SharedDetails from "@/components/SharedDetails";
import ACLDiscoverButton from "@/components/ACLDiscover";
import { removeAccessControlMeta } from "@/common/api";
import delay from "lodash/delay";

export default {
  name: "SharedOutTable",
  components: {
    SharedDetails,
    ACLDiscoverButton,
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
          this.$route.params.project,
        ).then(
          (ret) => {this.sharedOutList = ret;},
        );
      }
      else {
        delay(this.getSharedContainers, 100);
      }
    },
    deleteContainerShare: function (container) {
      removeAccessControlMeta(container).then(
        () => {
          this.$store.state.client.shareContainerDeleteAccess(
            this.$route.params.project,
            container,
          ).then(() => {
            this.$buefy.toast.open({
              duration: 5000,
              message: this.$t("message.share.success_delete"),
              type: "is-success",
            });
          });
        },
      );
    },
  },
};
</script>

<style scoped>
#shared-out-table {
  width: 100%;
}
.emptyTable {
  text-align: center;
  margin-top: 5%;
  margin-bottom: 5%;
}
</style>
