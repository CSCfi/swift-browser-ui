<template>
  <c-toolbar class="relative">
    <c-link
      :href="user ? '/browse' : '/'"
      target="_self"
      color="dark-grey"
      weight="400"
    >
      <c-csc-logo />
      <span>{{ $t('message.program_name') }} </span>
    </c-link>
    <c-spacer />
    <LanguageSelector />
  </c-toolbar>
</template>

<script>
import LanguageSelector from "@/components/CLanguageSelector.vue";
export default {
  components:{
    LanguageSelector,
  },
  props: ["user"],
};
</script>

<style lang="scss" scoped>
c-toolbar span {
  display: inline-flex;
  align-items: center;
  margin-left: 1rem;
}
</style>
