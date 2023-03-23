<template>
  <c-data-table
    id="objtable"
    :key="componentKey"
    :data.prop="objects"
    :headers.prop="hideTags ?
      headers.filter(header => header.key !== 'tags'): headers"
    :pagination.prop="disablePagination ? null : paginationOptions"
    :hide-footer="disablePagination"
    :footer-options.prop="footerOptions"
    :no-data-text="$t('message.emptyContainer')"
    :sort-by="sortBy"
    :sort-direction="sortDirection"
    selection-property="name"
    external-data
    selectable
    @selection="handleSelection"
    @paginate="getPage"
    @sort="onSort"
  />
</template>

<script>
import {
  getHumanReadableSize,
  truncate,
  sortObjects,
  parseDateTime,
} from "@/common/conv";
import {
  DecryptedDownloadSession,
  beginDownload,
} from "@/common/download";

import {
  toggleEditTagsModal,
} from "@/common/globalFunctions";

import { mdiTrayArrowDown, mdiPencilOutline, mdiDeleteOutline } from "@mdi/js";

export default {
  name: "CObjectTable",
  props: {
    objs: {
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
    renderFolders: {
      type: Boolean,
      default: true,
    },
    checkedRows: {
      default: [],
    },
  },
  data() {
    return {
      currentDownload: undefined,
      objects: [],
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
      componentKey: 0,
    };
  },
  computed: {
    container () {
      return this.$route.params.container;
    },
    prefix () {
      return this.$route.query.prefix;
    },
    locale () {
      return this.$i18n.locale;
    },
    active () {
      return this.$store.state.active;
    },
  },
  watch: {
    disablePagination() {
      this.componentKey += 1;
      this.getPage();
    },
    hideTags() {
      this.componentKey += 1;
      this.getPage();
    },
    renderFolders() {
      this.componentKey += 1;
      this.getPage();
    },
    prefix() {
      this.componentKey += 1;
      this.getPage();
    },
    objs() {
      this.componentKey += 1;
      this.getPage();
    },
    locale() {
      this.componentKey += 1;
      this.setHeaders();
      this.getPage();
    },
  },
  created() {
    this.setHeaders();
  },
  methods: {
    isFile: function (path) {
      // Return true if path represents a file in the active prefix context
      return path.replace(this.getPrefix(), "").match("/") ? false : true;
    },
    changeFolder: function (folder) {
      this.$router.push(
        `${window.location.pathname}?prefix=${this.getPrefix()}${folder}`,
      );
      this.componentKey += 1;
      this.getPage();
    },
    getFolderName: function (path) {
      // Get the name of the currently displayed pseudofolder
      let endregex = new RegExp("/.*$");
      return path.replace(this.getPrefix(), "").replace(endregex, "");
    },
    getPage: function () {
      let offset = 0;
      let limit = this.objs.length;
      if (!this.disablePagination || this.objs.length > 500) {
        offset =
          this.paginationOptions.currentPage
          * this.paginationOptions.itemsPerPage
          - this.paginationOptions.itemsPerPage;

        limit = this.paginationOptions.itemsPerPage;
      }

      let pagedLength = 0;

      this.objects = this
        .objs
        .filter((obj) => {
          return obj.name.startsWith(this.getPrefix());
        })
        .reduce((items, item) => {
          if (this.isFile(item.name) || !this.renderFolders) {
            items.push(item);
          } else {
            if (items.find(el => {
              return this.getFolderName(
                el.name,
              ).match(this.getFolderName(item.name)) ? true : false;
            })) {
              return items;
            } else {
              items.push(item);
            }
          }
          pagedLength = items.length;
          return items;
        }, [])
        .slice(offset, offset + limit)
        .reduce((
          items,
          item,
        ) => {
          let value = truncate(
            this.renderFolders ? this.getFolderName(item.name) : item.name,
          );
          items.push({
            name: {
              value: value,
              ...(this.renderFolders && !this.isFile(item.name) ? {
                component: {
                  tag: "c-link",
                  params: {
                    href: "javascript:void(0)",
                    color: "dark-grey",
                    onClick: () => this.changeFolder(value),
                  },
                },
              } : {}),
            },
            size: {
              value: getHumanReadableSize(item.bytes),
            },
            last_modified: {
              value: parseDateTime(this.locale, item.last_modified),
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
                  ...(item.tags && !item.tags.length ?
                    [{ key: "no_tags", value: "-" }] : []),
                ],
              },
            }),
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
                      title: "Download",
                      onClick: () => {
                        item.name.match(".c4gh")
                          ? this.beginDownload(item)
                          : this.navDownload(item.url);
                      },
                      path: mdiTrayArrowDown,
                    },
                  },
                },
                {
                  value: this.$t("message.table.editTags"),
                  component: {
                    tag: "c-button",
                    params: {
                      text: true,
                      size: "small",
                      title: "Edit tags",
                      path: mdiPencilOutline,
                      onClick: ({ data }) =>
                        toggleEditTagsModal(data.name.value, null),
                      onKeyUp: (event) => {
                        if(event.keyCode === 13) {
                          toggleEditTagsModal(item.data.name.value, null);
                        }
                      },
                    },
                  },
                },
                {
                  value: this.$t("message.delete"),
                  component: {
                    tag: "c-button",
                    params: {
                      text: true,
                      size: "small",
                      title: "Delete object",
                      path: mdiDeleteOutline,
                      onClick: () => {
                        this.$emit("delete-object", item);
                      },
                      onKeyUp: (event) => {
                        if(event.keyCode === 13) {
                          this.$emit("delete-object", item);
                        }
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
        itemCount: pagedLength,
      };
    },
    onSort(event) {
      this.sortBy = event.detail.sortBy;
      this.sortDirection = event.detail.direction;
      sortObjects(this.objs, this.sortBy, this.sortDirection);
    },
    getEditRoute: function(containerName, objectName) {
      if (this.$route.name == "SharedObjects") {
        return {
          name: "EditSharedObjectView",
          params: {
            container: containerName,
            object: objectName,
            owner: this.$route.params.owner,
          },
        };
      }
      return {
        name: "EditObjectView",
        params: {
          container: containerName,
          object: objectName,
        },
      };
    },
    handleSelection(event) {
      this.$emit("selected-rows", event.detail);
    },
    beginDownload(object) {
      this.currentDownload = new DecryptedDownloadSession(
        this.active,
        this.active.id,
        [object.name],
        this.$route.params.container,
        this.$store,
      );
      this.currentDownload.initServiceWorker();
      beginDownload();
    },
    navDownload(url) {
      window.open(url, "_blank");
    },
    getPrefix() {
      // Get current pseudofolder prefix
      if (this.$route.query.prefix == undefined) {
        return "";
      }
      return `${this.$route.query.prefix}/`;
    },
    setHeaders() {
      this.headers = [
        {
          key: "name",
          value: this.$t("message.table.name"),
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
          key: "last_modified",
          value: this.$t("message.table.modified"),
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
  },
};
</script>
