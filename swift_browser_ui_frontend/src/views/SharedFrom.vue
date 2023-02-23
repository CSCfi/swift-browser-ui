<template>
  <section class="contents">
    <div class="sharing-view columns">
      <SharedMenu
        class="column is-one-fifth"
      />
      <SharedOutTable />
    </div>
  </section>
</template>

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

<style scoped>
.sharing-view {
  display: flex;
  padding-left: 5%;
  padding-right: 5%;
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
