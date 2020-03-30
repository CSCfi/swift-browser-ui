<template>
  <div>
    <b-field grouped>
      <b-field
        horizontal
        label="Destination container"
        message="Insert replication destination container here"
        expanded
      >
        <b-input
          v-model="destination"
          name="container"
          expanded
        />
      </b-field>
      <b-field>
        <p class="control">
          <button
            class="button is-primary"
            @click="replicateContainer ()"
          >
            Replicate
          </button>
        </p>
      </b-field>
    </b-field>
  </div>
</template>

<script>
import {swiftCopyContainer} from "@/common/api";

export default {
  name: "ReplicationView",
  data () {
    return {
      destination: this.$route.params.container,
      project: this.$route.params.project,
    };
  },
  computed: {
    active () {
      return this.$store.state.active;
    },
  },
  methods: {
    replicateContainer: function () {
      // Initiate the container replication operation
      swiftCopyContainer(
        this.active.id,
        this.destination,
        this.$route.params.project,
        this.$route.params.container,
      ).then(() => {
        this.$buefy.toast.open({
          message: "Initiated container replication in the background.",
          type: "is-success",
        });
        this.$router.go(-1);
      }).catch(() => {
        this.$buefy.toast.open({
          message: "Container replication failed",
          type: "is-danger",
        });
      });
    },
  },
};
</script>
