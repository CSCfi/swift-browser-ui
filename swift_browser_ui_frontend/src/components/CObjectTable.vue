<template>
  <div id="c-objects">
    Checked rows: {{ checkedRows.length }}
    <c-data-table
      v-if="hideTags"
      id="objtable-no-tags"
      :data.prop="objects"
      :headers.prop="noTagHeaders"
      :pagination.prop="disablePagination ? null : paginationOptions"
      :footer-options.prop="footerOptions"
      :no-data-text="$t('message.emptyProject')"
      external-data
      selectable
      @selection="handleSelection" 
      @paginate="getPage"
    />
    <c-data-table
      v-else
      id="objtable-tags"
      :data.prop="objects"
      :headers.prop="extHeaders"
      :pagination.prop="disablePagination ? null : paginationOptions"
      :footer-options.prop="footerOptions"
      :no-data-text="$t('message.emptyProject')"
      external-data
      selectable
      :selection="checkedRows"
      @selection="handleSelection" 
      @paginate="getPage"
    />
  </div>
</template>

<script>
import { getHumanReadableSize, truncate } from "@/common/conv";

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
    checkedRows: {default: []},
  },
  data() {
    return {
      objects: [],
      extHeaders: [
        {
          key: "name",
          value: "Name",
          sortable: false,
        },
        {
          key: "last_modified",
          value: "Last Modified",
          sortable: false,
        },
        {
          key: "size",
          value: "Size",
          sortable: false,
        },
        {
          key: "tags",
          value: "Tags",
          sortable: false,
        },
        {
          key: "actions",
          align: "end",
          value: null,
          sortable: false,
        },
      ],
      noTagHeaders: [
        {
          key: "name",
          value: "Name",
          sortable: false,
        },
        {
          key: "last_modified",
          value: "Last Modified",
          sortable: false,
        },
        {
          key: "size",
          value: "Size",
          sortable: false,
        },
        {
          key: "actions",
          align: "end",
          value: null,
          sortable: false,
        },
      ],
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
      sortBy: null,
    };
  },
  watch: {
    disablePagination() {
      this.getPage();
    },
    hideTags() {
      this.getPage();
    },
    renderFolders() {
      this.getPage();
    },
    objs() {
      this.getPage();
    },
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
                  onClick: () => {
                    let e = new Event("changeFolder", {name: item.name});
                    this.$emit(e);
                  },
                },
              },
            } : {}),
          },
          size: {
            value: getHumanReadableSize(item.bytes),
          },
          last_modified: {
            value: item.last_modified,
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
                ...(!item.tags.length ? [{ key: "no_tags", value: "-" }] : []),
              ],
            },
          }),
          actions: {
            value: null,
            sortable: null,
            align: "end",
            children: [
              {
                value: "Download",
                component: {
                  tag: "c-button",
                  params: {
                    text: true,
                    size: "small",
                    title: "Download",
                    href: item.url,
                    target: "_blank",
                  },
                },
              },
              {
                value: "Edit tags",
                component: {
                  tag: "c-button",
                  params: {
                    text: true,
                    size: "small",
                    title: "Edit tags",
                    onClick: () => {
                      console.log("Edit not yet implemented.");
                    },
                  },
                },
              },
              {
                value: "Delete",
                component: {
                  tag: "c-button",
                  params: {
                    text: true,
                    size: "small",
                    title: "Share",
                    onClick: () => {
                      console.log("Delete not yet implemented.");
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
    handleSelection(event) {
      this.$emit("selected-rows", event.detail);
    },
  },
};
</script>
