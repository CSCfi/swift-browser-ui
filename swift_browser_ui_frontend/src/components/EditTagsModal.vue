<template>
  <c-card class="edit-tags">
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

import {
  addNewTag,
  deleteTag,
} from "@/common/globalFunctions";
import TagInput from "@/components/TagInput.vue";
import { mdiClose } from "@mdi/js";

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
  },
  watch: {
    selectedObjectName: function () {
      if (this.selectedObjectName && this.selectedObjectName.length > 0) {
        this.isObject = true;
        this.getObject();
      }
    },
    selectedFolderName: function () {
      if (this.selectedFolderName && this.selectedFolderName.length > 0) {
        this.isObject = false;
        this.getContainer();
      }
    },
  },
  methods: {
    getObject: async function () {
      this.container = await this.$store.state.db.containers.get({
        projectID: this.$route.params.project,
        name: this.$route.params.container,
      });
      if (this.$route.name === "SharedObjects") {
        this.$store.state.objectCache.map(obj => {
          if (obj.name === this.selectedObjectName) {
            this.tags = obj.tags;
            this.object = obj;
          }
        });
      } else {
        this.object = await this.$store.state.db.objects.get({
          containerID: this.container.id,
          name: this.selectedObjectName,
        });
        if (!this.object.tags.length) {
          const tags = await getTagsForObjects(
            this.$route.params.project,
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
      this.container = await this.$store.state.db.containers.get({
        projectID: this.$route.params.project,
        name: this.selectedFolderName,
      });
      if (!this.container.tags) {
        this.tags = await getTagsForContainer(
          this.$route.params.project,
          this.container.name,
        );
      } else {
        this.tags = this.container.tags;
      }
    },
    toggleEditTagsModal: function () {
      this.$store.commit("toggleEditTagsModal", false);
      this.$store.commit("setObjectName", "");
      this.$store.commit("setFolderName", "");
    },
    saveObjectTags: function () {
      let objectMeta = [
        this.object.name,
        {
          usertags: this.tags.join(";"),
        },
      ];
      updateObjectMeta(
        this.$route.params.owner || this.$route.params.project,
        this.$route.params.container,
        objectMeta,
      ).then(async () => {
        if (this.$route.name !== "SharedObjects") {
          await this.$store.state.db.objects
            .where(":id").equals(this.object.id)
            .modify({tags: this.tags});
        } else {
          await this.$store.dispatch("updateSharedObjects", {
            project: this.$route.params.project,
            container: {name: this.$route.params.container},
            owner: this.$route.params.owner,
          });
        }
        this.toggleEditTagsModal();
      });
    },
    saveContainerTags: function () {
      const tags = this.tags;
      const containerName = this.container.name;
      let meta = {
        usertags: tags.join(";"),
      };
      updateContainerMeta(this.$route.params.project, containerName, meta)
        .then(async () => {
          if (this.$route.name !== "SharedObjects") {
            await this.$store.state.db.containers
              .where({
                projectID: this.$route.params.project,
                name: containerName,
              })
              .modify({ tags });
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
  },
};
</script>

<style lang="scss" scoped>
@import "@/css/prod.scss";

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
  color: var(--csc-dark-grey);
  padding: 0;
}

c-card-actions {
  padding: 0;
}


</style>
