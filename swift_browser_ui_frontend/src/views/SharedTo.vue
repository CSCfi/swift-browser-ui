<template>
  <section>
    <div class="sharing-view">
      <SharedMenu />
      <SharedTable />
    </div>
  </section>
</template>

<style scoped>
.sharing-view {
  display: flex;
  width: 90%;
}
#ShareMenu {
  flex: 1 1 auto;
}
#SharedTable {
  flex: 4 1 auto;
}
</style>

<script>
import ShareMenu from "@/components/SharedMenu";
import SharedTable from "@/components/SharedTable";

export default {
  name: "SharedTo",
  components: {
    ShareMenu,
    SharedTable,
  },
  data () {
    return {};
  },
};
</script>
