<template>
  <c-data-table
    id="objtable"
    :key="componentKey"
    :data.prop="objects"
    :headers.prop="hideTags ?
      headers.filter(header => header.key !== 'tags'): headers"
    :pagination.prop="disablePagination ? null : paginationOptions"
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
    locale () {
      return this.$i18n.locale;
    },
  },
  watch: {
    disablePagination() {
      this.getPage();
    },
    hideTags() {
      this.componentKey += 1;
      this.getPage();
    },
    renderFolders() {
      this.getPage();
    },
    objs() {
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

      this.objects = this.objs.slice(offset, offset + limit).reduce((
        items,
        item,
      ) => {
        items.push({
          name: {
            value: truncate(item.name),
            ...(this.renderFolders ? {
              component: {
                tag: "c-link",
                params: {
                  href: "javascript:void(0)",
                  color: "dark-grey",
                  onClick: () => this.$emit("changeFolder", item.name),
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
                    href: item.url,
                    target: "_blank",
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
        itemCount: this.objs.length,
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
