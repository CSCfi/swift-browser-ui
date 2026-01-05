<template>
  <c-card
    ref="deleteObjsModal"
    class="delete-modal"
    @keydown="handleKeyDown"
  >
    <c-card
      ref="deleteObjsModal"
      class="delete-modal"
      @keydown="handleKeyDown"
    >
      <c-alert
        v-if="!isDeleting"
        type="error"
      >
        <div slot="title">
          {{ $t("message.objects.deleteObjects") }}
        </div>

        {{ owner ?
          $t("message.objects.deleteSharedObjects") :
          $t("message.objects.deleteObjectsMessage")
        }}

        <c-card-actions justify="end">
          <c-button
            outlined
            @click="toggleDeleteModal(false)"
            @keyup.enter="toggleDeleteModal(true)"
          >
            {{ $t("message.cancel") }}
          </c-button>
          <c-button
            id="delete-objs-btn"
            data-testid="confirm-delete-objects"
            @click="deleteObjects()"
            @keyup.enter="deleteObjects()"
          >
            {{ $t("message.objects.deleteConfirm") }}
          </c-button>
        </c-card-actions>
      </c-alert>
      <c-alert
        v-else
        type="success"
      >
        <div slot="title">
          {{ $t("message.objects.deleteInProgress") }}
        </div>
        <c-progress-bar
          single-line
          indeterminate
        />
      </c-alert>
    </c-card>
  </c-card>
</template>

<script>
import { getDB } from "@/common/db";
import { isFile } from "@/common/globalFunctions";
import {
  getFocusableElements,
  addFocusClass,
  removeFocusClass,
  moveFocusOutOfModal,
} from "@/common/keyboardNavigation";
import { awsDeleteObject, awsListObjects } from "@/common/s3commands";

