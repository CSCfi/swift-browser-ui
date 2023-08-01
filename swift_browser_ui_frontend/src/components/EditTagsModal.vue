<template>
  <c-card
    ref="editTagsContainer"
    class="edit-tags"
    @keydown="handleKeyDown"
  >
    <h2 class="title is-4 has-text-dark">
      {{ $t('message.editTags') }}
    </h2>
    <c-card-content>
      <TagInput
        :tags="tags"
        @addTag="addingTag"
        @deleteTag="deletingTag"
      />
    </c-card-content>
    <c-card-actions justify="space-between">
      <c-button
        outlined
        size="large"
        @click="toggleEditTagsModal"
        @keyup.enter="toggleEditTagsModal"
      >
        {{ $t("message.cancel") }}
      </c-button>
      <c-button
        size="large"
        @click="isObject ? saveObjectTags() : saveContainerTags()"
        @keyup.enter="isObject ? saveObjectTags() : saveContainerTags()"
      >
        {{ $t("message.save") }}
      </c-button>
    </c-card-actions>
  </c-card>
</template>

<script>
import {
  updateObjectMeta,
  updateContainerMeta,
} from "@/common/api";

import {
  getTagsForObjects,
  getTagsForContainer,
} from "@/common/conv";
import { getDB } from "@/common/db";

import {
  addNewTag,
  deleteTag,
  getCurrentISOtime,
  getFocusableElements,
  addFocusClass,
  removeFocusClass,
  moveFocusOutOfModal,
} from "@/common/globalFunctions";
import TagInput from "@/components/TagInput.vue";
import { mdiClose } from "@mdi/js";

import { toRaw } from "vue";

export default {
  name: "EditTagsModal",
  components: { TagInput },
  data() {
    return {
      container: null,
      object: null,
      tags: [],
      isObject: false,
      mdiClose,
    };
  },
  computed: {
    visible() {
      return this.$store.state.openEditTagsModal;
    },
    selectedObjectName() {
      return this.$store.state.selectedObjectName.length > 0
        ? this.$store.state.selectedObjectName
        : "";
    },
    selectedFolderName() {
      return this.$store.state.selectedFolderName.length > 0
        ? this.$store.state.selectedFolderName
        : "";
    },
    projectID() {
      return this.$route.params.project;
    },
    containerName() {
      return this.$route.params.container;
    },
    prevActiveEl() {
      return this.$store.state.prevActiveEl;
    },
  },
  watch: {
    visible: function () {
      if (this.visible) {
        if (this.selectedObjectName?.length > 0) {
          this.isObject = true;
          this.getObject();
        }
        else if (this.selectedFolderName?.length > 0) {
          this.isObject = false;
          this.getContainer();
        }
      }
    },
  },
  methods: {
    getObject: async function () {
      this.container = await getDB().containers.get({
        projectID: this.projectID,
        name: this.containerName,
      });
      if (this.$route.name === "SharedObjects") {
        this.$store.state.objectCache.map(obj => {
          if (obj.name === this.selectedObjectName) {
            this.tags = obj.tags;
            this.object = obj;
          }
        });
      } else {
        this.object = await getDB().objects.get({
          containerID: this.container.id,
          name: this.selectedObjectName,
        });
        if (!this.object.tags?.length) {
          const tags = await getTagsForObjects(
            this.projectID,
            this.container.name,
            [this.selectedObjectName],
          );
          this.tags = tags[0][1] || [];
        } else {
          this.tags = this.object.tags;
        }
      }
    },
    getContainer: async function () {
      this.container = await getDB().containers.get({
        projectID: this.projectID,
        name: this.selectedFolderName,
      });

      if (!this.container?.tags) {
        this.tags = await getTagsForContainer(
          this.projectID,
          this.container?.name,
        );
      } else {
        this.tags = this.container.tags;
      }
    },
    toggleEditTagsModal: function () {
      this.$store.commit("toggleEditTagsModal", false);
      this.$store.commit("setObjectName", "");
      this.$store.commit("setFolderName", "");
      this.tags = [];

      /*
        Prev Active element is a popup menu and it is removed from DOM
        when we click it to open Edit Tags Modal.
        Therefore, we need to make its focusable parent
        to be focused instead after we close the modal.
      */
      const prevActiveElParent = document.getElementById("container-table");
      if (document.body.contains(this.prevActiveEl)) {
        moveFocusOutOfModal(this.prevActiveEl);
      } else {
        moveFocusOutOfModal(prevActiveElParent);
      }

    },
    saveObjectTags: function () {
      const tags = toRaw(this.tags);
      let objectMeta = [
        this.object.name,
        {
          usertags: tags.join(";"),
        },
      ];

      updateObjectMeta(
        this.$route.params.owner || this.projectID,
        this.containerName,
        objectMeta,
      ).then(async () => {
        if (this.$route.name !== "SharedObjects") {
          const currentTime = getCurrentISOtime();
          await getDB().objects
            .where(":id").equals(this.object.id)
            .modify({ tags, last_modified: currentTime });

          // Also update container's last_modified in IDB
          await getDB().containers
            .where({
              projectID: this.projectID,
              name: this.containerName,
            })
            .modify({ last_modified: currentTime });
        } else {
          await this.$store.dispatch("updateSharedObjects", {
            projectID: this.projectID,
            container: {name: this.containerName},
            owner: this.$route.params.owner,
          });
        }
        this.toggleEditTagsModal();
      });
    },
    saveContainerTags: function () {
      const tags = toRaw(this.tags);
      const containerName = this.container.name;
      let meta = {
        usertags: tags.join(";"),
      };
      updateContainerMeta(this.projectID, containerName, meta)
        .then(async () => {
          if (this.$route.name !== "SharedObjects") {
            await getDB().containers
              .where({
                projectID: this.projectID,
                name: containerName,
              })
              .modify({ tags, last_modified: getCurrentISOtime() });
          }
        });
      this.toggleEditTagsModal();
    },
    addingTag: function (e, onBlur) {
      this.tags = addNewTag(e, this.tags, onBlur);
    },
    deletingTag: function (e, tag) {
      this.tags = deleteTag(e, tag, this.tags);
    },
    handleKeyDown: function(e) {
      const focusableList = this.$refs.editTagsContainer.querySelectorAll(
        "input, c-icon, c-button",
      );
      const { first, last } = getFocusableElements(focusableList);

      if (e.key === "Tab" && !e.shiftKey && e.target === last) {
        e.preventDefault();
        first.focus();
      } else if (e.key === "Tab" && e.shiftKey) {
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

<style lang="scss" scoped>

.edit-tags {
  padding: 3rem;
  position: absolute;
  top: -1rem;
  left: 0;
  right: 0;
  max-height: 75vh;
}

h2 { margin: 0 !important; }

c-card-content {
  color: var(--csc-dark);
  padding: 0;
}

c-card-actions {
  padding: 0;
}


</style>
