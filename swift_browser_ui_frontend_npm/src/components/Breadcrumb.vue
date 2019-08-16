<template>

<li class="breadcrumb-element">
  <router-link class="breadcrumb-link" v-bind:to="address">
    {{ alias }}
  </router-link>
</li>

</template>

<script>
export default {
  props: ["address", "alias"]
}
</script>