<template>
  <section>
    <b-field
      horizontal
      label="Container / Identifier" 
      message="The requested container name."
    >
      <b-input 
        v-model="container"
        name="container"
        expanded
      />
    </b-field>

    <b-field
      horizontal
      label="Owner"
      message="The requested container owner."
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
          Request
        </button>
      </p>
    </b-field>
  </section>
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
        this.$route.params.user,
        this.container,
        this.owner
      ).then(() => {
        this.$router.go();
      });
    },
  },
};
</script>
