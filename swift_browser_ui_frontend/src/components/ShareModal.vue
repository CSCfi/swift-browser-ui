<template>
  <c-card class="share-card">
    <header>
      <h3 class="title is-3">
        {{ $t('message.share.share_title') }}
        <br>
        <q>{{ folderName }}</q>
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
        <h4 class="title is-4 has-text-dark">
          {{ $t("message.share.share_other_projects") }}
        </h4>
        <c-alert type="info">
          <div class="guide-content">
            <section>
              <p>
                {{ $t("message.share.share_guide_heading") }}
              </p>
              <div v-show="openShareGuide">
                <br>
                <p>
                  {{ $t("message.share.share_guide_step1") }}
                </p>
                <p>
                  {{ $t("message.share.share_guide_step2") }}
                </p>
              </div>
            </section>
            <c-link
              underline
              @click="toggleShareGuide"
            >
              <span>
                {{ openShareGuide ? $t("message.share.close")
                  : $t("message.share.guide")
                }}
              </span>
            </c-link>
          </div>
        </c-alert>
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
          <c-menu
            :items.prop="accessRights"
            no-hover
          >
            <c-menu-item>{{ currentAccessRight }}</c-menu-item>
          </c-menu>
          <c-button
            :loading="loading"
            @click="shareSubmit()"
          >
            {{ $t('message.share.confirm') }}
          </c-button>
        </c-flex>
      </c-container>
    </c-card-content>
  </c-card>
</template>

<script>
import {
  addAccessControlMeta,
  getSharedContainerAddress,
} from "@/common/api";

export default {
  name: "ShareModal",
  data () {
    return {
      tags: [],
      openShareGuide: false,
      read: false,
      write: false,
      loading: false,
      menuTitle: "message.share.give_rights",
      accessRights: [],
      currentAccessRight: this.$t("message.share.give_rights"),
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
  created: function () {
    this.setAccessRights();
  },
  watch: {
    locale: function () {
      this.setAccessRights();
      this.currentAccessRight = this.$t(this.menuTitle);
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
  methods: {
    setAccessRights: function () {
      this.accessRights = [
        {
          name: this.$t("message.share.read_perm"),
          action: () => this.giveReadAccess(),
        },
        {
          name: this.$t("message.share.write_perm"),
          action: () => this.giveReadWriteAccess(),
        },
      ];
    },
    giveReadAccess: function () {
      this.currentAccessRight = this.accessRights[0].name;
      this.read = true;
      this.write = false;
    },
    giveReadWriteAccess: function () {
      this.currentAccessRight = this.accessRights[1].name;
      this.read = true;
      this.write = true;
    },
    shareSubmit: function () {
      this.loading = true;
      this.shareContainer().then(
        (ret) => {
          this.loading = false;
          if (ret) {
            this.$router.push({
              name: "SharedFrom",
              params: {
                project: this.$store.state.active.id,
              },
            });
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
        this.$buefy.toast.open({
          duration: 5000,
          message: this.$t("message.share.fail_noperm"),
          type: "is-danger",
        });
        return false;
      }
      if (this.tags.length < 1) {
        this.$buefy.toast.open({
          duration: 5000,
          message: this.$t("message.share.fail_noid"),
          type: "is-danger",
        });
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
          this.$buefy.toast.open({
            duration: 5000,
            message: this.$t("message.share.fail_duplicate"),
            type: "is-danger",
          });
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
      this.currentAccessRight = this.$t(this.menuTitle);
    },
  },
};
</script>

<style lang="scss" scoped>
  .share-card {
    padding: 3rem;
    position: absolute;
    top: -8rem;
    left: 0;
    right: 0;
  }

  @media screen and (max-height: 720px) {
    .share-card {
      max-height: 70vh;
      top: -30vh;
    }
    c-card-content  {
      overflow-y: scroll;
    }
  }

  header {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    & > h3 {
      color: var(--csc-dark-grey);
      margin: 0 !important;
      width: 100%;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }

  c-card-content {
    margin-top: 1rem;
    padding: 0;
    & > * {
      margin: 0 !important;
    };
    & > p {
      margin-top: -1rem !important;
      font-size: 0.875rem;
    }
  }

  .guide-content {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    font-size: 0.875rem;
    & > section {
      margin-right: 24px;
    }
  }

  c-link > span {
    font-size: 0.875rem;
  }

  .field {
    margin: 2rem 0 0 0;
  }

  c-flex {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }

  c-menu {
    border: 1px solid var(--csc-dark-grey);
  }

  c-menu-item {
    background-color: transparent;
  }

</style>
