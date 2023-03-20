<template>
  <div
    class="tags-list"
    :aria-label="$t(ariaLabel)"
  >
    <c-tag
      v-for="tag in tags"
      :key="tag"
      active
    >
      <span>{{ tag }}</span>
      <c-icon
        :path="mdiClose"
        :alt="$t('label.delete_tag')"
        color="white"
        size="16"
        @click="$emit('deleteTag', $event, tag)"
      />
    </c-tag>
    <input
      type="text"
      :aria-label="$t('label.edit_tag')"
      :placeholder="$t(placeholder)"
      @blur="$emit('addTag', $event, true)"
      @keydown="$emit('addTag', $event)"
    >
  </div>
</template>

<script>
import { mdiClose } from "@mdi/js";

export default {
  name: "TagInput",
  props: {
    tags: {
      type: Array,
      default: () => [],
    },
    ariaLabel: {
      type: String,
      default: "label.tagsList",
    },
    placeholder: {
      type: String,
      default: "message.tagPlaceholder",
    },
  },
  data() {
    return {
      mdiClose,
    };
  },
};
</script>

<style scoped lang="scss">
@import "@/css/prod.scss";

.tags-list {
  min-height: 3rem;
  background: transparent;
  border: 1px solid $csc-dark-grey;
  margin: 1rem 0;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}

.tags-list:focus-within {
  border: 2px solid $csc-primary;
}

.tags-list input {
  background: transparent;
  border: none;
  outline: none;
  flex: 1;
}

span {
  display: inline-block;
  max-width: 10rem;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>