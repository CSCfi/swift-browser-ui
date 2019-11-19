<template>
  <section>
    <SharedMenu />
    <RequestSharing />
    <ShareRequestsTable />
  </section>
</template>

<script>
import SharedMenu from "@/components/SharedMenu";
import ShareRequestsTable from "@/components/ShareRequestsTable";
import RequestSharing from "@/components/RequestSharing";

export default {
  name: "ShareRequests",
  components: {
    SharedMenu,
    ShareRequestsTable,
    RequestSharing,
  },
  data () {
    return {};
  },
};
</script>