export default {
  name: "DeleteModal",
  data() {
    return {
      isDeleting: false,
      bucketObjects: [],
    };
  },
  computed: {
    selectedObjects() {
      return this.$store.state.deletableObjects.length > 0
        ? this.$store.state.deletableObjects
        : [];
    },
    folders() {
      return this.$route.query.prefix ?
        this.$route.query.prefix.split("/") : [];
    },
    prefix() {
      return this.$route.query.prefix;
    },
    projectID() {
      return this.$route.params.project;
    },
    container() {
      return this.$route.params.container;
    },
    owner() {
      return this.$route.params.owner;
    },
    renderedFolders() {
      return this.$store.state.renderedFolders;
    },
    modalVisible() {
      return this.$store.state.openDeleteModal;
    },
  },
  watch: {
    async modalVisible() {
      if (this.modalVisible) {
        this.isDeleting = false;
        // Object listing needed for correct behaviour after deletion
        this.bucketObjects = await awsListObjects(this.container);
      }
    },
  },
  methods: {
    toggleDeleteModal: function(keypress) {
      this.$store.commit("toggleDeleteModal", false);
      this.$store.commit("setDeletableObjects", []);

      /*
        Prev Active element is a popup menu and it is removed from DOM
        when we click it to open Delete Modal.
        Therefore, we need to make its focusable parent
        to be focused instead after we close the modal.
      */
      if (keypress) {
        const prevActiveElParent = document.getElementById("obj-table");
        moveFocusOutOfModal(prevActiveElParent, true);
      }
    },
    deleteObjects: async function () {
      let switchAlertType = false;
      setTimeout(() => {
        // to avoid alert flashing
        // switch type only if mid-deletion after 250ms
        switchAlertType = true;
      }, 250);
      let to_remove = [];
      let segments_to_remove = []; // Array for segment objects to be deleted
      let segment_container = null;
      let selectedFolder = false;

      const isSegmentsContainer = this.container.endsWith("_segments");

      if (!isSegmentsContainer) {
        segment_container = await getDB().containers.get({
          projectID: this.projectID,
          name: `${this.selectedObjects[0].container}_segments`,
        });
      }

      for (let object of this.selectedObjects) {
        if (switchAlertType && !this.isDeleting) {
          this.isDeleting = true;
        }
        // Only files are able to delete
        //or when objects are shown as paths
        if (isFile(object.name, this.$route)
          || !this.renderedFolders) {
          to_remove.push(object.name);

          if (segment_container) {
            // Equivalent object from segment container needs to be deleted
            // We can filter the deleted segments objects by prefix
            let segments = await awsListObjects(
              segment_container.name,
              object.name,
            );
            segments.map(segment => {segments_to_remove.push(segment.name);});
          }
        } else {
          //flag if user is trying to delete a folder
          //when folders rendered
          selectedFolder = true;
        }
      }

      if (to_remove.length) {
        this.$store.commit("setDeleting", true);
        try {
          for(const obj of to_remove) {
            await awsDeleteObject(this.container, obj);
          }
          for(const obj of segments_to_remove) {
            await awsDeleteObject(segment_container.name, obj);
          }
          this.bucketObjects = this.bucketObjects.filter(item => !to_remove.includes(item.name));
        } finally {
          this.$store.commit("setDeleting", false);
        }
      }

      const dataTable = document.getElementById("obj-table");
      dataTable.clearSelections();

      this.toggleDeleteModal();

      this.getDeleteMessage(to_remove, selectedFolder);
    },
    getDeleteMessage: async function(to_remove, selectedFolder) {
      // Only files can be deleted
      // Show warnings when deleting folders
      if (to_remove.length > 0) {
        let msg;
        to_remove.length === 1?
          msg = to_remove.length + this.$t("message.objects.deleteOneSuccess")
          : msg = to_remove.length +
            this.$t("message.objects.deleteManySuccess");

        if (this.folders.length && this.renderedFolders) {
          const folderExists = this.bucketObjects
            .find(obj => obj.name.startsWith(this.folders[0]));
          if (!folderExists) {
            //if all folders empty, go to bucket
            //see if more than one folder removed
            this.folders.length > 1 ?
              msg = this.$t("message.folders.deleteManySuccess") :
              msg = this.$t("message.folders.deleteOneSuccess");
            this.$router.push({name: "ObjectsView"});
          }
          else {
            let newPrefix = this.prefix;
            for (let level=0; level < this.folders.length; level++) {
              let found = this.bucketObjects.find(obj =>
                obj.name.startsWith(newPrefix));
              if (found !== undefined) {
                //if file with this prefix found
                //go to containing folder
                //files found at same level: leave "file(s) deleted" ^
                //otherwise show "folder(s) deleted"
                if (level > 0) {
                  level > 1 ?
                    msg = this.$t("message.folders.deleteManySuccess") :
                    msg = this.$t("message.folders.deleteOneSuccess");
                  let path =
                    {name: "ObjectsView", query: { prefix: newPrefix}};
                  this.$router.push(path);
                }
                break;
              } else {
                //files with this prefix not found
                //go up a folder and check again
                newPrefix = newPrefix
                  .substring(0, newPrefix.lastIndexOf("/"));
              }
            }
          }
        }
        document.querySelector("#objects-toasts").addToast(
          { progress: false,
            type: "success",
            message: msg,
          },
        );
      }
      if (selectedFolder) {
        //if selected files include folders
        document.querySelector("#objects-toasts").addToast(
          {
            progress: false,
            type: "error",
            message: this.$t("message.folders.deleteNote"),
          },
        );
      }
    },
    handleKeyDown: function (e) {
      const focusableList = this.$refs.deleteObjsModal.querySelectorAll(
        "c-button",
      );
      const { first, last } = getFocusableElements(focusableList);

      if (e.key === "Tab" && !e.shiftKey) {
        if (e.target === last) {
          removeFocusClass(last);
          first.tabIndex="0";
          first.focus();
          addFocusClass(first);
        } else if (e.target === first) {
          removeFocusClass(first);
          last.tabIndex="0";
          last.focus();
          addFocusClass(last);
        }
      }
      else if (e.key === "Tab" && e.shiftKey) {
        if (e.target === first) {
          e.preventDefault();
          last.tabIndex = "0";
          last.focus();
          if (last === document.activeElement) {
            addFocusClass(last);
          }
        } else if (e.target === last) {
          removeFocusClass(last);
        }
      }
    },
  },
};
</script>

<style scoped>

.delete-modal {
  padding: 0px;
}

c-progress-bar {
  padding: 0.5rem;
}

</style>
