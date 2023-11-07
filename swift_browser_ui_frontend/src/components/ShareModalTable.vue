<template>
  <c-container>
    <h3 class="title is-5">
      {{ $t("message.share.shared_table_title") }}
    </h3>
    <!-- Footer options needs to be in CamelCase,
    because csc-ui wont recognise it otherwise. -->
    <!-- eslint-disable-->
    <c-alert
      v-show="clickedPermChange"
      id="perm-change-alert"
      type="warning"
    >
      {{ $t("message.share.perm_change_text") +
      "(" + getPermName(newPerms) + ")" +
      $t("message.share.perm_change_text2") }}
      <c-card-actions justify="end">
        <c-button
          outlined
          @click="clearPermChange"
          @keyup.enter="clearPermChange"
        >
          {{ $t("message.share.cancel") }}
        </c-button>
        <c-button
          @click="confirmPermChange"
          @keyup.enter="confirmPermChange"
        >
          {{ $t("message.share.perm_change_confirm") }}
        </c-button>
      </c-card-actions>
    </c-alert>
    <c-alert
      v-show="clickedDelete"
      id="delete-alert"
      type="warning"
    >
      {{ $t("message.share.share_delete_text") }}
      <c-card-actions justify="end">
        <c-button
          outlined
          @click="clearDelete"
          @keyup.enter="clearDelete"
        >
          {{ $t("message.share.cancel") }}
        </c-button>
        <c-button
          @click="confirmDelete"
          @keyup.enter="confirmDelete"
        >
          {{ $t("message.share.share_delete_confirm") }}
        </c-button>
      </c-card-actions>
    </c-alert>
    <c-data-table
      :key="newPerms"
      id="shared-projects-table"
      v-if="tableData.length > 0"
      :data.prop="tableData"
      :headers.prop="headers"
      :no-data-text="$t('message.encrypt.empty')"
      :pagination.prop="pagination"
      :footerOptions.prop="footer"
      horizontal-scrolling
    />
    <!-- eslint-enable-->
  </c-container>
</template>

<script>
import { toRaw } from "vue";
import {
  modifyAccessControlMeta,
  removeAccessControlMeta,
  GET,
} from "@/common/api";
import { DEV } from "@/common/conv";
import { mdiDelete } from "@mdi/js";

