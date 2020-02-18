<template>
  <ul>
    <li
      v-for="details in allDetails"
      :key="details"
    >
      <div class="columns">
        <div class="column is-four-fifths">
          <ul>
            <li>
              {{ $t('message.share.shared_details_to') }}
              {{ details.sharedTo }}
            </li>
            <li>
              {{ $t('message.share.shared_details_address') }}
              {{ details.address }}
            </li>
            <li>
              {{ $t('message.share.shared_details_rights') }}
              {{ details.access }}
            </li>
          </ul>
        </div>
        <div class="column">
          <b-button
            type="is-danger"
            icon-left="delete"
            @click="deleteSingleShare(details.sharedTo)"
          >
            {{ $t('message.share.revoke') }}
          </b-button>
        </div>
      </div>
    </li>
  </ul>
</template>

<script>
import { removeAccessControlMeta } from "@/common/api";

export default {
  props: ["container"],
  data: function () {
    return {
      allDetails: {},
    };
  },
  beforeMount () {
    this.getSharedDetails();
  },
  methods: {
    getSharedDetails: function () {
      this.$store.state.client.getShareDetails(
        this.$route.params.project,
        this.container
      ).then((ret) => {
        this.allDetails = ret;
      });
    },
    deleteSingleShare: function (
      recipient
    ) {
      removeAccessControlMeta(
        this.container,
        recipient
      ).then(() => {
        this.$store.state.client.shareDeleteAccess(
          this.$route.params.project,
          this.container,
          [recipient]
        ).then(() => {this.$router.go(0);});
      });
    },
  },
};
</script>
