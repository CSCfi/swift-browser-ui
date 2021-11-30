<template>
  <div
    id="replicateView"
    class="contents"
  >
    <b-field grouped>
      <b-field
        horizontal
        :label="$t('message.replicate.destinationLabel')"
        :message="$t('message.replicate.destinationMessage')"
        expanded
      >
        <b-input
          v-model="destination"
          name="container"
          expanded
        />
      </b-field>
      <b-field>
        <p 
          id="destinationButton"
          class="control"
        >
          <button
            v-if="destinationExists"
            class="button is-primary"
            disabled
          >
            {{ $t('message.copy') }}
          </button>
          <span
            v-if="destinationExists"
            class="forbiddenDestination"
          >
            {{ $t('message.replicate.destinationExists') }}
          </span>
          <button
            v-else
            class="button is-primary"
            @click="replicateContainer ()"
          >
            {{ $t('message.copy') }}
          </button>
        </p>
      </b-field>
    </b-field>
  </div>
</template>

<script>
import {swiftCopyContainer} from "@/common/api";
import escapeRegExp from "lodash/escapeRegExp";

export default {
  name: "ReplicationView",
  data () {
    return {
      destination: this.$route.params.container,
      project: this.$route.params.project,
      destinationExists: false,
    };
  },
  computed: {
    active () {
      return this.$store.state.active;
    },
    containerCache () {
      return this.$store.state.containerCache;
    },
  },
  watch: {
    destination: function () {
      this.checkDestination();
    },
  },
  mounted () {
    this.checkDestination();
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
          message: this.$t("message.copysuccess"),
          type: "is-success",
        });
        this.$store.dispatch("updateContainers");
        this.$router.go(-1);
      }).catch(() => {
        this.$buefy.toast.open({
          message: this.$t("message.copyfail"),
          type: "is-danger",
        });
      });
    },
    checkDestination: function () {
      // request parameter should be sanitized first
      var safeKey = escapeRegExp(this.destination);
      let re = new RegExp("^".concat(safeKey, "$"));
      for (let cont of this.containerCache) {
        if (cont.name.match(re)) {
          this.destinationExists = true;
          return;
        }
      }
      this.destinationExists = false;
    },
  },
};
</script>

<style scoped>
.forbiddenDestination {
  margin-top: auto;
  margin-bottom: auto;
}
#replicateView {
  width: 90%;
}
#destinationButton {
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
