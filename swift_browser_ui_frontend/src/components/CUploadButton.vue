Inspired by https://github.com/buefy/buefy/blob/3b3ae60e448ddfd669f20570d40812fd1e041473/src/components/upload/Upload.vue

<template>
  <div class="upload-btn-wrapper">
    <c-button
      @click="click"
      @keyup.enter="click"
    >
      <slot />
    </c-button>
    <input
      ref="input"
      :value="modelValue"
      type="file"
      multiple
      @input="$emit('update:modelValue', $event.target.files)"
      @cancel="$emit('cancel')"
    >
  </div>
</template>

<script>
export default {
  name: "CUploadButton",
  inheritAttrs: false,
  props: {
    modelValue: {
      type: Array,
      default: () => [],
    },
  },
  emits: ["update:modelValue", "add-files", "cancel"],
  methods: {
    click() {
      this.$refs.input.click();
      this.$emit("add-files");
    },
  },
};
</script>

<style scoped>

input {
  display: none;
}

</style>
