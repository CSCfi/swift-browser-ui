<template>
  <li class="breadcrumb-element">
    <router-link
      class="breadcrumb-link"
      :to="address"
    >
      {{ alias }}
    </router-link>
  </li>
</template>

<script>
export default {
  name: "BreadcrumbListElement",
  props: ["address", "alias"],
};
</script>