<template>
  <div>
    <b-field
      horizontal
      :label="$t('message.request.container')"
      :message="$t('message.request.container_message')"
    >
      <b-input 
        v-model="container"
        name="container"
        expanded
      />
    </b-field>

    <b-field
      horizontal
      :label="$t('message.request.owner')"
      :message="$t('message.request.owner_message')"
    >
      <b-input
        v-model="owner"
        name="owner"
        expanded
      />
    </b-field>

    <b-field>
      <p class="control">
        <button
          class="button is-primary"
          @click="requestShare ()"
        >
          {{ $t('message.request.request') }}
        </button>
      </p>
    </b-field>
  </div>
</template>

<script>
export default {
  name: "RequestSharing",
  data () {
    return {
      container: "",
      owner: "",
    };
  },
  methods: {
    requestShare: function () {
      this.$store.state.requestClient.addAccessRequest(
        this.$route.params.project,
        this.container,
        this.owner
      ).then(() => {
        this.$router.go();
      });
    },
  },
};
</script>
