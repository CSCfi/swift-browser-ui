<template>
  <c-tab-buttons
    :value="activeTab"
    :mandatory="true"
    data-testid="folder-tabs"
  >
    <c-button
      v-for="tab in tabs"
      :key="tab.label"
      @click="navigate(tab.route.name)"
    >
      {{ tab.label }}
    </c-button>
  </c-tab-buttons>
</template>

<script>
export default {
  name: "FolderTabs",
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
          label: this.$t("message.folderTabs.all"),
          route: { name: "AllFolders" },
        },
        {
          label: this.$t("message.folderTabs.sharedFrom"),
          route: { name: "SharedTo" },
        },
        {
          label: this.$t("message.folderTabs.sharedTo"), 
          route: { name: "SharedFrom" },
        },
      ];
    },
    navigate(routeName) {
      if (this.name !== routeName) {
        return this.$router.push({name: routeName ,params: {
          user: this.user,
          project: this.project,
        }});
      }
    },
  },
};
</script>


<style scroped>
c-tab-buttons {
  display: block;
  padding-bottom: 2rem;
}
</style>
