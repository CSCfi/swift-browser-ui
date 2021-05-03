<template>
  <div class="contents">
    <b-button
      type="is-primary"
      outlined
      size="is-small"
      :inverted="inverted"
      :disabled="disabled"
      @click="confirmDelete ()"
    >
      {{ $t('message.delete') }}
    </b-button>
  </div>
</template>

<script>
import {swiftDeleteContainer} from "@/common/api";

export default {
  name: "DeleteContainerButton",
  props: [
    "container",
    "disabled",
    "inverted",
  ],
  methods: {
    confirmDelete: function () {
      this.$buefy.dialog.confirm({
        title: "Delete Container",
        message: "Are you sure you want do delete this container?",
        confirmText: "Delete Container",
        type: "is-danger",
        hasIcon: true,
        onConfirm: () => {this.deleteContainer();},
      });
    },
    deleteContainer: function () {
      this.$buefy.toast.open( "Container deleted");
      swiftDeleteContainer(this.container).then(() => {
        this.$store.commit("updateContainers");
      });
    },
  },
};
</script>
