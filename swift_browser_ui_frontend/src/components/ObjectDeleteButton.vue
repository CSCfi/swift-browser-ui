<template>
  <div class="contents">
    <c-button
      text
      size="small"
      title="Delete"
      @click="confirmDelete ()"
      @keyup.enter="confirmDelete ()"
    >
      {{ $t('message.delete') }}
    </c-button>
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
      //removed toast for page that will be deleted
      let to_remove = new Array;
      if (typeof(this.$props.objects) == "string") {
        to_remove.push(this.$props.objects);
      } else {
        for (let object of this.$props.objects) {
          to_remove.push(object.name);
        }
      }
      if(this.$route.name !== "SharedObjects") {
        const objIDs = this.$props.objects.reduce(
          (prev, obj) => [...prev, obj.id], [],
        );
        this.$store.state.db.objects.bulkDelete(objIDs);
      }
      swiftDeleteObjects(
        this.$route.params.project,
        this.$route.params.container,
        to_remove,
      ).then(async () => {
        if (this.$route.name === "SharedObjects") {
          await this.$store.dispatch(
            "updateSharedObjects",
            {
              project: this.$route.params.project,
              container: {
                name: this.$route.params.container,
                id: 0,
              },
            },
          );
        }
      });
    },
  },
};
</script>
