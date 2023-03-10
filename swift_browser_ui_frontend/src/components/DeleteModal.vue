<template>
  <c-card class="delete-modal">
    <c-card-title>{{ title }}</c-card-title>

    <c-card-content>
      <c-row gap="10px" align="center">
        <i class="mdi mdi-alert-circle"></i>
        {{ message }}
      </c-row>
    </c-card-content>

    <c-card-actions justify="end">
      <c-button 
        @click="toggleDeleteModal"
        @keyup.enter="toggleDeleteModal"
        outlined
      >
        Cancel</c-button>
      <c-button 
        @click="isObject ? deleteObjects() : deleteContainer()"
        @keyup.enter="isObject ? deleteObjects() : deleteContainer()"
      >
        {{ confirmText }}
      </c-button>
    </c-card-actions>
  </c-card>
</template>

<script>
import { 
  swiftDeleteObjects,
  swiftDeleteContainer,
} from "@/common/api";

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
      this.$buefy.toast.open({
        message: this.$t("message.container_ops.deleteSuccess"),
        type: "is-success",
      });

      const projectID = this.$route.params.project;
      swiftDeleteContainer(
        projectID,
        this.selectedFolderName,
      ).then(async () => {
        await this.$store.state.db.containers
          .where({
            projectID,
            name: this.selectedFolderName,
          })
          .delete();

        this.toggleDeleteModal();
      });
    },
    deleteObjects: function () {
      this.$buefy.toast.open({
        message: this.$t("message.objects.deleteSuccess"),
        type: "is-success",
      });

      let to_remove = new Array;
      for (let object of this.selectedObjects) {
        to_remove.push(object.name);
      }
      if(this.$route.name !== "SharedObjects") {
        const objIDs = this.selectedObjects.reduce(
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
  position: absolute;
  left: 0;
  right: 0;
}
</style>