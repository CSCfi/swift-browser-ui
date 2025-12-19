<template>
  <!-- Footer options needs to be in CamelCase,
  because csc-ui wont recognise it otherwise. -->
  <c-data-table
    id="container-table"
    data-testid="container-table"
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
</template>

<script>
import {
  getHumanReadableSize,
  truncate,
  sortObjects,
  parseDateTime,
  parseDateFromNow,
  deleteStaleSharedContainers,
  DEV,
} from "@/common/conv";
import {
  mdiTrayArrowDown,
  mdiShareVariantOutline,
  mdiDotsHorizontal,
  mdiPail,
} from "@mdi/js";
import {
  toggleEditTagsModal,
  getSharingContainers,
  getSharedContainers,
  getAccessDetails,
  getPaginationOptions,
  toggleCopyBucketModal,
  checkIfItemIsLastOnPage,
  addErrorToastOnMain,
} from "@/common/globalFunctions";
import {
  setPrevActiveElement,
  disableFocusOutsideModal,
} from "@/common/keyboardNavigation";
import { toRaw } from "vue";
import {
  awsDeleteBucket,
  awsDeleteObject,
  awsListObjects,
  getBucketMetadata,
} from "@/common/s3commands";

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
      sharingContainers: [],
      sharedContainers: [],
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
    sharingUpdated () {
      return this.$store.state.sharingUpdated;
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
      Promise.all([this.getSharingContainers(), this.getSharedContainers()])
        .then(() => this.getPage());
    },
    showTimestamp() {
      this.getPage();
    },
    locale() {
      this.setHeaders();
      this.getPage();
      this.setPagination();
    },
    sharingUpdated() {
      if (this.sharingUpdated) {
        this.getSharingContainers().then(() => this.getPage());
        this.$store.commit("setSharingUpdated", false);
      }
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
  expose: ["toFirstPage"],
  methods: {
    toFirstPage() {
      this.paginationOptions.currentPage = 1;
    },
    async getSharingContainers () {
      this.sharingContainers =
        await getSharingContainers(this.active.id, this.abortController.signal);
    },
    async getSharedContainers () {
      this.sharedContainers =
        await getSharedContainers(this.active.id, this.abortController.signal);
    },
    async getPage () {
      let offset = 0;
      let limit = this.conts?.length;

      if (!this.disablePagination || this.conts?.length > 100) {
        offset =
          this.paginationOptions.currentPage
          * this.paginationOptions.itemsPerPage
          - this.paginationOptions.itemsPerPage;

        limit = this.paginationOptions.itemsPerPage;
      }

      const getSharedStatus = (bucketName) => {
        if (this.sharingContainers.indexOf(bucketName) > -1) {
          return this.$t("message.table.sharing");
        } else if (this.sharedContainers.findIndex(
          cont => cont.container === bucketName) > -1) {
          return this.$t("message.table.shared");
        }
        return "";
      };

      // Filter out segment buckets for rendering
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

      let containersPage = [];

      await Promise.all(
        mappedContainers
          .slice(offset, offset + limit).map(async (
            item,
          ) => {
            let bucketMetadata = await getBucketMetadata(
              item.name,
              new Date(item.last_modified),
            );

            containersPage.push({
              name: {
                value: truncate(item.name),
                component: {
                  tag: "c-link",
                  params: {
                    href: "javascript:void(0)",
                    color: "dark-grey",
                    path: mdiPail,
                    iconFill: "primary",
                    iconStyle: {
                      marginRight: "1rem",
                      flexShrink: "0",
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
                value: bucketMetadata.count,
              },
              size: {
                value: getHumanReadableSize(
                  bucketMetadata.bytes,
                  this.locale,
                ),
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
                    ...(item.tags && !item.tags?.length
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
                  this.locale, bucketMetadata.last_modified, this.$t, false) :
                  parseDateFromNow(
                    this.locale,
                    bucketMetadata.last_modified,
                    this.$t,
                  ),
              },
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
                        testid: "download-container",
                        text: true,
                        size: "small",
                        title: this.$t("message.download.download"),
                        onClick: ({ event }) => {
                          this.beginDownload(
                            item.name,
                            item.owner ? item.owner : "",
                            event.isTrusted,
                          );
                        },
                        target: "_blank",
                        path: mdiTrayArrowDown,
                        disabled: (
                          item.owner && item.accessRights?.length === 0
                        ) || !bucketMetadata.count,
                      },
                    },
                  },
                  // Share button is disabled for Shared (with you) buckets
                  {
                    value: this.$t("message.share.share"),
                    component: {
                      tag: "c-button",
                      params: {
                        testid: "share-container",
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
                              this.openCopyBucketModal(item.name, item.owner);
                              const menuItems = document
                                .querySelector("c-menu-items");
                              menuItems.addEventListener("keydown", (e) =>{
                                if (e.keyCode === 13) {
                                  this.openCopyBucketModal(
                                    item.name, item.owner, true,
                                  );
                                }
                              });
                            },
                            disabled: !bucketMetadata.bytes,
                          },
                          /*{
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
                        },*/
                          {
                            name: this.$t("message.delete"),
                            action: () => this.delete(
                              item.name, bucketMetadata.count,
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
                              disabled: (item.owner &&
                                (item.accessRights?.length === 0 ||
                                  !bucketMetadata.bytes)),
                            },
                          },
                        },
                      },
                    },
                  },
                ],
              },
            });
          }));

      // Remember to sort the page to preserve order lost with promises
      containersPage = containersPage.sort((a, b) => {
        return a.name.value.localeCompare(b.name.value);
      });

      this.containers = containersPage;

      this.paginationOptions = {
        ...this.paginationOptions,
        itemCount: mappedContainers.length,
      };
    },
    async onSort(event) {
      this.$store.commit("setNewBucket", "");

      this.sortBy = event.detail.sortBy;
      this.sortDirection = event.detail.direction;

      if (this.sortBy === "sharing") {
        let allSharing = this.conts.map(x =>
          this.sharingContainers.includes(x.name)
            ? this.$t("message.table.sharing") : "");
        let allShared = this.conts.map(x =>
          this.sharedContainers.some(cont => cont.container === x.name)
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
    delete: async function (bucket, objects) {
      if (objects > 0) { // If bucket not empty
        addErrorToastOnMain(this.$t("message.container_ops.deleteNote"));
      }
      else { // Delete empty bucket without confirmation
        awsDeleteBucket(bucket).then(async() => {
          // In case the bucket has a legacy segments bucket still in
          // existence we should take care of that as well
          const segmentsBucket = `${bucket}_segments`;
          let segmentsBucketExists = false;

          // List and delete all segment objects matching the deleted bucket.
          const segmentListResp = await awsListObjects(segmentsBucket);
          for (const key of segmentListResp) {
            try {
              await awsDeleteObject(segmentsBucket, key.name);
            } catch (e) {
              if (DEV) {
                console.log(
                  `Failed deleting object ${key.name} in ${segmentsBucket}: `,
                  e,
                );
              }
            }
          }

          // Finally delete the segments bucket
          if (segmentsBucketExists) {
            await awsDeleteBucket(segmentsBucket);
          }

          document.querySelector("#container-toasts").addToast(
            { progress: false,
              type: "success",
              message: this.$t("message.container_ops.deleteSuccess")},
          );
          this.$emit("delete-container", bucket);
          // Delete stale shared containers if the deleted container
          // was shared with other projects
          const sharedDetails = await this.$store.state.client.getShareDetails(
            this.$route.params.project,
            bucket,
          );
          if (sharedDetails.length)
            await deleteStaleSharedContainers(this.$store);
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
    beginDownload(container, owner, eventTrusted) {
      //add test param to test direct downloads
      //by using origin private file system (OPFS)
      //automated testing creates untrusted events
      const test = eventTrusted === undefined ? false : !eventTrusted;

      this.$store.state.s3download.addDownload(
        container,
        [],
        owner,
        test,
      ).then(() => {
        if (DEV) console.log(`Started downloading all objects from container ${container}`);
      }).catch(() => {
        addErrorToastOnMain(this.$t("message.download.error"));
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
        "setBucketName", itemName);

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
    openCopyBucketModal(itemName, itemOwner, keypress) {
      itemOwner
        ? toggleCopyBucketModal(itemName, itemOwner)
        : toggleCopyBucketModal(itemName);
      if (keypress) {
        setPrevActiveElement();
        const copyBucketModal = document.getElementById("copy-bucket-modal");
        disableFocusOutsideModal(copyBucketModal);
      }
      setTimeout(() => {
        const copyBucketInput = document
          .querySelector("#new-copy-bucketName input");
        copyBucketInput.focus();
      }, 300);
    },
  },
};
</script>
