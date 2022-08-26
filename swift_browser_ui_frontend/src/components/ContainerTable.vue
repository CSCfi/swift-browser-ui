<template>
  <c-data-table
    id="contable-tags"
    :key="componentKey"
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
import { mdiTrayArrowDown, mdiShareVariantOutline } from "@mdi/js";

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
      componentKey: 0,
    };
  },
  computed: {
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
    conts() {
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
