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
  props: ["sharedDetails", "folderName", "removeSharedFolder"],

  data: function () {
    return {
      tableData: [],
    };
  },
  watch: {
    sharedDetails: function () {
      this.getTableData();
    },
  },
  computed: {
    projectId () {
      return this.$route.params.project;
    },
    headers () {
      return [
        {
          key: "projectId",
          value: this.$t("message.share.permissions"),
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
          value: this.$t("message.share.project_id"),
          width: "30%",
          sortable: false,
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
                    this.removeSharedFolder(data);
                    this.deleteFolderShare();
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
  methods: {
    getTableData: function () {
      this.tableData = this.sharedDetails.map(item => ({
        projectId: {value: item.sharedTo},
        permissions: {
          value: item.access.length > 1 ?
            this.$t("message.share.write_perm")
            : this.$t("message.share.write_perm")},
      }));
    },
    deleteFolderShare: function () {
      removeAccessControlMeta(
        this.projectId,
        this.folderName,
      ).then(
        () => {
          this.$store.state.client.shareContainerDeleteAccess(
            this.projectId,
            this.folderName,
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

<style lang="scss" scoped>
c-data-table {
  color: var(--csc-dark-grey);
}

</style>
