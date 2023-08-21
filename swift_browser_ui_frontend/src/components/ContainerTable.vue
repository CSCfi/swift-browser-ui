<template>
  <!-- Footer options needs to be in CamelCase,
  because csc-ui wont recognise it otherwise. -->
  <!-- eslint-disable-->
  <c-data-table
    id="container-table"
    :data.prop="containers"
    :headers.prop="hideTags ?
      headers.filter(header => header.key !== 'tags'): headers"
    :pagination.prop="disablePagination ? null : paginationOptions"
    :hide-footer="disablePagination"
    :footerOptions.prop="footerOptions"
    :no-data-text="getEmptyText()"
    :sort-by="sortBy"
    :sort-direction="sortDirection"
    external-data
    @paginate="getPage"
    @sort="onSort"
  />
  <!-- eslint-enable-->
</template>

<script>
import {
  getHumanReadableSize,
  truncate,
  sortObjects,
  parseDateTime,
  parseDateFromNow,
} from "@/common/conv";
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
  getPaginationOptions,
  toggleCopyFolderModal,
  checkIfItemIsLastOnPage,
} from "@/common/globalFunctions";
import {
  setPrevActiveElement,
  disableFocusOutsideModal,
} from "@/common/keyboardNavigation";
import { toRaw } from "vue";
import { swiftDeleteContainer } from "@/common/api";

