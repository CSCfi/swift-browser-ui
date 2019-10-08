<template>

<ul>
  <li
    v-for="details in allDetails"
    :key="details"
  >
    <ul>
      <li>
        Shared to: {{ details.sharedTo }}
      </li>
      <li>
        Container address: {{ details.address }}
      </li>
      <li>
        Given Rights: {{ details.access }}
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
      allDetails: {}
    };
  },
  beforeMount () {
    this.getSharedDetails();
  },
  methods: {
    getSharedDetails: function () {
      this.$store.state.client.get_share_details(
        this.$route.params.user,
        this.container
      ).then((ret) => {
        this.allDetails = ret;
      })
    },
  }
}
</script>
