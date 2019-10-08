<template>
  <div id="shared-tabs">
    <b-tabs
      type="is-toggle"
      v-model="activeTab"
      expanded
      style="width:90%;margin-left:5%;margin-right:5%;"
    >
      <b-tab-item :label="$t('message.share.to_me')">
        <SharedTable />
      </b-tab-item>
      <b-tab-item :label="$t('message.share.from_me')">
        <SharedOutTable />
      </b-tab-item>
    </b-tabs>
  </div>
</template>

<script>
// Import table for the containers shared to the querying user
import SharedTable from "@/components/SharedTable";
// Import table for the containers shared by the querying user
import SharedOutTable from "@/components/SharedOutTable";

export default {
  name: "Shared",
  components: {
    SharedTable,
    SharedOutTable,
  },
  data: function () {
    return {
      activeTab: 0,
    }
  }
}
</script>
