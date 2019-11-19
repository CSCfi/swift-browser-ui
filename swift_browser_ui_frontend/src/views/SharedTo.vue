<template>
  <section>
    <ShareMenu />
    <SharedTable />
  </section>
</template>

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