export default {
  name: "ShareModalTable",
  props: ["sharedDetails", "folderName", "accessRights"],

  data: function () {
    return {
      tableData: [],
      clickedPermChange: false,
      newPerms: [],
      sharedTo: "",
      clickedDelete: false,
      toDelete: {},
    };
  },
  computed: {
    projectId () {
      return this.$store.state.active.id;
    },
    shareModalOpen () {
      return this.$store.state.openShareModal;
    },
    headers () {
      return [
        {
          key: "projectId",
          value: this.$t("message.share.share_id"),
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
          key: "delete",
          value: null,
          sortable: false,
          children: [
            {
              value: this.$t("message.delete"),
              component: {
                tag: "c-button",
                params: {
                  text: true,
                  size: "small",
                  title: this.$t("message.delete"),
                  path: mdiDelete,
                  onClick: ({ data }) => {
                    this.toDelete = data;
                    this.clickedDelete = true;
                    document.getElementById("delete-alert")
                      .scrollTo(0, 0);
                  },
                  onKeyUp: (e) => {
                    if(e.keyCode === 13) {
                      // Get the row element of item that is to be removed
                      const row = e.target.closest("tr");
                      if (row !== undefined) {
                        const data = {
                          projectId: {value: row.children[0]?.innerText},
                        };
                        this.toDelete = data;
                        this.clickedDelete = true;
                        document.getElementById("delete-alert")
                          .scrollTo(0, 0);
                      }
                    }
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
    shareModalOpen: function () {
      if (!this.shareModalOpen) {
        //clear alerts on closed modal
        this.clearPermChange();
        this.clearDelete();
      }
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
                    width: "100%",
                    fontSize: "0.875rem",
                    marginTop: "1rem",
                  },
                  items: this.accessRights,
                  value: item.access.length > 0
                    ? (
                      item.access.length > 1
                        ? this.accessRights[2]
                        : this.accessRights[1])
                    : this.accessRights[0],
                  onChangeValue: (e) =>  {
                    this.newPerms = this.getPermArray(e.detail.value);
                    if (this.getPermName(this.newPerms)
                      !== this.getPermName(toRaw(item.access))) {
                      //if different than current perms chosen
                      this.sharedTo = item.sharedTo;
                      this.clickedPermChange = true;
                      document.getElementById("perm-change-alert")
                        .scrollTo(0, 0);
                    } else {
                      this.clearPermChange();
                    }
                  },
                  onClick: ({ event }) => {
                    const wrapper =
                      document.getElementById("share-card-modal-content");
                    let wrapperPosition = wrapper.getBoundingClientRect();
                    let targetPosition = event.target.getBoundingClientRect();
                    let diff = wrapperPosition.bottom - targetPosition.bottom;
                    const ul = event.target.shadowRoot.
                      activeElement.parentNode.nextSibling.querySelector("ul");
                    setTimeout(() => {
                      const ulPosition = ul.getBoundingClientRect();
                      if (diff < ulPosition.height) {
                        wrapper.scrollBy(0, ulPosition.height - diff);
                      }
                    }, 150);
                  },
                },
              },
            },
          ],
        },
      }));
    },
    getPermName(array) {
      return array.length > 1 ? this.accessRights[2].name
        : (this.accessRights[1].value[0] === array[0] ?
          this.accessRights[1].name : this.accessRights[0].name);
    },
    clearPermChange() {
      this.clickedPermChange = false;
      this.newPerms = [];
      this.sharedTo = "";
    },
    async confirmPermChange() {
      await this.editAccessRight(this.sharedTo);
      this.clearPermChange();
      this.getTableData();
    },
    getPermArray(val) {
      if (!val) return [];
      if (val === "view") return ["v"];
      else if (val === "read") return ["r"];
      else return ["r", "w"];
    },
    editAccessRight: async function (sharedProjectId) {

      await modifyAccessControlMeta(
        this.projectId,
        this.folderName,
        [sharedProjectId],
        this.newPerms,
      );

      await modifyAccessControlMeta(
        this.projectId,
        `${this.folderName}_segments`,
        [sharedProjectId],
        this.newPerms,
      );

      await this.$store.state.client.shareEditAccess(
        this.projectId,
        this.folderName,
        [sharedProjectId],
        this.newPerms,
      );

      await this.$store.state.client.shareEditAccess(
        this.projectId,
        `${this.folderName}_segments`,
        [sharedProjectId],
        this.newPerms,
      );
      let projectIDs = await this.$store.state.client.projectCheckIDs(
        sharedProjectId,
      );

      let signatureUrl = new URL("/sign/3600", document.location.origin);
      signatureUrl.searchParams.append("path", `/cryptic/${this.$store.state.active.name}/${this.folderName}`);
      let signed = await GET(signatureUrl);
      signed = await signed.json();

      let whitelistUrl = new URL(this.$store.state.uploadEndpoint.concat(
        `/cryptic/${this.$store.state.active.name}/${this.folderName}`,
      ));
      whitelistUrl.searchParams.append(
        "valid",
        signed.valid,
      );
      whitelistUrl.searchParams.append(
        "signature",
        signed.signature,
      );

      if (this.newPerms.length === 1 && this.newPerms[0] === "v") {
        await fetch(
          whitelistUrl,
          {
            method: "DELETE",
            body: JSON.stringify([projectIDs.name]),
          },
        ).then(() => {
          if (DEV) console.log(`Deleted sharing whitelist entry for ${sharedProjectId}`);
        });
      } else {
        await fetch(
          whitelistUrl,
          {
            method: "PUT",
            body: JSON.stringify([projectIDs]),
          },
        ).then(() => {
          if (DEV) console.log(`Edited sharing whitelist entry for ${sharedProjectId}`);
        });
      }
      this.$emit("updateSharedFolder");
    },
    confirmDelete: async function () {
      this.$emit("removeSharedFolder", this.toDelete);
      await this.deleteFolderShare(this.toDelete);
      this.clearDelete();
    },
    clearDelete: function () {
      this.clickedDelete = false;
      this.toDelete = {};
    },
    deleteFolderShare: async function (folderData) {
      await removeAccessControlMeta(
        this.projectId,
        this.folderName,
      );

      await removeAccessControlMeta(
        this.projectId,
        `${this.folderName}_segments`,
      );

      await this.$store.state.client.shareDeleteAccess(
        this.projectId,
        this.folderName,
        [folderData.projectId.value],
      );

      await this.$store.state.client.shareDeleteAccess(
        this.projectId,
        `${this.folderName}_segments`,
        [folderData.projectId.value],
      );

      let projectIDs = await this.$store.state.client.projectCheckIDs(
        folderData.projectId.value,
      );

      let signatureUrl = new URL("/sign/3600", document.location.origin);
      signatureUrl.searchParams.append("path", `/cryptic/${this.$store.state.active.name}/${this.folderName}`);
      let signed = await GET(signatureUrl);
      signed = await signed.json();

      let whitelistUrl = new URL(this.$store.state.uploadEndpoint.concat(
        `/cryptic/${this.$store.state.active.name}/${this.folderName}`,
      ));
      whitelistUrl.searchParams.append(
        "valid",
        signed.valid,
      );
      whitelistUrl.searchParams.append(
        "signature",
        signed.signature,
      );

      fetch(
        whitelistUrl,
        {
          method: "DELETE",
          body: JSON.stringify([
            projectIDs.name,
          ]),
        },
      ).then(() => {
        if (DEV) console.log(
          `Deleted sharing whitelist entry for ${folderData.projectId.value}`,
        );
      },
      ).finally(() => {
        if (DEV) console.log(
          `Share deletion for ${folderData.projectId.value} finished.`,
        );
      });
    },
  },
};
</script>

<style lang="scss" scoped>

h3 {
  margin-top: 1rem;
}

c-data-table {
  color: var(--csc-dark);
  margin-top: 1rem;
  padding-bottom: 4rem;
}

c-container {
  min-width: 0;
}
</style>
