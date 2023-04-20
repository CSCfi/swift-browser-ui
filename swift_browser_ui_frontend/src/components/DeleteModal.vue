<template>
  <c-card class="delete-modal">
    <c-alert type="error">
      <div slot="title">
        {{ $t("message.objects.deleteObjects") }}
      </div>

      {{ $t("message.objects.deleteObjectsMessage") }}

      <c-card-actions justify="end">
        <c-button
          outlined
          @click="toggleDeleteModal"
          @keyup.enter="toggleDeleteModal"
        >
          {{ $t("message.cancel") }}
        </c-button>
        <c-button
          @click="deleteObjects()"
          @keyup.enter="deleteObjects()"
        >
          {{ $t("message.objects.deleteConfirm") }}
        </c-button>
      </c-card-actions>
    </c-alert>
  </c-card>
</template>

<script>
import { swiftDeleteObjects } from "@/common/api";
import { getDB } from "@/common/db";

import { isFile } from "@/common/globalFunctions";

export default {
  name: "DeleteModal",
  computed: {
    selectedObjects() {
      return this.$store.state.deletableObjects.length > 0
        ? this.$store.state.deletableObjects
        : [];
    },
    multipleSubfolders() {
      return this.$route.query.prefix.includes("/");
    },
    prefix() {
      return this.$route.query.prefix;
    },
    container() {
      return this.$route.params.container;
    },
    renderedFolders() {
      return this.$store.state.renderedFolders;
    },
  },
  methods: {
    toggleDeleteModal: function() {
      this.$store.commit("toggleDeleteModal", false);
      this.$store.commit("setDeletableObjects", []);
    },
    goToParent: function() {
      let path;
      if (this.multipleSubfolders) { //parent is subfolder -> go up
        path = {name: "ObjectsView", query:
          { prefix: this.prefix.slice(0, this.prefix.lastIndexOf("/"))}};
      } else { //parent is container
        path = {name: "ObjectsView"}; //go to container
      }
      this.$router.push(path);
    },
    deleteObjects: function () {
      let to_remove = new Array;
      let selectedSubfolder = false;
      for (let object of this.selectedObjects) {
        // Only files are able to delete
        //or when objects are shown as paths
        if (isFile(object.name, this.$route)
          || !this.renderedFolders) {
          to_remove.push(object.name);
        } else {
          //flag if user is trying to delete a subfolder
          //when folders rendered
          selectedSubfolder = true;
        }
      }

      if(this.$route.name !== "SharedObjects") {
        const objIDs = this.selectedObjects.filter(
          obj => obj.name && to_remove.includes(obj.name)).reduce(
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
        const dataTable = document.getElementById("objtable");
        dataTable.clearSelections();

        // Only files can be deleted
        // Show warnings when deleting subfolders
        if (to_remove.length > 0) {
          let msg;
          to_remove.length === 1?
            msg = to_remove.length + this.$t("message.objects.deleteOneSuccess")
            : msg = to_remove.length +
              this.$t("message.objects.deleteManySuccess");

          if (this.prefix && this.renderedFolders) {
            //if there are no files with same prefix in same container:
            //subfolder is empty
            const samePrefixFiles = await getDB().objects
              .filter(obj => obj.name.startsWith(this.prefix)
                && obj.container === this.container)
              .toArray();
            if (samePrefixFiles.length < 1) {
              msg = this.$t("message.subfolders.deleteSuccess");
              this.goToParent();
            }
          }
          document.querySelector("#objects-toasts").addToast(
            { progress: false,
              type: "success",
              message: msg },
          );
        }
        if (selectedSubfolder) {
          //if selected files include subfolders
          document.querySelector("#objects-toasts").addToast(
            {
              progress: false,
              type: "error",
              message: this.$t("message.subfolders.deleteNote"),
            },
          );
        }
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
