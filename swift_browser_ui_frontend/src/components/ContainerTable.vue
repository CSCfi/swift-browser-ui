<template>
  <c-data-table
    id="contable-tags"
    :data.prop="containers"
    :headers.prop="hideTags ?
      headers.filter(header => header.key !== 'tags'): headers"
    :pagination.prop="disablePagination ? null : paginationOptions"
    :hide-footer="disablePagination"
    :footer-options.prop="footerOptions"
    :no-data-text="getEmptyText()"
    :sort-by="sortBy"
    :sort-direction="sortDirection"
    external-data
    @paginate="getPage"
    @sort="onSort"
  />
</template>

<script>
import { getHumanReadableSize, truncate, sortObjects } from "@/common/conv";
import {
  mdiTrayArrowDown,
  mdiShareVariantOutline,
  mdiDotsHorizontal,
  mdiFolder,
} from "@mdi/js";
import {
  toggleEditTagsModal,
  getSharingContainers,
  getSharedContainers,
  getAccessDetails,
  toggleCopyFolderModal,
} from "@/common/globalFunctions";
import { toRaw } from "vue";
import { swiftDeleteContainer } from "@/common/api";
import { getDB } from "@/common/db";

export default {
  name: "ContainerTable",
  props: {
    conts: {
      type: Array,
      default: () => {return [];},
    },
    disablePagination: {
      type: Boolean,
      default: false,
    },
    hideTags: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      containers: [],
      direction: "asc",
      footerOptions: {
        itemsPerPageOptions: [5, 10, 15, 20, 25],
      },
      paginationOptions: {
        itemCount: 0,
        itemsPerPage: 10,
        currentPage: 1,
        startFrom: 0,
        endTo: 9,
      },
      sortBy: "name",
      sortDirection: "asc",
      paginationTextOverrides: {
        itemsPerPageText: this.$t("message.table.itemsPerPage"),
        nextPage: this.$t("message.table.nextPage"),
        prevPage: this.$t("message.table.prevPage"),
        pageText:
          ({ start, end, count }) => start + " - " + end + " / " + count + "",
        pageOfText:
          ({ pageNumber, count }) =>
            this.$t("message.table.page") + pageNumber + " / " + count + "",
      },
    };
  },
  computed: {
    locale () {
      return this.$i18n.locale;
    },
    active() {
      return this.$store.state.active;
    },
  },
  watch: {
    disablePagination() {
      this.getPage();
    },
    hideTags() {
      this.getPage();
    },
    conts() {
      this.getPage();
    },
    locale() {
      this.setHeaders();
      this.handlePaginationText();
      this.getPage();
    },
  },
  created() {
    this.setHeaders();
    this.handlePaginationText();
  },
  methods: {
    async getSharingContainers() {
      return this.sharingClient
        ? this.sharingClient.getShare(this.active.id)
        : [];
    },
    getSharedContainers () {
      return this.sharingClient
        ? this.sharingClient.getAccess(this.$route.params.project)
        : [];
    },
    async getPage () {
      let offset = 0;
      let limit = this.conts.length;

      if (!this.disablePagination || this.conts.length > 500) {
        offset =
          this.paginationOptions.currentPage
          * this.paginationOptions.itemsPerPage
          - this.paginationOptions.itemsPerPage;

        limit = this.paginationOptions.itemsPerPage;
      }
      const sharingContainers = await getSharingContainers(this.active.id);
      const sharedContainers = await getSharedContainers(this.active.id);

      const getSharedStatus = (folderName) => {
        if (sharingContainers.indexOf(folderName) > -1) {
          return this.$t("message.table.sharing");
        } else if (sharedContainers.findIndex(
          cont => cont.container === folderName) > -1) {
          return this.$t("message.table.shared");
        }
        return "";
      };

      // Map the 'accessRights' to the container if it's a shared container
      const mappedContainers = await Promise.all(this.conts.map(async(cont) => {
        const sharedDetails = cont.owner ? await getAccessDetails(
          this.$route.params.project,
          cont.container,
          cont.owner) : null;
        const accessRights = sharedDetails ? sharedDetails.access : null;
        return sharedDetails && accessRights ?
          {...cont, accessRights} : {...cont};
      }));

      this.containers = mappedContainers.slice(offset, offset + limit).reduce((
        items,
        item,
      ) => {
        items.push({
          name: {
            value: truncate(item.name),
            component: {
              tag: "c-link",
              params: {
                href: "javascript:void(0)",
                color: "dark-grey",
                path: mdiFolder,
                iconFill: "primary",
                iconStyle: {
                  marginRight: "1rem",
                },
                onClick: () => {
                  if(item.owner) {
                    this.$router.push({
                      name: "SharedObjects",
                      params: {
                        container: item.name,
                        owner: item.owner,
                      },
                    });
                  } else {
                    this.$router.push({
                      name: "ObjectsView",
                      params: {
                        container: item.name,
                      },
                    });
                  }
                },
              },
            },
          },
          items: {
            value: item.count,
          },
          size: {
            value: getHumanReadableSize(item.bytes),
          },
          ...(this.hideTags ? {} : {
            tags: {
              value: null,
              children: [
                ...(item.tags || []).map((tag, index) => ({
                  key: "tag_" + index + "",
                  value: tag,
                  component: {
                    tag: "c-tag",
                    params: {
                      flat: true,
                    },
                  },
                })),
                ...(item.tags && !item.tags.length
                  ? [{ key: "no_tags", value: "-" }]
                  : []),
              ],
            },
          }),
          sharing: {
            value: getSharedStatus(item.name),
          },
          actions: {
            value: null,
            sortable: null,
            align: "end",
            children: [
              {
                value: this.$t("message.download"),
                component: {
                  tag: "c-button",
                  params: {
                    text: true,
                    size: "small",
                    title: this.$t("message.download"),
                    href: "/download/".concat(
                      this.$route.params.project,
                      "/",
                      item.name,
                    ),
                    target: "_blank",
                    path: mdiTrayArrowDown,
                  },
                },
              },
              // Share button is disabled for Shared (with you) Folders
              {
                value: this.$t("message.share.share"),
                component: {
                  tag: "c-button",
                  params: {
                    text: true,
                    size: "small",
                    title: this.$t("message.share.share"),
                    path: mdiShareVariantOutline,
                    onClick: (item) => {
                      this.$store.commit("toggleShareModal", true);
                      this.$store.commit(
                        "setFolderName", item.data.name.value);
                    },
                    onKeyUp: (event) => {
                      if(event.keyCode === 13) {
                        this.$store.commit("toggleShareModal", true);
                        this.$store.commit(
                          "setFolderName", item.data.name.value);
                      }
                    },
                    disabled: item.owner,
                  },
                },
              },
              {
                value: null,
                component: {
                  tag: "c-menu",
                  params: {
                    items: [
                      {
                        name: this.$t("message.copy"),
                        action: item.owner
                          ? () => toggleCopyFolderModal(item.name, item.owner)
                          : () => toggleCopyFolderModal(item.name),
                        disabled: !item.bytes ? true : false,
                      },
                      {
                        name: this.$t("message.editTags"),
                        action: () => toggleEditTagsModal(null, item.name),
                      },
                      {
                        name: this.$t("message.delete"),
                        action: () => this.delete(
                          item.name, item.count,
                        ),
                        disabled: item.owner && item.accessRights.length > 1,
                      },
                    ],
                    customTrigger: {
                      value: this.$t("message.options"),
                      disabled: true,
                      component: {
                        tag: "c-button",
                        params: {
                          text: true,
                          path: mdiDotsHorizontal,
                          title: this.$t("message.options"),
                          size: "small",
                          disabled: item.owner
                            && item.accessRights.length === 1,
                        },
                      },
                    },
                  },
                },
              },
            ],
          },
        });
        return items;
      }, []);

      this.paginationOptions = {
        ...this.paginationOptions,
        itemCount: this.conts.length,
      };
    },
    async onSort(event) {
      this.sortBy = event.detail.sortBy;
      this.sortDirection = event.detail.direction;

      if (this.sortBy === "sharing") {
        const sharingContainers = await getSharingContainers(this.active.id);
        const sharedContainers = await getSharedContainers(this.active.id);

        let allSharing = this.conts.map(x => sharingContainers.includes(x.name)
          ? this.$t("message.table.sharing") : "");
        let allShared = this.conts.map(x =>
          sharedContainers.some(cont => cont.container === x.name)
            ? this.$t("message.table.shared") : "");

        let combined = allSharing.map((value, idx) =>
          value !== "" ? value : allShared[idx]);
        this.conts.forEach((cont, idx) => (cont.sharing = combined[idx]));
      }

      // Use toRaw to mutate the original array, not the proxy
      sortObjects(toRaw(this.conts), this.sortBy, this.sortDirection);
      this.getPage();
    },
    setHeaders() {
      this.headers = [
        {
          key: "name",
          value: this.$t("message.table.name"),
          sortable: true,
        },
        {
          key: "items",
          value: this.$t("message.table.items"),
          sortable: true,
        },
        {
          key: "size",
          value: this.$t("message.table.size"),
          sortable: true,
        },
        {
          key: "tags",
          value: this.$t("message.table.tags"),
          sortable: true,
        },
        {
          key: "sharing",
          value: this.$t("message.table.shared_status"),
          sortable: true,
        },
        {
          key: "actions",
          align: "end",
          value: null,
          sortable: false,
          ariaLabel: "test",
        },
      ];
    },
    delete: function (container, objects) {
      if (objects > 0) { //if container not empty
        document.querySelector("#container-error-toasts").addToast(
          {
            progress: false,
            type: "error",
            duration: 6000,
            message: this.$t("message.container_ops.deleteNote"),
          },
        );
      } else { //delete empty folder without confirmation
        document.querySelector("#container-toasts").addToast(
          { progress: false,
            type: "success",
            message: this.$t("message.container_ops.deleteSuccess")},
        );
        const projectID = this.$route.params.project;
        swiftDeleteContainer(
          projectID,
          container,
        ).then(async () => {
          await getDB().containers
            .where({
              projectID,
              name: container,
            })
            .delete();
        }).then(() => this.$emit("delete-container"));
      }
    },
    handlePaginationText() {
      this.paginationOptions.textOverrides = this.locale === "fi"
        ? this.paginationTextOverrides
        : {};
    },
    getEmptyText() {
      if (this.$route.name == "SharedFrom") {
        return this.$t("message.emptyProject.sharedFrom");
      }

      if (this.$route.name == "SharedTo") {
        return this.$t("message.emptyProject.sharedTo");
      }

      return this.$t("message.emptyProject.all");
    },
  },
};
</script>
