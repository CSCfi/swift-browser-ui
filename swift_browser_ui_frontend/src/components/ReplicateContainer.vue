<template>
  <div>
    <a
      v-if="smallsize"
      class="button is-primary is-outlined"
      size="is-small"
      @click="$router.push({
        name: 'ReplicateContainer',
        props: {
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
  beforeMount () {
    this.checkSize();
  },
  methods: {
    getProject: function () {
      if(this.$route.params.user == undefined) {
        return this.project ? this.project : this.$route.params.project;
      }
      return this.active.id;
    },
    getContainer: function () {
      return this.container ? this.container : this.$route.params.container;
    },
  },
};
</script>
