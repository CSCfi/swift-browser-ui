<template>
  <section>
    <b-field
      label="Project"
      v-if="projects.length > 1"
    >
      <b-select
        :placeholder="active.name"
        v-model="project"
      >
        <option
          v-for="item in projects"
          :value="item.id"
          :key="item.id"
        >
          {{ project.name }}
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
  </section>
</template>

<script>
export default {
  name: "DirectRequest",
  data () {
    return {
      container: "",
      owner: "",
      project: "",
      chosen: "",
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
    this.project = active.id
    checkMultiProject();
    this.setParams();
  },
  methods: {
    requestShare: function () {
      this.$store.state.requestClient.addAccessRequest(
        this.project,
        this.container,
        this.owner
      ).then(() => {
        this.$router.go();
      });
    },
    setParams: function () {
      this.container = this.$route.query.container;
      this.owner = this.$route.query.owner;
    },
    checkMultiProject: function () {
      if (projects.length > 1) {
        this.$buefy.notification.open({
          indefinite: true,
          message: "Account has access to multiple projects. " +
          "Please verify that the correct project is set active in the " +
          "menu, and submit the request with the Request button.",
          type: "is-danger"
        })
      }

      else {
        this.requestShare()
      }
    }
  },
};
</script>
