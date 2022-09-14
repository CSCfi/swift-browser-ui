<template>
  <c-card class="share-card">
    <header>
      <h3 class="title is-3 has-text-dark">
        {{ $t('message.share.share_title') }}
        {{ folderName }}
      </h3>
      <c-button
        text
        @click="toggleShareModal"
      >
        <c-icon-button text>
          <i class="mdi mdi-close" />
        </c-icon-button>
        {{ $t("message.share.close") }}
      </c-button>
    </header>
    <c-card-content>
      <h6 class="subtitle is-6 has-text-dark">
        {{ $t("message.share.share_subtitle1") }}
        <b>{{ $t("message.container_ops.myResearchProject") }}</b>
      </h6>
      <p class="has-text-dark">
        {{ $t("message.share.share_subtitle2") }}
      </p>
      <c-container>
        <c-row justify="space-between" align="center">
          <h4 class="title is-4 has-text-dark">
            {{ $t("message.share.share_other_projects") }}
          </h4>
          <c-flex
            class="toggle-instructions"
            @click="toggleShareGuide"
          >
            <c-icon-button text v-show="!openShareGuide">
              <i class="mdi mdi-information-outline" />
            </c-icon-button>
            <c-link underline>
              {{ openShareGuide ? $t("message.share.close_instructions")
                                : $t("message.share.instructions")
              }}
            </c-link>
          </c-flex>
        </c-row>
        <div class="guide-content" v-show="openShareGuide">
          <p>
            {{ $t("message.share.share_guide_step1") }}
          </p>
          <p>
            {{ $t("message.share.share_guide_step2") }}
          </p>
        </div>
        <b-field
          custom-class="field"
          type="is-dark"
        >
          <b-taginput
            v-model="tags"
            ellipsis
            :placeholder="$t('message.share.field_placeholder')"
          />
        </b-field>
        <c-flex>
          <c-select
            v-control
            v-csc-model="sharedAccessRight"
            shadow="false"
            :label="$t('message.share.permissions')"
            :items.prop="accessRights"
            placeholder="Select permission"
            @changeValue="onSelectPermission($event)"
          />
          <c-button
            :loading="loading"
            @click="shareSubmit()"
          >
            {{ $t('message.share.confirm') }}
          </c-button>
        </c-flex>
      </c-container>
      <c-container v-show="sharedDetails.length > 0">
        <c-alert
          v-show="isShared"
          type="success"
        >
          <div class="shared-notification">
            {{ $t('message.share.shared_successfully') }}
            <c-button
              text
              size="small"
              @click="closeSharedNotification()"
            >
              <c-icon-button text>
                <i class="mdi mdi-close" />
              </c-icon-button>
              {{ $t("message.share.close") }}
            </c-button>
          </div>
        </c-alert>
        <ShareModalTable
          :shared-details="sharedDetails"
          :folder-name="folderName"
          :accessRights="accessRights"
          @removeSharedFolder="removeSharedFolder"
        />
      </c-container>
    </c-card-content>
    <c-toasts
      id="shareModal-toasts"
      vertical="top"
      data-testid="shareModal-toasts"
    />
  </c-card>
</template>

<script>
import {
  addAccessControlMeta,
  getSharedContainerAddress,
} from "@/common/api";
import ShareModalTable from "@/components/ShareModalTable";

export default {
  name: "ShareModal",
  components: { ShareModalTable },
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
    };
  },
  computed: {
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
      if (this.folderName)  this.getSharedDetails();
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
            this.isShared = true;
            this.getSharedDetails();
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
      }
      catch(error) {
        if (error instanceof TypeError) {
          document.querySelector("#shareModal-toasts").addToast(
            {
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
      return true;
    },
    toggleShareGuide: function () {
      this.openShareGuide = !this.openShareGuide;
    },
    toggleShareModal: function () {
      this.$store.commit("toggleShareModal", false);
      this.$store.commit("setFolderName", "");
      this.openShareGuide = false;
      this.tags = [];
      this.isShared = false;
    },
    closeSharedNotification: function () {
      this.isShared = false;
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
    removeSharedFolder: function (folderData) {
      this.sharedDetails = this.sharedDetails.filter(
        item => {
          return item.sharedTo !== folderData.projectId.value;
        });
    },
  },
};
</script>

<style lang="scss" scoped>
@import "@/css/prod.scss";

.share-card {
  padding: 3rem 2rem 0 2rem;
  position: absolute;
  top: -8rem;
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
    padding: 1rem 1rem 6rem 1rem;
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
    & > p {
      margin-top: -1rem !important;
      font-size: 0.875rem;
    }
  }

  header {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    padding: 0 1rem;
    & > h3 {
      margin: 0 !important;
      width: 100%;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }

  .toggle-instructions {
    justify-content: flex-end;
    align-items: center;
  }

  h4 {
    margin: 0 !important;
  }

  .guide-content {
    margin-top: 1rem;
    background-color: $csc-primary-lighter;
    justify-content: space-between;
    padding: 1rem;
  }

  c-select {
    color: var(--csc-dark-grey);
  }

  c-link > span {
    font-size: 0.875rem;
  }

  .field {
    margin: 2rem 0 0 0;
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

</style>
