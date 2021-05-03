<template>
  <div class="contents">
    <b-button
      type="is-primary"
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
        title: "Delete Object / Objects",
        message: "Are you sure you want do delete these objects?",
        confirmText: "Delete Objects",
        type: "is-danger",
        hasIcon: true,
        onConfirm: () => {this.deleteObjects();},
      });
    },
    deleteObjects: function () {
      this.$buefy.toast.open("Objects deleted");
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
        this.$store.commit({
          type: "updateObjects",
          route: this.$route,
        });
      });
    },
  },
};
</script>
