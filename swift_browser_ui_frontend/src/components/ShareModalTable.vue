<template>
  <c-data-table
    v-if="tableData.length > 0"
    :data.prop="tableData"
    :headers.prop="headers"
    :no-data-text="$t('message.encrypt.empty')"
    :pagination.prop="pagination"
    :footer-options.prop="footer"
  />
</template>

<script>
import { removeAccessControlMeta } from "@/common/api";

export default {
  name: "ShareModalTable",
  props: ["sharedDetails", "folderName", "accessRights"],

  data: function () {
    return {
      tableData: [],
    };
  },
  computed: {
    projectId () {
      return this.$store.state.active.id;
    },
    headers () {
      return [
        {
          key: "projectId",
          value: this.$t("message.share.project_id"),
          width: "50%",
          sortable: true,
          align: "start",
          component: {
            tag: "div",
            params: {
              style: {
                fontSize: "0.875rem",
              },
            },
          },
        },
        {
          key: "permissions",
          value: this.$t("message.share.permissions"),
          width: "30%",
          sortable: false,
        },
        {
          key: "remove",
          value: null,
          sortable: false,
          children: [
            {
              value: this.$t("message.remove"),
              component: {
                tag: "c-button",
                params: {
                  text: true,
                  size: "small",
                  title: this.$t("message.remove"),
                  onClick: ({ data }) => {
                    this.$emit("removeSharedFolder", data);
                    this.deleteFolderShare(data);
                  },
                },
              },
            },
          ],
        },
      ];
    },
    pagination() {
      return {
        itemCount: this.tableData.length,
        itemsPerPage: 50,
        currentPage: 1,
      };
    },
    footer() {
      return {
        hideDetails: true,
      };
    },
  },
  watch: {
    sharedDetails: function () {
      this.getTableData();
    },
  },
  methods: {
    getTableData: function () {
      this.tableData = this.sharedDetails.map(item => ({
        projectId: {value: item.sharedTo},
        permissions: {
          value: null,
          children: [
            {
              component: {
                tag: "c-select",
                params: {
                  style: {
                    fontSize: "0.875rem",
                    marginTop: "1rem",
                  },
                  items: this.accessRights,
                  value: item.access.length > 1 ? this.accessRights[1]
                    : this.accessRights[0],
                  onChangeValue: (e) => this.editAccessRight(e, item.sharedTo),
                },
              },
            },
          ],
        },
      }));
    },
    editAccessRight: async function (e, sharedProjectId) {
      const rights = [];
      const val = e.detail.value;
      if (val === "read") rights.push("r");
      else rights.push("r", "w");

      await this.$store.state.client.shareEditAccess(
        this.projectId,
        this.folderName,
        [sharedProjectId],
        rights,
      );
    },
    deleteFolderShare: function (folderData) {
      removeAccessControlMeta(
        this.projectId,
        this.folderName,
      ).then(
        () => {
          this.$store.state.client.shareDeleteAccess(
            this.projectId,
            this.folderName,
            [folderData.projectId.value],
          );
        },
      );
    },
  },
};
</script>

<style lang="scss" scoped>
c-data-table {
  color: var(--csc-dark-grey);
  margin-top: 1rem;
}

</style>
