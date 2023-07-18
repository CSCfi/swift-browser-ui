<template>
  <div class="object-table-wrapper">
    <!-- Footer options needs to be in CamelCase,
    because csc-ui wont recognise it otherwise. -->
    <!-- eslint-disable-->
    <c-data-table
      id="objtable"
      :data.prop="objects"
      :headers.prop="hideTags ?
        headers.filter(header => header.key !== 'tags'): headers"
      :pagination.prop="disablePagination ? null : paginationOptions"
      :hide-footer="disablePagination"
      :footerOptions.prop="footerOptions"
      :no-data-text="$t('message.emptyContainer')"
      :sort-by="sortBy"
      :sort-direction="sortDirection"
      selection-property="name"
      external-data
      :selectable="selectable"
      @selection="handleSelection"
      @paginate="getPage"
      @sort="onSort"
    />
    <!-- eslint-enable-->
    <c-loader v-show="isLoaderVisible">
      {{ $t('message.upload.uploadedItems') }}
    </c-loader>
  </div>
</template>

<script>
import {
  truncate,
  sortObjects,
  parseDateTime,
  parseDateFromNow,
  getItemSize,
} from "@/common/conv";
import {
  DecryptedDownloadSession,
  beginDownload,
} from "@/common/download";

import {
  toggleEditTagsModal,
  isFile,
  getFolderName,
  getPrefix,
  getPaginationOptions,
  checkIfItemIsLastOnPage,
} from "@/common/globalFunctions";

import {
  mdiTrayArrowDown,
  mdiPencilOutline,
  mdiDeleteOutline,
  mdiFolder ,
} from "@mdi/js";
import { toRaw } from "vue";

export default {
  name: "CObjectTable",
  props: {
    objs: {
      type: Array,
      default: () => [],
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
    showTimestamp: {
      type: Boolean,
      default: false,
    },
    accessRights: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      currentDownload: undefined,
      objects: [],
      footerOptions: {
        itemsPerPageOptions: [5, 10, 25, 50, 100],
      },
      paginationOptions: {},
      sortBy: "name",
      sortDirection: "asc",
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
    selectable () {
      return this.$route.name !== "SharedObjects"
        || this.accessRights.length === 2;
    },
    isLoaderVisible() {
      return this.$store.state.isLoaderVisible;
    },
  },
  watch: {
    prefix() {
      this.getPage();
    },
    locale() {
      this.setHeaders();
      this.setPagination();
    },
  },
  created() {
    this.setHeaders();
    this.setPagination();
  },
  beforeUpdate() {
    this.getPage();
  },
  updated(){
    this.paginationOptions.currentPage =
      checkIfItemIsLastOnPage(this.paginationOptions);
  },
  methods: {
    changeFolder: function (folder) {
      this.$router.push(
        `${window.location.pathname}?prefix=${getPrefix(this.$route)}${folder}`,
      );
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

      // Filtered objects based on prefix
      const filteredObjs = this
        .objs
        .filter((obj) => {
          return obj.name.startsWith(getPrefix(this.$route));
        });

      let pagedLength = 0;

      this.objects = filteredObjs
        .reduce((items, item) => {
          if (isFile(item.name, this.$route) || !this.renderFolders) {
            items.push(item);
          } else {
            if (items.find(el => {
              return getFolderName(
                el.name, this.$route,
              ) === getFolderName(item.name, this.$route) ? true : false;
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
          const value = truncate(
            this.renderFolders ?
              getFolderName(item.name, this.$route)
              : item.name,
          );

          const isSubfolder = this.renderFolders &&
            !isFile(item.name, this.$route);

          items.push({
            name: {
              value: value,
              ...(isSubfolder ? {
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
                    onClick: () => this.changeFolder(value),
                  },
                },
              } : {}),
            },
            size: {
              value: getItemSize(item, filteredObjs, this.$route),
            },
            last_modified: {
              value: this.showTimestamp? parseDateTime(
                this.locale, item.last_modified, this.$t, false) :
                parseDateFromNow(this.locale, item.last_modified, this.$t),
            },
            ...(this.hideTags ? {} : {
              tags: {
                value: null,
                children: [
                  ...(item.tags?.length && !isSubfolder ?
                    item.tags.map((tag, index) => ({
                      key: "tag_" + index + "",
                      value: tag,
                      component: {
                        tag: "c-tag",
                        params: {
                          flat: true,
                        },
                      },
                    })) : [{ key: "no_tags", value: "-" }]),
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
                      onClick: () =>
                        toggleEditTagsModal(item.name, null),
                      onKeyUp: (event) => {
                        if(event.keyCode === 13) {
                          toggleEditTagsModal(item.name, null);
                        }
                      },
                      disabled: isSubfolder || this.accessRights.length <= 1,
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
                      disabled: this.accessRights.length <= 1,
                    },
                  },
                },
              ],
            },
          });
          let queryWithOutFile = {
            ...this.$route.query,
            file: null,
          };
          this.$router.replace({"query": queryWithOutFile});
          return items;
        }, []);

      this.paginationOptions = {
        ...this.paginationOptions,
        itemCount: pagedLength,
      };
      this.setPageByFileName(this.$route.query.file);
    },
    setPageByFileName: function(file){
      if(file != undefined){
        var index = this.objs.findIndex(item => item.name == file);
        if(index <= 0){
          index = 1;
        }
        this.paginationOptions.currentPage =
          Math.floor(index  / this.paginationOptions.itemsPerPage) + 1;
      }
    },
    setPagination: function () {
      const paginationOptions = getPaginationOptions(this.$t);
      this.paginationOptions = paginationOptions;
    },
    onSort(event) {
      this.sortBy = event.detail.sortBy;
      this.sortDirection = event.detail.direction;

      // Use toRaw to mutate the original array, not the proxy
      sortObjects(toRaw(this.objs), this.sortBy, this.sortDirection);
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
      if (event.detail.length > 0 && this.renderFolders) {
        const prefix = getPrefix(this.$route);
        const selectedRows = event.detail.map(item => prefix.concat(item));
        this.$emit("selected-rows", selectedRows);
      } else {
        this.$emit("selected-rows", event.detail);
      }
    },
    beginDownload(object) {
      console.log(object);
      this.currentDownload = new DecryptedDownloadSession(
        this.active,
        this.active.id,
        [object.name],
        this.$route.params.container,
        (this.$route.params.owner != undefined) ? this.$route.params.owner : "",
        this.$store,
      );
      this.currentDownload.initServiceWorker();
      beginDownload();
    },
    navDownload(url) {
      window.open(url, "_blank");
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

<style lang="scss" scoped>
 .object-table-wrapper{
    position: relative;
  }
</style>
