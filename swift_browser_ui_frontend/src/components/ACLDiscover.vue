<template>
  <section>
    <b-button
      v-if="!isLoading"
      type="is-primary"
      outlined
      @click="syncShares"
    >
      {{ $t("message.discover.sync_shares") }}
    </b-button>
    <b-button
      v-else
      type="is-primary"
      loading
      outlined
    >
      {{ $t("message.discover.sync_shares") }}
    </b-button>
  </section>
</template>

<script>
import { syncContainerACLs } from "@/common/conv";

export default {
  name: "ACLDiscoverButton",
  data: function () {
    return {
      isLoading: false,
    };
  },
  methods: {
    syncShares: function () {
      this.isLoading = true;
      syncContainerACLs(this.$store.state.client, this.$store.state.active.id)
        .then((amount) => {
          if (amount > 1) {
            this.$buefy.toast.open({
              message: this.$t("message.discover.sync_success_template").concat(
                amount,
                this.$t("message.discover.sync_success_concat"),
              ),
              type: "is-success",
            });
          } else {
            this.$buefy.toast.open({
              message: this.$t("message.discover.sync_failure_template"),
              type: "is-success",
            });
          }
          this.isLoading = false;
          this.$emit("synced");
        })
        .catch(() => {
          this.isLoading = false;
        });
    },
  },
};
</script>
