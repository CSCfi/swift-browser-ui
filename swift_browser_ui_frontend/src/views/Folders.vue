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

import { markRaw } from "vue";

export default {
  name: "FoldersView",
  components: { FolderTabs },

  // values in the 'data' property are reactive by default
  // but components shouldn't be reactive, so we use `markRaw`
  // https://vuejs.org/api/reactivity-advanced.html#markraw
  data: function() {
    return {
      activeRouteName: "",
      folderComponents: [
        {type: markRaw(AllFoldersTable), name: "AllFolders"},
        {type: markRaw(SharedTable), name: "SharedTo"},
        {type: markRaw(SharedOutTable), name: "SharedFrom"},
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
