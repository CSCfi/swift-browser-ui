<template>
  <section>
    <b-button
      v-if="!isLoading"
      type="is-primary"
      outlined
      @click="syncShares"
    >
      {{ $t('message.discover.sync_shares') }}
    </b-button>
    <b-button
      v-else
      type="is-primary"
      loading
      outlined
    >
      {{ $t('message.discover.sync_shares') }}
    </b-button>
  </section>
</template>

<script>
import {getAccessControlMeta} from "@/common/api";

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
      getAccessControlMeta().then(async (acl) => {
        let amount = 0;
        let aclmeta = acl.access;
        let currentsharing = await this.$store.state.client.getShare(
          this.$store.state.active.id,
        );

        for (let container of Object.keys(aclmeta)) {
          let currentdetails = [];
          if (currentsharing.includes(container)) {
            currentdetails = await this.$store.state.client.getShareDetails(
              this.$store.state.active.id,
              container,
            );
          }
          for (let share of Object.keys(aclmeta[container])) {
            if (await this.checkDuplicate(
              container,
              share,
              currentdetails,
            )) {
              continue;
            }
            let accesslist = [];
            if (aclmeta[container][share].read) {
              accesslist.push("r");
            }
            if (aclmeta[container][share].write) {
              accesslist.push("w");
            }
            await this.$store.state.client.shareNewAccess(
              this.$store.state.active.id,
              container,
              [share],
              accesslist,
              acl.address,
            );
            amount++;
          }
        }
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
      });
    },
    checkDuplicate: async function (
      container,
      share,
      currentdetails,
    ) {
      for (let detail of currentdetails) {
        if(
          detail.container == container &&
          detail.sharedTo == share
        ) {
          return true;
        }
      }
      return false;
    },
  },
};
</script>
