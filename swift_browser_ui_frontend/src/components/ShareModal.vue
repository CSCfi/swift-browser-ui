<template>
  <c-card class="share-card">
    <c-card-actions
      justify="space-between"
    >
      <h2 class="title is-4 has-text-dark">
        {{ $t('message.share.share_title') }}
        {{ folderName }}
      </h2>
      <c-button
        text
        @click="toggleShareModal"
        @keyup.enter="toggleShareModal"
      >
        <c-icon
          :path="mdiClose"
          alt=""
          aria-hidden="true"
        />
        {{ $t("message.share.close") }}
      </c-button>
    </c-card-actions>
    <c-card-content id="share-card-modal-content">
      <c-container>
        <c-row
          justify="space-between"
          align="center"
        >
          <h3 class="title is-5 has-text-dark">
            {{ $t("message.share.share_other_projects") }}
          </h3>
          <c-flex
            class="toggle-instructions"
            :aria-label="$t('label.shareid_instructions')"
            @click="toggleShareGuide"
            @keyup.enter="toggleShareGuide"
          >
            <c-icon
              :path="mdiInformationOutline"
              alt=""
              aria-hidden="true"
            />
            <c-link
              underline
              tabindex="0"
            >
              {{ openShareGuide ? $t("message.share.close_instructions")
                : $t("message.share.instructions")
              }}
            </c-link>
          </c-flex>
        </c-row>
        <div
          v-show="openShareGuide"
          class="content guide-content"
        >
          <p>
            {{ $t("message.share.share_guide_intro") }}
          </p>
          <p>
            {{ $t("message.share.share_guide_step1") }}
          </p>
          <p>
            {{ $t("message.share.share_guide_step2") }}
          </p>
          <ul>
            <li
              v-for="(item, i) in
                $tm('message.share.share_guide_step2_list')"
              :key="i"
            >
              {{ item }}
            </li>
          </ul>
        </div>
        <TagInput
          :tags="tags"
          aria-label="label.list_of_shareids"
          placeholder="message.share.field_placeholder"
          @addTag="addingTag"
          @deleteTag="deletingTag"
        />
        <c-flex>
          <c-select
            v-model="sharedAccessRight"
            v-csc-control
            shadow="false"
            :label="$t('message.share.permissions')"
            :items.prop="accessRights"
            :placeholder="$t('message.share.permissions')"
            @changeValue="onSelectPermission($event)"
          />
          <c-button
            :loading="loading"
            @click="shareSubmit"
            @keyup.enter="shareSubmit"
          >
            {{ $t('message.share.confirm') }}
          </c-button>
        </c-flex>
      </c-container>
      <c-alert
        v-show="isShared || isPermissionRemoved || isPermissionUpdated"
        type="success"
      >
        <div class="shared-notification">
          {{ isShared ? $t('message.share.shared_successfully')
            : isPermissionUpdated ? $t('message.share.update_permission')
              : $t('message.share.remove_permission')
          }}
          <c-button
            text
            size="small"
            @click="closeSharedNotification"
          >
            <c-icon
              :path="mdiClose"
              alt=""
              aria-hidden="true"
            />
            {{ $t("message.share.close") }}
          </c-button>
        </div>
      </c-alert>
      <c-container v-show="sharedDetails.length > 0">
        <ShareModalTable
          :shared-details="sharedDetails"
          :folder-name="folderName"
          :access-rights="accessRights"
          @removeSharedFolder="removeSharedFolder"
          @updateSharedFolder="updateSharedFolder"
        />
      </c-container>
    </c-card-content>
    <c-toasts
      id="shareModal-toasts"
      data-testid="shareModal-toasts"
    />
  </c-card>
</template>

<script>
import {
  addAccessControlMeta,
  getSharedContainerAddress,
} from "@/common/api";

import {
  addNewTag,
  deleteTag,
} from "@/common/globalFunctions";

