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
    subfolders() {
      return this.$route.query.prefix ?
        this.$route.query.prefix.split("/") : [];
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
    deleteObjects: async function () {
      let to_remove = [];
      let segments_to_remove = []; // Array for segment objects to be deleted
      let segment_container = null;
      let selectedSubfolder = false;

      const isSegmentsContainer = this.container.endsWith("_segments");
      if (!isSegmentsContainer) {
        segment_container = await getDB().containers.get({
          projectID: this.projectID,
          name: `${this.selectedObjects[0].container}_segments`,
        });
      }

      for (let object of this.selectedObjects) {
        // Only files are able to delete
        //or when objects are shown as paths
        if (isFile(object.name, this.$route)
          || !this.renderedFolders) {
          to_remove.push(object.name);
          if (segment_container) {
            // Equivalent object from segment container needs to be deleted
            const segment_obj = await getDB().objects
              .where({containerID: segment_container.id})
              .filter(obj => obj.name.includes(`${object.name}/`)).first();
            segments_to_remove.push(segment_obj.name);
          }
        } else {
          //flag if user is trying to delete a subfolder
          //when folders rendered
          selectedSubfolder = true;
        }
      }

      if(this.$route.name !== "SharedObjects") {
        // Delete objects and segment objects from IDB
        const objIDs = this.selectedObjects.filter(
          obj => obj.name && to_remove.includes(obj.name)).reduce(
          (prev, obj) => [...prev, obj.id], [],
        );

        const segmentObjIDs = await getDB().objects
          .where({ containerID: segment_container.id })
          .filter(obj => obj.name && segments_to_remove.includes(obj.name))
          .primaryKeys();

        getDB().objects.bulkDelete(objIDs.concat(segmentObjIDs));
      }

      swiftDeleteObjects(
        this.$route.params.owner || this.projectID,
        this.container,
        to_remove,
      ).then(async () => {

        if (segments_to_remove.length > 0) {
          await swiftDeleteObjects(
            this.$route.params.owner || this.projectID,
            segment_container.name,
            segments_to_remove,
          );
        }

        if (this.$route.name === "SharedObjects") {
          await this.$store.dispatch(
            "updateSharedObjects",
            {
              project: this.projectID,
              owner: this.$route.params.owner,
              container: {
                name: this.container,
                id: 0,
              },
            },
          );
        }

        const dataTable = document.getElementById("objtable");
        dataTable.clearSelections();

        this.toggleDeleteModal();

        // Only files can be deleted
        // Show warnings when deleting subfolders
        if (to_remove.length > 0) {
          let msg;
          to_remove.length === 1?
            msg = to_remove.length + this.$t("message.objects.deleteOneSuccess")
            : msg = to_remove.length +
              this.$t("message.objects.deleteManySuccess");

          if (this.subfolders.length && this.renderedFolders) {
            //get all files uppermost subfolder contains
            const folderFiles = await getDB().objects
              .filter(obj => obj.name.startsWith(this.subfolders[0])
                && obj.container === this.container)
              .toArray();
            if (folderFiles.length < 1) {
              //if all subfolders empty, go to container
              //see if more than one subfolder removed
              this.subfolders.length > 1 ?
                msg = this.$t("message.subfolders.deleteManySuccess") :
                msg = this.$t("message.subfolders.deleteOneSuccess");
              this.$router.push({name: "ObjectsView"});
            }
            else {
              let newPrefix = this.prefix;
              for (let level=0; level < this.subfolders.length; level++) {
                let found = folderFiles.find(obj =>
                  obj.name.startsWith(newPrefix));
                if (found !== undefined) {
                  //if file with this prefix found
                  //go to containing subfolder
                  //files found at same level: leave "file(s) deleted" ^
                  //otherwise show "subfolder(s) deleted"
                  if (level > 0) {
                    level > 1 ?
                      msg = this.$t("message.subfolders.deleteManySuccess") :
                      msg = this.$t("message.subfolders.deleteOneSuccess");
                    let path =
                      {name: "ObjectsView", query: { prefix: newPrefix}};
                    this.$router.push(path);
                  }
                  break;
                } else {
                  //files with this prefix not found
                  //go up a subfolder and check again
                  newPrefix = newPrefix
                    .substring(0, newPrefix.lastIndexOf("/"));
                }
              }
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
