<template>
  <div
    id="replicateView"
    class="contents"
  >
    <b-message
      v-if="destinationExists"
      type="is-danger"
    >
      {{ $t("message.replicate.destinationExists") }}
    </b-message>
    <b-field grouped>
      <b-field
        :label="$t('message.replicate.destinationLabel')"
        :message="$t('message.replicate.destinationMessage')"
        expanded
      >
        <b-input
          v-model="destination"
          name="container"
          expanded
        />
        <p class="control">
          <button
            v-if="destinationExists"
            class="button is-primary"
            disabled
          >
            {{ $t("message.copy") }}
          </button>
          <button
            v-else
            class="button is-primary"
            @click="replicateContainer()"
          >
            {{ $t("message.copy") }}
          </button>
        </p>
      </b-field>
    </b-field>
  </div>
</template>

<script>
import {swiftCopyContainer} from "@/common/api";
import escapeRegExp from "lodash/escapeRegExp";
import { useObservable } from "@vueuse/rxjs";
import { liveQuery } from "dexie";

export default {
  name: "ReplicationView",
  data () {
    return {
      destination: this.$route.params.container,
      project: this.$route.params.project,
      destinationExists: false,
      containers: { value: [] },
    };
  },
  computed: {
    active () {
      return this.$store.state.active;
    },
  },
  watch: {
    destination: function () {
      this.checkDestination();
    },
  },
  created () {
    this.fetchContainers().then(() => this.checkDestination());
  },
  methods: {
    fetchContainers: async function () {
      if (
        this.active.id === undefined &&
        this.$route.params.project === undefined
      ) {
        return;
      }
      this.containers = useObservable(
        liveQuery(() => 
          this.$store.state.db.containers
            .where({ projectID: this.$route.params.project })
            .toArray(),
        ),
      );
      await this.$store.dispatch("updateContainers", {
        projectID: this.$route.params.project,
        signal: null,
      });
    },
    replicateContainer: function () {
      // Initiate the container replication operation
      swiftCopyContainer(
        this.active.id,
        this.destination,
        this.$route.params.from,
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
      for (let cont of this.containers.value) {
        if (cont.name.match(re)) {
          this.destinationExists = true;
          return;
        }
      }
      if (this.$route.params.container.match(re)) {
        this.destinationExists = true;
        return;
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
  margin: auto;
}
#destinationButton {
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
