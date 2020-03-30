<template>
  <div>
    <a
      v-if="smallSize"
      class="is-primary is-outlined"
      size="is-small"
      @click="$router.push({
        name: 'ReplicateContainer',
        query: {
          container: getContainer(),
          project: getProject(),
        }
      })"
    >
      Copy
    </a>
    <a
      v-else
      class="is-primary is-outlined"
      @click="$router.push({
        name: 'ReplicateContainer',
        query: {
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
    "smallSize",
  ],
  beforeMount () {
    this.checkSize();
  },
  methods: {
    getProject: function () {
      return this.project ? this.project : this.$route.params.project;
    },
    getContainer: function () {
      return this.container ? this.container : this.$route.params.container;
    },
  },
};
</script>
