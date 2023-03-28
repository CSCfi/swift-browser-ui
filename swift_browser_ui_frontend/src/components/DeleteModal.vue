<template>
  <c-card class="delete-modal">
    <c-alert type="error">
      <div slot="title">
        {{ title }}
      </div>

      {{ message }}

      <c-card-actions justify="end">
        <c-button
          outlined
          @click="toggleDeleteModal"
          @keyup.enter="toggleDeleteModal"
        >
          {{ $t("message.cancel") }}
        </c-button>
        <c-button
          @click="isObject ? deleteObjects() : deleteContainer()"
          @keyup.enter="isObject ? deleteObjects() : deleteContainer()"
        >
          {{ confirmText }}
        </c-button>
      </c-card-actions>
    </c-alert>
  </c-card>
</template>

<script>
import {
  swiftDeleteObjects,
  swiftDeleteContainer,
} from "@/common/api";
import { getDB } from "@/common/db";

export default {
  name: "DeleteModal",
  data: function () {
    return {
      isObject: false,
    };
  },
  computed: {
    title() {
      return this.isObject
        ? this.$t("message.objects.deleteObjects")
        : this.$t("message.container_ops.deleteConfirm");
    },
    message() {
      return this.isObject
        ? this.$t("message.objects.deleteObjectsMessage")
        : this.$t("message.container_ops.deleteConfirmMessage");
    },
    confirmText() {
      return this.isObject
        ? this.$t("message.objects.deleteConfirm")
        : this.$t("message.container_ops.deleteConfirm");
    },
    selectedObjects() {
      return this.$store.state.deletableObjects.length > 0
        ? this.$store.state.deletableObjects
        : [];
    },
    selectedFolderName() {
      return this.$store.state.selectedFolderName.length > 0
        ? this.$store.state.selectedFolderName
        : "";
    },
  },
  watch: {
    selectedObjects: function () {
      if (this.selectedObjects && this.selectedObjects.length > 0) {
        this.isObject = true;
      } else {
        this.isObject = false;
      }
    },
  },
  methods: {
    toggleDeleteModal: function() {
      this.$store.commit("toggleDeleteModal", false);
      this.$store.commit("setDeletableObjects", []);
      this.$store.commit("setFolderName", "");
    },
    deleteContainer: function() {
      document.querySelector("#container-toasts").addToast(
        { progress: false,
          type: "success",
          message: this.$t("message.container_ops.deleteSuccess")},
      );

      const projectID = this.$route.params.project;
      swiftDeleteContainer(
        projectID,
        this.selectedFolderName,
      ).then(async () => {
        await getDB().containers
          .where({
            projectID,
            name: this.selectedFolderName,
          })
          .delete();

        this.toggleDeleteModal();
      });
    },
    deleteObjects: function () {
      document.querySelector("#objects-toasts").addToast(
        { progress: false,
          type: "success",
          message: this.$t("message.objects.deleteSuccess")},
      );

      let to_remove = new Array;
      for (let object of this.selectedObjects) {
        to_remove.push(object.name);
      }
      if(this.$route.name !== "SharedObjects") {
        const objIDs = this.selectedObjects.reduce(
          (prev, obj) => [...prev, obj.id], [],
        );
        getDB().objects.bulkDelete(objIDs);
      }
      swiftDeleteObjects(
        this.$route.params.owner || this.$route.params.project,
        this.$route.params.container,
        to_remove,
      ).then(async () => {
        if (this.$route.name === "SharedObjects") {
          await this.$store.dispatch(
            "updateSharedObjects",
            {
              project: this.$route.params.project,
              owner: this.$route.params.owner,
              container: {
                name: this.$route.params.container,
                id: 0,
              },
            },
          );
        }

        this.toggleDeleteModal();
      });
    },
  },
};
</script>

<style scoped lang="scss">
@import "@/css/prod.scss";

.mdi-alert-circle {
  font-size: 2.0em;
  color: $csc-red;
}

.delete-modal {
  padding: 0px;
}
</style>
