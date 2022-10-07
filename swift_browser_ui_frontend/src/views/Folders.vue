<template>
  <c-flex class="container-box">
    <FolderTabs />
    <div
      v-for="component of folderComponents"
      :key="component.name"
    >
      <component
        :is="component.type"
        v-if="activeRouteName === component.name"
      />
    </div>
  </c-flex>
</template>

<script>
import FolderTabs from "@/components/FolderTabs.vue";
import ContainersView from "@/views/Containers.vue";
import SharedOutTable from "@/components/SharedOutTable.vue";
import SharedTable from "@/components/SharedTable.vue";

export default {
  name: "FoldersView",
  components: {
    FolderTabs,
    ContainersView,
  },
  data: function() {
    return {
      activeRouteName: "",
      folderComponents: [
        {type: ContainersView, name: "AllFolders"},
        {type: SharedOutTable, name: "SharedFrom"},
        {type: SharedTable, name: "SharedTo"},
      ],
    };
  }, 
  computed: {
    name () {
      return this.$route.name;
    },
  },
  watch: {
    "$route.name": function (name) {
      this.activeRouteName = name;
    },
  },
  created() {
    this.activeRouteName = this.name;
  },
};
</script>
