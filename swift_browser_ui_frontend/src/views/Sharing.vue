<template>
  <div
    id="sharingview"
    class="contents"
  >
    <form action="">
      <div class="contents">
        <header>
          <h1 class="title is-3 sharinghead">
            {{ $t('message.share.share_cont') }}
          </h1>
        </header>
        <section>
          <b-field grouped>
            <b-switch
              v-model="read"
            >
              {{ $t('message.share.read_perm') }}
            </b-switch>
            <b-switch
              v-model="write"
            >
              {{ $t('message.share.write_perm') }}
            </b-switch>
            <b-button
              class="syncbutton"
              type="is-primary"
              icon-left="refresh"
              outlined
              @click="syncShareRequests()"
            >
              {{ $t('message.share.sync_requests') }}
            </b-button>
          </b-field>
          <b-field
            :label="$t('message.share.field_label')"
          >
            <b-taginput
              v-model="tags"
              :placeholder="$t('message.share.field_placeholder')"
            />
          </b-field>
          <b-field
            :label="$t('message.share.container_label')"
          >
            <b-input v-model="container" />
          </b-field>
        </section>
        <section>
          <b-button
            class="is-light sharingbutton"
            @click="$router.go(-1)"
          >
            {{ $t('message.share.cancel') }}
          </b-button>
          <b-button
            class="is-primary sharingbutton"
            :loading="loading"
            @click="shareSubmit()"
          >
            {{ $t('message.share.confirm') }}
          </b-button>
        </section>
      </div>
    </form>
  </div>
</template>

<script>
import {
  addAccessControlMeta,
  getSharedContainerAddress,
} from "@/common/api";

export default {
  name: "SharingView",
  data () {
    return {
      tags: [],
      container: "",
      read: false,
      write: false,
      loading: false,
    };
  },
  watch: {
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
  beforeMount () {
    this.checkContainer();
  },
  methods: {
    checkContainer: function () {
      if (this.$route.query.container != undefined) {
        this.container = this.$route.query.container;
      }
    },
    syncShareRequests: function () {
      if (!this.container) {
        this.$buefy.toast.open({
          duration: 5000,
          message: this.$t("message.share.request_sync_nocont"),
          type: "is-danger",
        });
        return;
      }
      this.$store.state.requestClient.listOwnedRequests(
        this.$store.state.active.id,
      ).then((ret) => {
        let requests = ret.filter(req => req.container == this.container);
        let request_amount = 0;
        for (let request of requests) {
          this.tags.push(request.user);
          request_amount++;
        }
        if (request_amount > 0) {
          this.$buefy.toast.open({
            duration: 5000,
            message: this.$t("message.share.request_synced"),
            type: "is-success",
          });
        }
        else {
          this.$buefy.toast.open({
            duration: 5000,
            message: this.$t("message.share.request_not_synced"),
            type: "is-success",
          });
        }
      });
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
      if (this.container == "") {
        this.$buefy.toast.open({
          duration: 5000,
          message: this.$t("message.share.fail_nocont"),
          type: "is-danger",
        });
        return false;
      }
      try {
        await this.$store.state.client.shareNewAccess(
          this.$store.state.active.id,
          this.container,
          this.tags,
          rights,
          await getSharedContainerAddress(),
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
        this.container,
        rights,
        this.tags, 
      );
      return true;
    },
  },
};
</script>

<style scoped>
  #sharingview {
    width: auto;
    margin-left: 5%;
    margin-right: 5%;
  }

  .sharingbutton {
    margin: 1% 0;
  }

  .sharingbutton + .sharingbutton {
    margin-left: 1%;
  }

  .syncbutton {
    margin-left: 1%;
  }

  .sharinghead {
    margin: 1% 1% 1% 0;
  }
</style>
