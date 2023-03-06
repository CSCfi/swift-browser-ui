<template>
  <c-flex
    class="container-box"
    role="region"
  >
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
import AllFoldersTable from "@/components/AllFoldersTable.vue";
import SharedOutTable from "@/components/SharedOutTable.vue";
import SharedTable from "@/components/SharedTable.vue";

export default {
  name: "FoldersView",
  components: { FolderTabs },
  data: function() {
    return {
      activeRouteName: "",
      folderComponents: [
        {type: AllFoldersTable, name: "AllFolders"},
        {type: SharedTable, name: "SharedTo"},
        {type: SharedOutTable, name: "SharedFrom"},
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
