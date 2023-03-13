Inspired by https://github.com/buefy/buefy/blob/3b3ae60e448ddfd669f20570d40812fd1e041473/src/components/upload/Upload.vue

<template>
  <div class="upload-btn-wrapper">
    <c-button 
      @click="$refs.input.click()"
      @keyup.enter="$refs.input.click()"
    >
      <slot />
    </c-button>
    <input
      ref="input"
      type="file"
      v-bind="$attrs"
      multiple 
      @change="onFileChange"
    >
  </div>
</template>

<script>
export default {
  name: "CUploadButton",
  inheritAttrs: false,
  props: {
    value: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      newValue: this.value,
    };
  },
  watch: {
    value(value) {
      this.newValue = value;
      if (!value || (Array.isArray(value) && value.length === 0)) {
        this.$refs.input.value = null;
      }
    },
  },
  methods: {
    onFileChange(event) {
      const value = event.target.files || event.dataTransfer.files;
      if (value.length === 0) {
        if (!this.newValue) return;
      } else {
        let newValues = false;
        for (let i = 0; i < value.length; i++) {
          const file = value[i];
          this.newValue.push(file);
          newValues = true;
        }
        if (!newValues) return;
      }
      this.$emit("input", this.newValue);
    },
  },
};
</script>

<style>

input {
  display: none;
}

</style>