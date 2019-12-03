<template>
  <section>
    <div class="sharing-view">
      <SharedMenu />
      <SharedOutTable />
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