import ShareModalTable from "@/components/ShareModalTable.vue";
import TagInput from "@/components/TagInput.vue";
import { mdiClose, mdiInformationOutline } from "@mdi/js";

export default {
  name: "ShareModal",
  components: { ShareModalTable, TagInput },
  data () {
    return {
      tags: [],
      openShareGuide: false,
      read: false,
      write: false,
      loading: false,
      accessRights: [],
      sharedAccessRight: null,
      isShared: false,
      sharedDetails: [],
      isPermissionRemoved: false,
      isPermissionUpdated: false,
      timeout: null,
      mdiClose,
      mdiInformationOutline,
    };
  },
  computed: {
    active() {
      return this.$store.state.active;
    },
    folderName() {
      return this.$store.state.selectedFolderName;
    },
    locale () {
      return this.$i18n.locale;
    },
  },
  watch: {
    locale: function () {
      this.setAccessRights();
    },
    folderName: function () {
      if (this.folderName) this.getSharedDetails();
    },
    read: function () {
      if(!this.read) {
        this.write = false;
      }
    },
    write: function () {
      if(this.write) {
        this.read = true;
      }
    },
  },
  created: function () {
    this.setAccessRights();
  },
  methods: {
    onSelectPermission: function(e) {
      const val = e.target.value.value;
      if (val === "read") this.giveReadAccess();
      else this.giveReadWriteAccess();
    },
    setAccessRights: function () {
      this.accessRights = [
        {
          name: this.$t("message.share.read_perm"),
          value: "read",
        },
        {
          name: this.$t("message.share.write_perm"),
          value: "read and write",
        },
      ];
    },
    giveReadAccess: function () {
      this.read = true;
      this.write = false;
    },
    giveReadWriteAccess: function () {
      this.read = true;
      this.write = true;
    },
    shareSubmit: function () {
      this.loading = true;
      this.shareContainer().then(
        (ret) => {
          this.loading = false;
          if (ret) {
            this.getSharedDetails();
            this.closeSharedNotification();
            this.isShared = true;
            this.closeSharedNotificationWithTimeout();
          }
        },
      );
    },
    shareContainer: async function () {
      let rights = [];
      if (this.read) {
        rights.push("r");
      }
      if (this.write) {
        rights.push("w");
      }
      if (rights.length < 1) {
        document.querySelector("#shareModal-toasts").addToast(
          {
            id: "error-noperm",
            type: "error",
            duration: 5000,
            persistent: false,
            progress: false,
            message: this.$t("message.share.fail_noperm"),
          },
        );
        return false;
      }
      if (this.tags.length < 1) {
        document.querySelector("#shareModal-toasts").addToast(
          {
            id: "error-noid",
            type: "error",
            duration: 5000,
            persistent: false,
            progress: false,
            message: this.$t("message.share.fail_noid"),
          },
        );
        return false;
      }
      try {
        await this.$store.state.client.shareNewAccess(
          this.$store.state.active.id,
          this.folderName,
          this.tags,
          rights,
          await getSharedContainerAddress(this.$route.params.project),
        );
        await this.$store.state.client.shareNewAccess(
          this.$store.state.active.id,
          `${this.folderName}_segments`,
          this.tags,
          rights,
          await getSharedContainerAddress(this.$route.params.project),
        );
      }
      catch(error) {
        if (error instanceof TypeError) {
          document.querySelector("#shareModal-toasts").addToast(
            {
              id: "error-duplicate",
              type: "error",
              duration: 5000,
              persistent: false,
              progress: false,
              message: this.$t("message.share.fail_duplicate"),
            },
          );
          return false;
        }
        else {
          throw error;
        }
      }

      await addAccessControlMeta(
        this.$route.params.project,
        this.folderName,
        rights,
        this.tags,
      );

      await addAccessControlMeta(
        this.$route.params.project,
        `${this.folderName}_segments`,
        rights,
        this.tags,
      );
      return true;
    },
    toggleShareGuide: function () {
      this.openShareGuide = !this.openShareGuide;
    },
    toggleShareModal: function () {
      this.$store.commit("toggleShareModal", false);
      this.$store.commit("setFolderName", "");
      this.sharedAccessRight = null;
      this.openShareGuide = false;
      this.tags = [];
      this.isShared = false;
      this.isPermissionRemoved = false;
      document.querySelector("#shareModal-toasts").removeToast("error-noperm");
      document.querySelector("#shareModal-toasts").removeToast("error-noid");
      document.querySelector("#shareModal-toasts")
        .removeToast("error-duplicate");
    },
    closeSharedNotificationWithTimeout() {
      document.getElementById("share-card-modal-content").scrollTo(0, 0);
      this.timeout = setTimeout(() => this.closeSharedNotification(), 3000);
    },
    closeSharedNotification: function () {
      if (this.timeout !== null) {
        clearTimeout(this.timeout);
      }

      this.isShared = false;
      this.isPermissionRemoved = false;
      this.isPermissionUpdated = false;
    },
    getSharedDetails: function () {
      this.$store.state.client.getShareDetails(
        this.$route.params.project,
        this.folderName,
      ).then((ret) => {
        this.sharedDetails = ret;
        this.tags = [];
      });
    },
    updateSharedFolder: function () {
      this.closeSharedNotification();
      this.isPermissionUpdated = true;
      this.closeSharedNotificationWithTimeout();
    },
    removeSharedFolder: function (folderData) {
      this.closeSharedNotification();
      this.sharedDetails = this.sharedDetails.filter(
        item => {
          return item.sharedTo !== folderData.projectId.value;
        });
      this.isPermissionRemoved = true;
      this.closeSharedNotificationWithTimeout();
    },
    addingTag: function (e, onBlur) {
      this.tags = addNewTag(e, this.tags, onBlur);
    },
    deletingTag: function (e, tag) {
      this.tags = deleteTag(e, tag, this.tags);
    },
  },
};
</script>

