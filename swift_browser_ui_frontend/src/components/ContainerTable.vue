<template>
  <div id="c-containers">
    <c-data-table
      v-if="hideTags"
      id="contable"
      :data.prop="containers"
      :headers.prop="noTagHeaders"
      :pagination.prop="disablePagination ? null : paginationOptions"
      :footer-options.prop="footerOptions"
      :sort-by.prop="sortBy"
      :sort-direction.prop="direction"
      :no-data-text="$t('message.emptyProject')"
      external-data
      @paginate="getPage"
      @sort="console.log('Sort called.')"
    />
    <c-data-table
      v-else
      id="contable"
      :data.prop="containers"
      :headers.prop="extHeaders"
      :pagination.prop="disablePagination ? null : paginationOptions"
      :footer-options.prop="footerOptions"
      :sort-by.prop="sortBy"
      :sort-direction.prop="direction"
      :no-data-text="$t('message.emptyProject')"
      external-data
      @paginate="getPage"
      @sort="console.log('Sort called.')"
    />
  </div>
</template>

<script>
import { getHumanReadableSize, truncate } from "@/common/conv";

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
      extHeaders: [
        {
          key: "name",
          value: "Name",
        },
        {
          key: "size",
          value: "Size",
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
        },
        {
          key: "size",
          value: "Size",
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
    conts() {
      this.getPage();
    },
  },
  methods: {
    getPage: function () {
      let offset = 0;
      let limit = this.conts.length;
      if (!this.disablePagination || this.conts.length > 500) {
        offset =
          this.paginationOptions.currentPage
          * this.paginationOptions.itemsPerPage
          - this.paginationOptions.itemsPerPage;
        
        limit = this.paginationOptions.itemsPerPage;
      }
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
                onClick: () => {
                  this.$router.push({
                    name: "ObjectsView",
                    params: {
                      container: item.name,
                    },
                  });
                },
              },
            },
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
                    href: "/download/".concat(
                      this.$route.params.project,
                      "/",
                      item.name,
                    ),
                    target: "_blank",
                  },
                },
              },
              {
                value: "Share",
                component: {
                  tag: "c-button",
                  params: {
                    text: true,
                    size: "small",
                    title: "Share",
                    onClick: (item) => {
                      this.$router.push({
                        name: "SharingView",
                        query: { container: item.name },
                      });
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
  },
};
</script>
