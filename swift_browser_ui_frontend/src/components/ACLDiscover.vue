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
            //removed toast for page that will be deleted
          } else {
            //removed toast for page that will be deleted
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
