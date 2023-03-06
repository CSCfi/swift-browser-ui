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
              <b-taglist>
                <b-tag
                  v-if="details.access.includes('r')"
                  type="is-primary"
                >
                  {{ $t('message.share.shared_details_read') }}
                </b-tag>
                <b-tag
                  v-if="details.access.includes('w')"
                  type="is-primary"
                >
                  {{ $t('message.share.shared_details_write') }}
                </b-tag>
              </b-taglist>
            </li>
          </ul>
        </div>
        <div class="column">
          <b-button
            class="container-share-revoke-button"
            type="is-danger"
            size="is-small"
            icon-left="delete"
            outlined
            @click="deleteSingleShare(details.sharedTo)"
          >
            {{ $t('message.share.revoke_project') }}
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
  computed: {
    project () {
      return this.$route.params.project;
    },
  },
  beforeMount () {
    this.getSharedDetails();
  },
  methods: {
    getSharedDetails: function () {
      this.$store.state.client.getShareDetails(
        this.$route.params.project,
        this.container,
      ).then((ret) => {
        this.allDetails = ret;
      });
    },
    deleteSingleShare: function (
      recipient,
    ) {
      removeAccessControlMeta(
        this.project,
        this.container,
        recipient,
      ).then(() => {
        this.$store.state.client.shareDeleteAccess(
          this.$route.params.project,
          this.container,
          [recipient],
        ).then(() => {
          //removed toast for page that will be deleted
        });
      });
    },
  },
};
</script>

<style>
  .container-share-revoke-button{
    margin-top: auto;
    margin-bottom: auto;
  }
</style>
