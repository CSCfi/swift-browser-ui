<template>
  <div class="contents">
    <div class="sharing-view">
      <SharedMenu />
      <SharedOutTable />
    </div>
  </div>
</template>

<style scoped>
.sharing-view {
  display: flex;
  padding-left: 3%;
  padding-right: 3%;
  width: auto;
}
#SharedMenu {
  flex: 1 1 auto;
  padding-right: 1%
}
#SharedOutTable {
  flex: 4 1 auto;
}
</style>

<script>
import SharedMenu from "@/components/SharedMenu";
import SharedOutTable from "@/components/SharedOutTable";

export default {
  name: "SharedFrom",
  components: {
    SharedOutTable,
    SharedMenu,
  },
  data () {
    return {};
  },
};
</script>
