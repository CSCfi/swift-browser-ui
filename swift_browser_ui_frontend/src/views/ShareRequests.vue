<template>
  <section>
    <div class="sharing-view">
      <SharedMenu />
      <div class="requestview">
        <RequestSharing />
        <ShareRequestsTable />
      </div>
    </div>
  </section>
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
.requestview {
  flex: 4 1 auto;
}
</style>

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
