<template>
  <div class="contents">
    <div class="sharing-view">
      <SharedMenu />
      <SharedTable />
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
#SharedTable {
  flex: 4 1 auto;
}
</style>

<script>
import SharedMenu from "@/components/SharedMenu";
import SharedTable from "@/components/SharedTable";

export default {
  name: "SharedTo",
  components: {
    SharedMenu,
    SharedTable,
  },
  data () {
    return {};
  },
};
</script>
