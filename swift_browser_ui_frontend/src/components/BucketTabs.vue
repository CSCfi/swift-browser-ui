<template>
  <c-tab-buttons
    :value="activeTab"
    :mandatory="true"
    data-testid="bucket-tabs"
    :aria-label="$t('label.bucket_tabs')"
  >
    <c-button
      v-for="tab in tabs"
      :key="tab.key"
      :data-testid="tab.route.name"
      class="tab-button"
      @click="navigate(tab.route.name)"
      @keyup.enter="navigate(tab.route.name)"
    >
      {{ $t(tab.key) }}
    </c-button>
  </c-tab-buttons>
</template>

<script>
export default {
  name: "BucketTabs",
  data: function() {
    return {
      tabs: [],
    };
  },
  computed: {
    project () {
      return this.$route.params.project;
    },
    user () {
      return this.$route.params.user;
    },
    name () {
      return this.$route.name;
    },
    activeTab () {
      const routes = this.tabs.flatMap(tab => tab.route.name);
      return routes.indexOf(this.name);
    },
  },
  created: function () {
    this.setTabs();
  },
  methods: {
    setTabs() {
      this.tabs = [
        {
          key: "message.bucketTabs.all",
          route: { name: "AllBuckets" },
        },
        {
          key: "message.bucketTabs.sharedFrom",
          route: { name: "SharedFrom" },
        },
        {
          key: "message.bucketTabs.sharedTo",
          route: { name: "SharedTo" },
        },
      ];
    },
    navigate(routeName) {
      if (this.name !== routeName) {
        return this.$router.push({name: routeName, params: {
          user: this.user,
          project: this.project,
        }});
      }
    },
  },
};
</script>


<style scoped>

c-tab-buttons {
  display: block;
  padding-top: 1rem;
}

.tab-button {
  flex-basis: 0;
}

</style>
