<!--NOT up-to-date: tags not in use-->
<template>
  <c-card
    ref="editTagsContainer"
    class="modal-card"
    data-testid="edit-tags-modal"
    @keydown="handleKeyDown"
  >
    <c-card-content class="modal-card-content">
      <h2 class="title is-4 has-text-dark">
        {{ $t('message.editTags') }}
      </h2>
      <TagInput
        id="edit-tags-input"
        data-testid="edit-tags-input"
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
        data-testid="save-edit-tags"
        size="large"
        @click="isObject ? saveObjectTags() : saveContainerTags()"
        @keyup.enter="isObject ?
          saveObjectTags() : saveContainerTags()"
      >
        {{ $t("message.save") }}
      </c-button>
    </c-card-actions>
  </c-card>
</template>

<script>
import { getDB } from "@/common/idb";

import {
  addNewTag,
  deleteTag,
  getCurrentISOtime,
} from "@/common/globalFunctions";
import { captureKeyboardNavInsideModal } from "@/common/keyboardNavigation";
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
      return this.$store.openEditTagsModal;
    },
    selectedObjectName() {
      return this.$store.selectedObjectName.length > 0
        ? this.$store.selectedObjectName
        : "";
    },
    selectedBucketName() {
      return this.$store.selectedBucketName.length > 0
        ? this.$store.selectedBucketName
        : "";
    },
    projectID() {
      return this.$route.params.project;
    },
    containerName() {
      return this.$route.params.container;
    },
  },
  watch: {
    visible: function () {
      if (this.visible) {
        if (this.selectedObjectName?.length > 0) {
          this.isObject = true;
          this.getObject();
        }
        else if (this.selectedBucketName?.length > 0) {
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
      // Objects no longer in IDB
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
    },
    getContainer: async function () {
      this.container = await getDB().containers.get({
        projectID: this.projectID,
        name: this.selectedBucketName,
      });

      if (!this.container?.tags) {
        // this.tags = await getTagsForContainer(
        //   this.projectID,
        //   this.container?.name,
        // );
      } else {
        this.tags = this.container.tags;
      }
    },
    toggleEditTagsModal: function () {
      this.$store.toggleEditTagsModal(false);
      this.$store.setObjectName("");
      this.$store.setBucketName("");
      this.tags = [];
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
        const currentTime = getCurrentISOtime();

        // Update container's last_modified in IDB
        await getDB().containers
          .where({
            projectID: this.projectID,
            name: this.containerName,
          })
          .modify({ last_modified: currentTime });

        this.toggleEditTagsModal();
      });
    },
    saveContainerTags: function () {
      this.toggleEditTagsModal();
    },
    addingTag: function (e, onBlur) {
      this.tags = addNewTag(e, this.tags, onBlur);
    },
    deletingTag: function (e, tag) {
      this.tags = deleteTag(e, tag, this.tags);
    },
    handleKeyDown: function(e) {
      if (e.key === "Escape") {
        this.toggleEditTagsModal();
      } else {
        captureKeyboardNavInsideModal(e, this.$refs.editTagsContainer);
      }
    },
  },
};
</script>

<style scoped>

h2 { margin: 0 !important; }

c-card-actions {
  padding: 0;
}


</style>
