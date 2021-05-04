<template>
  <div
    id="requestview"
    class="contents"
  >
    <h1 class="title is-3 requesthead">
      Requets access to a container
    </h1>
    <b-field
      v-if="projects.length > 1"
      horizontal
      :label="$t('message.request.project')"
    >
      <b-select
        v-model="project"
        :placeholder="active.name"
      >
        <option
          v-for="item in projects"
          :key="item.id"
          :value="item.id"
        >
          {{ item.name }}
        </option>
      </b-select>
    </b-field>
    <b-field
      horizontal
      :label="$t('message.request.container')"
      :message="$t('message.request.container_message')"
    >
      <b-input 
        v-model="container"
        name="container"
        expanded
        aria-required="true"
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
        aria-required="true"
      />
    </b-field>

    <b-field
      horizontal
    >
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
import delay from "lodash/delay";

export default {
  name: "DirectRequest",
  data () {
    return {
      container: "",
      owner: "",
      project: "",
    };
  },
  computed: {
    projects () {
      return this.$store.state.projects;
    },
    active () {
      return this.$store.state.active;
    },
  },
  beforeMount () {
    this.setActive(50);
    this.checkMultiProject(50);
    this.setParams(50);
  },
  methods: {
    requestShare: function () {
      this.$store.state.requestClient.addAccessRequest(
        this.project,
        this.container,
        this.owner,
      ).then(() => {
        this.$router.go();
      });
    },
    setActive: function (wait) {
      try {
        this.project = this.active.id;
      } catch(ReferenceError) {
        delay(this.setActive, wait, [wait * 2]);
      }
    },
    setParams: function (wait) {
      try {
        this.container = this.$route.query.container;
        this.owner = this.$route.query.owner;
      } catch (ReferenceError) {
        delay(this.setParams, wait, [wait * 2]);
      }
    },
    checkMultiProject: function (wait) {
      try {
        if (this.projects.length > 1) {
          this.$buefy.notification.open({
            indefinite: true,
            message: this.$t("message.request.multi_project"),
            type: "is-danger",
          });
        }

        else {
          this.requestShare();
        }
      } catch (ReferenceError) {
        delay(this.checkMultiProject, wait, [wait * 2]);
      }
    },
  },
};
</script>

<style scoped>
  #requestview {
    width: auto;
    margin-left: 5%;
    margin-right: 5%;
  }
  .requesthead {
    margin: 1% 1% 1% 0;
  }
</style>
