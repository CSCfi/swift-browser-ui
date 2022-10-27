<template>
  <div v-if="disabled">
    <b-button
      v-if="smallsize"
      type="is-primary"
      size="is-small"
      outlined
      disabled
      :inverted="inverted"
      icon-left="content-copy"
    >
      {{ $t('message.copy') }}
    </b-button>
    <b-button
      v-else
      type="is-primary"
      outlined
      :inverted="inverted"
      disabled
      icon-left="content-copy"
    >
      {{ $t('message.copy') }}
    </b-button>
  </div>
  <div v-else>
    <b-button
      v-if="smallsize"
      type="is-primary"
      size="is-small"
      outlined
      :inverted="inverted"
      icon-left="content-copy"
      @click="toggleCopyFolderModal(container, from)"
    >
      {{ $t('message.copy') }}
    </b-button>
    <b-button
      v-else
      type="is-primary"
      outlined
      :inverted="inverted"
      icon-left="content-copy"
      @click="toggleCopyFolderModal(container, from)"
    >
      {{ $t('message.copy') }}
    </b-button>
  </div>
</template>

<script>
import { toggleCopyFolderModal } from "@/common/globalFunctions";

export default {
  name: "ReplicateContainerButton",
  props: [
    "container",
    "smallsize",
    "inverted",
    "disabled",
    "from",
  ],
  data: function () {
    return {
      toggleCopyFolderModal,
    };
  },
};
</script>