<style lang="scss" scoped>

.share-card {
  padding: 3rem 2rem 0 2rem;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  max-height: 75vh;
}

  @media screen and (max-height: 720px) {
    .share-card {
      max-height: 70vh;
      top: -30vh;
    }
  }

  c-card-content  {
    overflow-y: scroll;
    scrollbar-width: 0.5rem;
    padding: 0 1rem 6rem 1rem;
    &::-webkit-scrollbar {
      width: 0.5rem;
    }
    &::-webkit-scrollbar-thumb {
      background: var(--csc-mid-grey);
      border-radius: 10px;
      &:hover {
        background: var(--csc-dark-grey);
      }
    }

    & > * {
      margin: 0 !important;
    };
  }

  c-card-actions > h2 {
    margin: 0 !important;
    width: 100%;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .toggle-instructions {
    justify-content: flex-end;
    align-items: center;
  }

  h3 {
    margin: 0 !important;
  }

  .guide-content {
    margin-top: 1rem;
    background-color: $csc-primary-lighter;
    justify-content: space-between;
    padding: 1rem;
  }

  .guide-content > li {
    font-size: 0.875rem;
  }

  c-select {
    color: $csc-dark-grey;
  }

  c-link > span {
    font-size: 0.875rem;
  }

  c-flex, .shared-notification {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }

  c-alert[type="success"] {
    align-items: center;
    & > .shared-notification {
      color: var(--csc-dark-grey);
    };
    margin-bottom: 1.5rem;
    box-shadow: 2px 4px 4px 0px var(--csc-light-grey);
  }

  c-toasts {
    width: fit-content;
  }

  c-alert[type="success"] {
    align-items: center;
    & > .shared-notification {
      color: var(--csc-dark-grey);
    };
    margin-bottom: 1.5rem;
    box-shadow: 2px 4px 4px 0px var(--csc-light-grey);
  }
</style>
