<template>
  <section>
    <b-button
      is-primary
      is-inverted
      @click="syncShares"
    >
      Discover shares
    </b-button>
  </section>
</template>

<script>
import {getAccessControlMeta} from "@/common/api";

export default {
  name: "ACLDiscoverButton",
  methods: {
    syncShares: function () {
      getAccessControlMeta().then(async (acl) => {
        let amount = 0;
        let aclmeta = acl.access;
        let currentsharing = await this.$store.state.client.getShare(
          this.$store.state.active.id
        );

        for (let container of Object.keys(aclmeta)) {
          let currentdetails = [];
          if (currentsharing.includes(container)) {
            currentdetails = await this.$store.state.client.getShareDetails(
              this.$store.state.active.id,
              container
            );
          }
          for (let share of Object.keys(aclmeta[container])) {
            if (await this.checkDuplicate(
              container,
              share,
              currentdetails
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
            message: "Successfully synchronized ".concat(
              amount,
              " shares"
            ),
            type: "is-success",
          });
        } else {
          this.$buefy.toast.open({
            message: "No new sharing information to synchronize.",
            type: "is-success",
          });
        }
      });
    },
    checkDuplicate: async function (
      container,
      share,
      currentdetails
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
