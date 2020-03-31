<template>
  <div>
    <a
      v-if="smallsize"
      class="button is-primary is-outlined is-small"
      @click="$router.push({
        name: 'ReplicateContainer',
        params: {
          container: getContainer(),
          project: getProject(),
        }
      })"
    >
      Copy
    </a>
    <a
      v-else
      class="button is-primary is-outlined"
      @click="$router.push({
        name: 'ReplicateContainer',
        params: {
          container: getContainer(),
          project: getProject(),
        }
      })"
    >
      Copy
    </a>
  </div>
</template>

<script>
export default {
  name: "ReplicateContainerButton",
  props: [
    "project",
    "container",
    "smallsize",
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
