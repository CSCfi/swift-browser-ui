<template>
  <div id="shared-out-table">
    <b-field
      grouped
      group-multiline
    >
      <b-select
        v-model="perPage"
      >
        <option value="5">
          5 {{ $t('message.table.pageNb') }}
        </option>
        <option value="10">
          10 {{ $t('message.table.pageNb') }}
        </option>
        <option value="15">
          15 {{ $t('message.table.pageNb') }}
        </option>
        <option value="25">
          25 {{ $t('message.table.pageNb') }}
        </option>
        <option value="50">
          50 {{ $t('message.table.pageNb') }}
        </option>
        <option value="100">
          100 {{ $t('message.table.pageNb') }}
        </option>
      </b-select>
    </b-field>
  </div>
</template>

<script>
export default {
  data: function () {
    return {
      sharedList: [],
      selected: undefined,
      perPage: 15,
      defaultSortDirection: "asc",
      currentPage: 1,
    }
  },
}
</script>
