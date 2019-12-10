<template>
  <ul>
    <li
      v-for="details in allDetails"
      :key="details"
    >
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
    </li>
  </ul>
</template>

<script>
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
  },
};
</script>
