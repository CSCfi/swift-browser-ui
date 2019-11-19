<template>
  <section>
    <SharedMenu />
    <SharedOutTable />
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