export default {
  name: "ContainerTable",
  props: {
    conts: {
      type: Array,
      default: () => {return [];},
    },
    showTimestamp: {
      type: Boolean,
      default: false,
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
        itemsPerPageOptions: [5, 10, 25, 50, 100],
      },
      paginationOptions: {},
      sortBy: "name",
      sortDirection: "asc",
      abortController: null,
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
    showTimestamp() {
      this.getPage();
    },
    locale() {
      this.setHeaders();
      this.getPage();
      this.setPagination();
    },
  },
  created() {
    this.setHeaders();
    this.setPagination();
  },
  beforeMount () {
    this.abortController = new AbortController();
  },
  beforeUnmount () {
    this.abortController.abort();
  },
  methods: {
    async getSharingContainers() {
      return this.sharingClient
        ? this.sharingClient.getShare(
          this.active.id,
          this.abortController.signal)
        : [];
    },
    getSharedContainers () {
      return this.sharingClient
        ? this.sharingClient.getAccess(
          this.$route.params.project,
          this.abortController.signal)
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

      const sharingContainers =
        await getSharingContainers(this.active.id, this.abortController.signal);
      const sharedContainers =
        await getSharedContainers(this.active.id, this.abortController.signal);

      const getSharedStatus = (folderName) => {
        if (sharingContainers.indexOf(folderName) > -1) {
          return this.$t("message.table.sharing");
        } else if (sharedContainers.findIndex(
          cont => cont.container === folderName) > -1) {
          return this.$t("message.table.shared");
        }
        return "";
      };

      // Filter out segment folders for rendering
      // Map the 'accessRights' to the container if it's a shared container
      const mappedContainers = await Promise.all(
        this.conts.filter(cont => !cont.name.endsWith("_segments"))
          .map(async(cont) => {
            const sharedDetails = cont.owner ? await getAccessDetails(
              this.$route.params.project,
              cont.container,
              cont.owner,
              this.abortController.signal) : null;
            const accessRights = sharedDetails ? sharedDetails.access : null;
            return sharedDetails && accessRights
              ? {...cont, accessRights} : {...cont};
          }));

      this.containers = mappedContainers
        .slice(offset, offset + limit).reduce((
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
            last_activity: {
              value: this.showTimestamp? parseDateTime(
                this.locale, item.last_modified, this.$t, false) :
                parseDateFromNow(this.locale, item.last_modified, this.$t),
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
                      disabled: item.owner && item.accessRights.length === 0
                        || item.bytes === 0,
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
                      onClick: () =>
                        this.onOpenShareModal(item.name),
                      onKeyUp: (event) => {
                        if(event.keyCode === 13)
                          this.onOpenShareModal(item.name, true);
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
                          action: () => {
                            this.openCopyFolderModal(item.name, item.owner);
                            const menuItems = document
                              .querySelector("c-menu-items");
                            menuItems.addEventListener("keydown", (e) =>{
                              if (e.keyCode === 13) {
                                this.openCopyFolderModal(
                                  item.name, item.owner, true,
                                );
                              }
                            });
                          },
                          disabled: !item.bytes ? true : false,
                        },
                        {
                          name: this.$t("message.editTags"),
                          action: () => {
                            this.openEditTagsModal(item.name);
                            const menuItems = document
                              .querySelector("c-menu-items");
                            menuItems.addEventListener("keydown", (e) =>{
                              if (e.keyCode === 13) {
                                this.openEditTagsModal(item.name, true);
                              }
                            });
                          },
                          disabled: item.owner,
                        },
                        {
                          name: this.$t("message.delete"),
                          action: () => this.delete(
                            item.name, item.count,
                          ),
                          disabled: item.owner,
                        },
                      ],
                      customTrigger: {
                        value: this.$t("message.options"),
                        component: {
                          tag: "c-button",
                          params: {
                            text: true,
                            path: mdiDotsHorizontal,
                            title: this.$t("message.options"),
                            size: "small",
                            disabled: item.owner &&
                              item.accessRights.length === 0,
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
        itemCount: mappedContainers.length,
      };
    },
    async onSort(event) {
      this.sortBy = event.detail.sortBy;
      this.sortDirection = event.detail.direction;

      if (this.sortBy === "sharing") {
        const sharingContainers =
          await getSharingContainers(
            this.active.id,
            this.abortController.signal,
          );
        const sharedContainers =
          await getSharedContainers(
            this.active.id,
            this.abortController.signal,
          );

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
          key: "last_activity",
          value: this.$t("message.table.activity"),
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
    setPagination: function () {
      const paginationOptions = getPaginationOptions(this.$t);
      this.paginationOptions = paginationOptions;
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
        const projectID = this.$route.params.project;
        swiftDeleteContainer(
          projectID,
          container,
        ).then(async() => {
          await swiftDeleteContainer(projectID, `${container}_segments`);
          document.querySelector("#container-toasts").addToast(
            { progress: false,
              type: "success",
              message: this.$t("message.container_ops.deleteSuccess")},
          );
          this.$emit("delete-container", container);
        });
      }
      this.paginationOptions.currentPage =
        checkIfItemIsLastOnPage({
          currentPage:
            this.paginationOptions.currentPage,
          itemsPerPage:
            this.paginationOptions.itemsPerPage,
          itemCount:
            this.paginationOptions.itemCount - 1,
        });
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
    onOpenShareModal(itemName, keypress) {
      this.$store.commit("toggleShareModal", true);
      this.$store.commit(
        "setFolderName", itemName);

      if (keypress) {
        setPrevActiveElement();
        const shareModal = document.getElementById("share-modal");
        disableFocusOutsideModal(shareModal);
      }
      setTimeout(() => {
        const shareIDsInput = document.getElementById("share-ids")?.children[0];
        shareIDsInput.focus();
      }, 300);
    },
    openEditTagsModal(itemName, keypress) {
      toggleEditTagsModal(null, itemName);
      if (keypress) {
        setPrevActiveElement();
        const editTagsModal = document.getElementById("edit-tags-modal");
        disableFocusOutsideModal(editTagsModal);
      }
      setTimeout(() => {
        const editTagsInput = document.getElementById("edit-tags-input")
          ?.children[0];
        editTagsInput.focus();
      }, 300);
    },
    openCopyFolderModal(itemName, itemOwner, keypress) {
      itemOwner
        ? toggleCopyFolderModal(itemName, itemOwner)
        : toggleCopyFolderModal(itemName);
      if (keypress) {
        setPrevActiveElement();
        const copyFolderModal = document.getElementById("copy-folder-modal");
        disableFocusOutsideModal(copyFolderModal);
      }
      setTimeout(() => {
        const copyFolderInput = document
          .querySelector("#new-copy-folderName input");
        copyFolderInput.focus();
      }, 300);
    },
  },
};
</script>
