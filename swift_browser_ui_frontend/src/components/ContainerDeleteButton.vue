<template>
  <div class="contents">
    <b-button
      type="is-danger"
      icon-left="delete"
      outlined
      size="is-small"
      :inverted="inverted"
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
    "inverted",
    "objects",
  ],
  methods: {
    confirmDelete: function () {
      if (this.$props.objects > 0) {
        this.$buefy.notification.open({
          message: "Deleting a container requires deleting all objects first.",
          type: "is-danger",
          position: "is-top-right",
          hasIcon: true,
        });
        this.$router.push(
          this.$route.params.project
            + "/"
            + this.$props.container,
        );
      } else {
        this.$buefy.dialog.confirm({
          title: this.$t("message.container_ops.deleteConfirm"),
          message: this.$t("message.container_ops.deleteConfirmMessage"),
          confirmText: this.$t("message.container_ops.deleteConfirm"),
          type: "is-danger",
          hasIcon: true,
          onConfirm: () => {this.deleteContainer();},
        });
      }
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
