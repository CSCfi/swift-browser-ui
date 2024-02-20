<template>
  <div class="object-table-wrapper">
    <!-- Footer options needs to be in CamelCase,
    because csc-ui wont recognise it otherwise. -->
    <c-data-table
      id="obj-table"
      :data.prop="objects"
      :headers.prop="hideTags ?
        headers.filter(header => header.key !== 'tags'): headers"
      :pagination.prop="disablePagination ? null : paginationOptions"
      :hide-footer="disablePagination"
      :footerOptions.prop="footerOptions"
      :no-data-text="noDataText"
      :sort-by="sortBy"
      :sort-direction="sortDirection"
      selection-property="name"
      external-data
      :selectable="selectable"
      @selection="handleSelection"
      @paginate="getPage"
      @sort="onSort"
    />
    <c-loader v-show="isLoaderVisible">
      {{ $t('message.upload.uploadedItems') }}
    </c-loader>
  </div>
</template>

<script>
import {
  sortItems,
  parseDateTime,
  parseDateFromNow,
  getHumanReadableSize,
  DEV,
} from "@/common/conv";

import {
  toggleEditTagsModal,
  isFile,
  getFolderName,
  getPrefix,
  getPaginationOptions,
  checkIfItemIsLastOnPage,
  checkIfCanDownloadTar,
  addErrorToastOnMain,
} from "@/common/globalFunctions";
import {
  setPrevActiveElement,
  disableFocusOutsideModal,
} from "@/common/keyboardNavigation";
import {
  mdiTrayArrowDown,
  mdiPencilOutline,
  mdiDeleteOutline,
  mdiFolder ,
} from "@mdi/js";

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
    breadcrumbClickedProp: {
      type: Boolean,
      default: false,
    },
    noDataText: {
      type: String,
      default: "",
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
    owner() {
      return this.$route.params.owner;
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
    if(this.breadcrumbClickedProp) this.paginationOptions.currentPage = 1;
  },
  mounted() {
    window.addEventListener("popstate", this.handlePopState);
  },
  beforeUnmount() {
    window.removeEventListener("popstate", this.handlePopState);
  },
  updated(){
    this.paginationOptions.currentPage =
      checkIfItemIsLastOnPage(this.paginationOptions);
  },
  methods: {
    handlePopState(event) {
      // reset page to 1 after reversing a page
      if (event.type === "popstate") {
        this.paginationOptions.currentPage = 1;
      }
    },
    changeFolder: function (folder) {
      this.paginationOptions.currentPage = 1;
      this.$router.push(
        `${window.location.pathname}?prefix=${getPrefix(this.$route)}${folder}`,
      );
    },
    formatItem: function (item) {
      const name = this.renderFolders ?
        getFolderName(item.name, this.$route)
        : item.name;

      return {
        name: {
          value: name,
          ...(item?.subfolder ? {
            component: {
              tag: "c-link",
              params: {
                href: "javascript:void(0)",
                color: "dark-grey",
                path: mdiFolder,
                iconFill: "primary",
                iconStyle: {
                  marginRight: "1rem",
                  flexShrink: "0",
                },
                onClick: () => this.changeFolder(name),
              },
            },
          } : {}),
        },
        size: {
          value: getHumanReadableSize(item.bytes, this.locale),
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
              ...(item.tags?.length ?
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
              value: this.$t("message.download.download"),
              component: {
                tag: "c-button",
                params: {
                  text: true,
                  size: "small",
                  title: "Download",
                  path: mdiTrayArrowDown,
                  onClick: () => {
                    item.name.match(".c4gh") || item?.subfolder
                      ? this.beginDownload(item)
                      : this.navDownload(item.url);
                  },
                  disabled: this.owner != undefined &&
                    this.accessRights.length === 0,
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
                    this.onOpenEditTagsModal(item.name),
                  onKeyUp: (event) => {
                    if(event.keyCode === 13) {
                      this.onOpenEditTagsModal(item.name, true);
                    }
                  },
                  disabled: item?.subfolder ||
                    (this.owner != undefined && this.accessRights.length <= 1),
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
                      this.$emit("delete-object", item, true);
                    }
                  },
                  disabled:
                    this.owner != undefined && this.accessRights.length <= 1,
                },
              },
            },
          ],
        },
      };
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

      if (this.objs.length > 0 && filteredObjs.length == 0) {
        window.location.pathname = "/notfound";
      }

      let pagedLength = 0;

      this.objects = filteredObjs.reduce((items, item) => {
        if (isFile(item.name, this.$route) || !this.renderFolders) {
          items.push(item);
        } else {
          let subName = getFolderName(item.name, this.$route);
          //check if subfolder already added
          if (items.find(el => getFolderName(el.name, this.$route)
            === subName)) {
            return items;
          } else {
            //filter objs that would belong to subfolder
            let subfolderObjs = filteredObjs.filter(obj => {
              if (getFolderName(obj.name, this.$route) ===
                subName) {
                return obj;
              }
            });
            //sort by latest last_modified
            subfolderObjs.sort((a, b) => sortItems(
              a, b, "last_modified", "desc"));
            const subSize = subfolderObjs.reduce((sum, obj) => {
              return sum += obj.bytes;
            }, 0);
            const fullSubName = getPrefix(this.$route) + subName + "/";
            //add new subfolder
            const subfolder = {
              container: item.container,
              name: fullSubName,
              bytes: subSize,
              last_modified: subfolderObjs[0].last_modified,
              tags: [],
              subfolder: true,
            };
            items.push(subfolder);
          }
        }
        pagedLength = items.length;
        return items;
      }, [])
        .sort((a, b) => sortItems(a, b, this.sortBy, this.sortDirection))
        .slice(offset, offset + limit)
        .map(item => this.formatItem(item));

      this.paginationOptions = {
        ...this.paginationOptions,
        itemCount: pagedLength,
      };
      if (this.objs.length > 0) this.setPageByFileName(this.$route.query.file);
    },
    setPageByFileName: function(file){
      if(file != undefined){
        let objectList = this.objs;
        // check if file is in subfolder
        if(file.includes("/")){
          let subfolderItems = [];
          objectList.forEach(element => {
            if(element.name.substr(0, element.name.lastIndexOf("/") + 1)
              === file.substr(0, file.lastIndexOf("/") + 1)){
              subfolderItems.push(element);
            }
          });
          objectList = subfolderItems;
        }
        let index = objectList.findIndex(item => item.name == file);
        if(index <= 0){
          index = 1;
        }
        this.paginationOptions.currentPage =
          Math.floor(index  / this.paginationOptions.itemsPerPage) + 1;
        let queryWithOutFile = {
          ...this.$route.query,
          file: null,
        };
        this.$router.replace({"query": queryWithOutFile});
      }
    },
    setPagination: function () {
      const paginationOptions = getPaginationOptions(this.$t);
      this.paginationOptions = paginationOptions;
    },
    onSort(event) {
      this.sortBy = event.detail.sortBy;
      this.sortDirection = event.detail.direction;
      //sorted in getPage()
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
      if (object?.subfolder) {
        const subfolderFiles = this
          .objs
          .filter((obj) => {
            return obj.name.startsWith(object.name);
          })
          .map(item => item.name);
        const canDownload = checkIfCanDownloadTar(subfolderFiles, true);
        if (canDownload) {
          this.$store.state.socket.addDownload(
            this.$route.params.container,
            subfolderFiles,
            this.$route.params.owner ? this.$route.params.owner : "",
          ).then(() => {
            if (DEV) console.log(`Started downloading subfolder ${object.name}`);
          }).catch(() => {
            addErrorToastOnMain(this.$t("message.download.error"));
          });
        } else {
          addErrorToastOnMain(this.$t("message.download.files"));
        }
      } else {
        this.$store.state.socket.addDownload(
          this.$route.params.container,
          [object.name],
          this.$route.params.owner ? this.$route.params.owner : "",
        ).then(() => {
          if (DEV) console.log(`Started downloading object ${object.name}`);
        }).catch(() => {
          addErrorToastOnMain(this.$t("message.download.error"));
        });
      }
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
    onOpenEditTagsModal(itemName, keypress) {
      toggleEditTagsModal(itemName, null);
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
  },
};
</script>

<style lang="scss" scoped>

 .object-table-wrapper{
    position: relative;
  }

</style>
