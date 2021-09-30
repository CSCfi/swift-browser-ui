<template>
  <li class="breadcrumb-element">
    <router-link
      class="breadcrumb-link"
      :to="address"
    >
      {{ alias | truncate(100) }}
    </router-link>
  </li>
</template>

<script>
export default {
  name: "BreadcrumbListElement",
  filters: {
    truncate(value, length) {
      return value.length > length ? value.substr(0, length) + "..." : value;
    },
  },
  props: ["address", "alias"],
};
</script>
