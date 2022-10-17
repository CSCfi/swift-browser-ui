<template>
  <c-data-table
    id="contable-tags"
    :data.prop="containers"
    :headers.prop="hideTags ?
      headers.filter(header => header.key !== 'tags'): headers"
    :pagination.prop="disablePagination ? null : paginationOptions"
    :footer-options.prop="footerOptions"
    :no-data-text="$t('message.emptyProject')"
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
  toggleCreateFolderModal,
  getSharingContainers,
  getSharedContainers,
} from "@/common/globalFunctions";
import {swiftDeleteContainer} from "@/common/api";

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

      this.containers = this.conts.slice(offset, offset + limit).reduce((
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
                      this.$store.commit("setFolderName", item.data.name.value);
                    },
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
                        action: (() => {
                          this.$router.push({
                            name: "ReplicateContainer",
                            params: {
                              container: item.name,
                              project: item.projectID,
                              from: item.from ? item.from : item.projectID,
                            },
                          });
                        }),
                        disabled: !item.bytes ? true : false,
                      },
                      {
                        name: this.$t("message.editTags"),
                        action: () => toggleCreateFolderModal(item.name),
                      },
                      {
                        name: this.$t("message.delete"),
                        action: () => this.confirmDelete(
                          item.name, item.count,
                        ),
                      },
                    ],
                    customTrigger: {
                      value: this.$t("message.options"),
                      component: {
                        tag: "c-button",
                        params: {
                          text: true,
                          path: mdiDotsHorizontal,
                          title: "Menu with custom trigger",
                          size: "small",
                        },
                      },
                    },
                    path: mdiDotsHorizontal,

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
    onSort(event) {
      this.sortBy = event.detail.sortBy;
      this.sortDirection = event.detail.direction;
      sortObjects(this.conts, this.sortBy, this.sortDirection);
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
        },
      ];
    },
    confirmDelete: function (container, objects) {
      if (objects > 0) {
        this.$buefy.notification.open({
          message: "Deleting a container requires deleting all objects first.",
          type: "is-danger",
          position: "is-top-right",
          duration: 30000,
          hasIcon: true,
        });
        this.$router.push(
          this.$route.params.project
            + "/"
            + container,
        );
      } else {
        this.$buefy.dialog.confirm({
          title: this.$t("message.container_ops.deleteConfirm"),
          message: this.$t("message.container_ops.deleteConfirmMessage"),
          confirmText: this.$t("message.container_ops.deleteConfirm"),
          type: "is-danger",
          hasIcon: true,
          onConfirm: () => {this.deleteContainer(container);},
        });
      }
    },
    deleteContainer: function(container) {
      this.$buefy.toast.open({
        message: this.$t("message.container_ops.deleteSuccess"),
        type: "is-success",
      });
      const projectID = this.$store.state.active.id;
      swiftDeleteContainer(
        projectID,
        container,
      ).then(async () => {
        await this.$store.state.db.containers
          .where({
            projectID,
            name: container,
          })
          .delete();
      });
    },
    handlePaginationText() {
      this.paginationOptions.textOverrides = this.locale === "fi"
        ? this.paginationTextOverrides
        : {};
    },
  },
};
</script>
