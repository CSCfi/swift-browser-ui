<template>
  <div>
    <b-button
      v-if="smallsize"
      type="is-primary"
      size="is-small"
      outlined
      :inverted="inverted"
      @click="$router.push({
        name: 'ReplicateContainer',
        params: {
          container: getContainer(),
          project: getProject(),
        }
      })"
    >
      Copy
    </b-button>
    <b-button
      v-else
      type="is-primary"
      outlined
      :inverted="inverted"
      @click="$router.push({
        name: 'ReplicateContainer',
        params: {
          container: getContainer(),
          project: getProject(),
        }
      })"
    >
      Copy
    </b-button>
  </div>
</template>

<script>
export default {
  name: "ReplicateContainerButton",
  props: [
    "project",
    "container",
    "smallsize",
    "inverted",
  ],
  computed: {
    active () {
      return this.$store.state.active;
    },
  },
  methods: {
    getProject: function () {
      if(this.$route.params.user == undefined) {
        return this.$props.project ? this.$props.project :
          this.$route.params.project;
      }
      return this.active.id;
    },
    getContainer: function () {
      return this.$props.container ? this.$props.container :
        this.$route.params.container;
    },
  },
};
</script>
