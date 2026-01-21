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
  checkIfItemIsLastOnPage,
  getPaginationOptions,
  sortObjects,
  truncate,
} from "@/common/tableFunctions";
import {
  mdiTrayArrowDown,
  mdiShareVariantOutline,
  mdiDotsHorizontal,
  mdiPail,
} from "@mdi/js";
import {
  DEV,
  toggleEditTagsModal,
  toggleCopyBucketModal,
  addErrorToastOnMain,
  checkAndAddBucketCors,
} from "@/common/globalFunctions";
import {
  deleteStaleShares,
  getSharingContainers,
  getSharedContainers,
  getAccessDetails,
} from "@/common/share";
import {
  setPrevActiveElement,
  disableFocusOutsideModal,
} from "@/common/keyboardNavigation";
import { toRaw } from "vue";
import {
  awsDeleteBucket,
  awsDeleteObject,
  awsListObjects,
  checkBucketEmpty,
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

      mappedContainers
        .slice(offset, offset + limit).map((
          item,
        ) => {
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
            sharing: {
              value: getSharedStatus(item.name),
            },
            actions: {
              value: null,
              sortable: null,
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
                        this.handleDownloadClick(
                          item.name,
                          item.owner ? item.owner : "",
                          event.isTrusted,
                        );
                      },
                      target: "_blank",
                      path: mdiTrayArrowDown,
                      disabled: (
                        item.owner && item.accessRights?.length === 0
                      ),
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
                            this.handleCopyClick(item.name, item.owner);
                            const menuItems = document
                              .querySelector("c-menu-items");
                            menuItems.addEventListener("keydown", (e) =>{
                              if (e.keyCode === 13) {
                                this.handleCopyClick(
                                  item.name, item.owner, true,
                                );
                              }
                            });
                          },
                        },
                        {
                          name: this.$t("message.delete"),
                          action: () => this.handleDeleteClick(item.name),
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
                              (item.accessRights?.length === 0),
                          },
                        },
                      },
                    },
                  },
                },
              ],
            },
          });
        });

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
          width: "50%",
        },
        {
          key: "sharing",
          value: this.$t("message.table.shared_status"),
          sortable: false,
        },
        {
          key: "actions",
          align: "end",
          justify: "end",
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
    ensureBucketState: async function (bucket, shouldBeEmpty, errorMsg) {
      // There is no CORS check on bucket list fetch, only share sync
      // Make sure it is in place before fetching objects
      await checkAndAddBucketCors(this.active.id, bucket);
      const isEmpty = await checkBucketEmpty(bucket);
      if (isEmpty === shouldBeEmpty) {
        return true;
      }
      addErrorToastOnMain(errorMsg);
      return false;
    },
    handleDeleteClick: async function (bucket) {
      // Show error if attempting to delete a non-empty bucket
      const bucketEmpty = await this.ensureBucketState(
        bucket, true, this.$t("message.container_ops.deleteEmpty"));
      if (!bucketEmpty) return;
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
          // Delete stale shares if the deleted bucket
          // was shared with other projects
          const sharedDetails = await this.$store.state.sharingClient.getShareDetails(
            this.$route.params.project,
            bucket,
          );
          if (sharedDetails.length) await deleteStaleShares(this.active.id, bucket);
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
    handleDownloadClick: async function(container, owner, eventTrusted) {
      // Don't attempt to download an empty bucket
      const bucketHasContent = await this.ensureBucketState(
        container, false, this.$t("message.container_ops.downloadNotEmpty"));
      if (!bucketHasContent) return;

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
    handleCopyClick: async function(bucket, owner, keypress) {
      // Don't attempt to copy an empty bucket
      const bucketHasContent = await this.ensureBucketState(
        bucket, false, this.$t("message.container_ops.copyNotEmpty"));
      if (!bucketHasContent) return;

      owner
        ? toggleCopyBucketModal(bucket, owner)
        : toggleCopyBucketModal(bucket);
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
