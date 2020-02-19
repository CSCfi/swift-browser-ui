<template>
  <div
    id="sharingview"
    class="contents"
  >
    <form action="">
      <div>
        <header>
          <h1 class="title sharinghead">
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
          </b-field>
          <b-field
            :label="$t('message.share.field_label')"
            label-position="on-border"
          >
            <b-taginput
              v-model="tags"
              :placeholder="$t('message.share.field_placeholder')"
            />
          </b-field>
          <b-field
            :label="$t('message.share.container_label')"
            label-position="on-border"
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

<style scoped>
  #sharingview {
    width: auto;
    margin-top: 2%;
    margin-left: 5%;
    margin-right: 5%;
  }

  .sharingbutton {
    margin: 1%;
  }

  .sharinghead {
    margin: 1%;
  }
</style>

<script>
import {
  addAccessControlMeta,
  getSharedContainerAddress,
} from "@/common/api";

export default {
  name: "Sharing",
  data () {
    return {
      tags: [],
      container: "",
      read: false,
      write: false,
      loading: false,
    };
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
        }
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
          await getSharedContainerAddress()
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
        this.tags 
      );
      return true;
    },
  },
};
</script>
