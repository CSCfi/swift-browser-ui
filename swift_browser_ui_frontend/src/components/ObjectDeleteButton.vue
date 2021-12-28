<template>
  <div class="contents">
    <b-button
      type="is-danger"
      icon-left="delete"
      outlined
      :size="size"
      :inverted="inverted"
      :disabled="disabled"
      @click="confirmDelete ()"
    >
      {{ $t('message.delete') }}
    </b-button>
  </div>
</template>

<script>
import {swiftDeleteObjects} from "@/common/api";

export default {
  name: "DeleteObjectsButton",
  props: [
    "disabled",
    "inverted",
    "size",
    "objects",
  ],
  methods: {
    confirmDelete: function () {
      this.$buefy.dialog.confirm({
        title: this.$t("message.objects.deleteObjects"),
        message: this.$t("message.objects.deleteObjectsMessage"),
        confirmText: this.$t("message.objects.deleteConfirm"),
        type: "is-danger",
        hasIcon: true,
        onConfirm: () => {this.deleteObjects();},
      });
    },
    deleteObjects: function () {
      this.$buefy.toast.open({
        message: this.$t("message.objects.deleteSuccess"),
        type: "is-success",
      });
      let to_remove = new Array;
      if (typeof(this.$props.objects) == "string") {
        to_remove.push(this.$props.objects);
      } else {
        for (let object of this.$props.objects) {
          to_remove.push(object.name);
        }
      }
      swiftDeleteObjects(
        this.$route.params.container,
        to_remove,
      ).then(() => {
        this.$store.dispatch("updateObjects", {route: this.$route});
      });
    },
  },
};
</script>
