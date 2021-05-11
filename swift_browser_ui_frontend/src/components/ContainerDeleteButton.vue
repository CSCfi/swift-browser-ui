<template>
  <div class="contents">
    <b-button
      type="is-danger"
      icon="delete"
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
        title: this.$t("message.container_ops.deleteConfirm"),
        message: this.$t("message.container_ops.deleteConfirmMessage"),
        confirmText: this.$t("message.container_ops.deleteConfirm"),
        type: "is-danger",
        hasIcon: true,
        onConfirm: () => {this.deleteContainer();},
      });
    },
    deleteContainer: function () {
      this.$buefy.toast.open({
        message: this.$t("message.container_ops.deleteSuccess"),
        type: "is-success",
      });
      swiftDeleteContainer(this.container).then(() => {
        this.$store.commit("updateContainers");
      });
    },
  },
};
</script>
