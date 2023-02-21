<template>
  <div class="contents container-box">
    <ObjectTable />
  </div>
</template>

<script>
import ObjectTable from "@/components/ObjectTable.vue";

export default {
  name: "SharedObjects",
  components: { ObjectTable },
};
</script>
