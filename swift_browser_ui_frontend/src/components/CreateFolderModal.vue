<template>
  <c-card class="add-folder">
    <div
      id="createFolder-modal-content"
      class="modal-content-wrapper"
    >
      <c-toasts
        id="createModal-toasts"
        data-testid="createModal-toasts"
        vertical="bottom"
        absolute
      />
      <h2 class="title is-4 has-text-dark">
        {{ $t("message.container_ops.addContainer") }}
      </h2>
      <c-card-content>
        <p class="info-text is-size-6">
          {{ $t("message.container_ops.norename") }}
        </p>
        <c-text-field
          id="folderName"
          v-model="folderName"
          v-csc-control
          :label="$t('message.container_ops.folderName')"
          name="foldername"
          aria-required="true"
          data-testid="folder-name"
        />
        <label
          class="taginput-label"
          label-for="create-folder-taginput"
        >
          {{ $t('message.tagName') }}
        </label>
        <TagInput
          id="create-folder-taginput"
          :tags="tags"
          data-testid="folder-tag"
          @addTag="addingTag"
          @deleteTag="deletingTag"
        />
        <p class="info-text is-size-6">
          {{ $t("message.container_ops.createdFolder") }}
          <b>{{ active.name }}</b>.
        </p>
        <c-link
          :href="projectInfoLink"
          underline
          target="_blank"
        >
          {{ $t("message.container_ops.viewProjectMembers") }}
          <i class="mdi mdi-open-in-new" />
        </c-link>
      </c-card-content>
    </div>
    <c-card-actions justify="space-between">
      <c-button
        outlined
        size="large"
        @click="toggleCreateFolderModal"
        @keyup.enter="toggleCreateFolderModal"
      >
        {{ $t("message.cancel") }}
      </c-button>
      <c-button
        size="large"
        data-testid="save-folder"
        @click="createContainer"
        @keyup.enter="createContainer"
      >
        {{ $t("message.save") }}
      </c-button>
    </c-card-actions>
  </c-card>
</template>

<script>
import { swiftCreateContainer } from "@/common/api";
import {
  tokenize,
} from "@/common/conv";
import { getDB } from "@/common/db";

import {
  addNewTag,
  deleteTag,
  getProjectNumber,
} from "@/common/globalFunctions";
import TagInput from "@/components/TagInput.vue";

import { toRaw } from "vue";

export default {
  name: "CreateFolderModal",
  components: { TagInput },
  data() {
    return {
      folderName: "",
      tags: [],
      projectInfoLink: "",
    };
  },
  computed: {
    active() {
      return this.$store.state.active;
    },
  },
  watch: {
    active: function () {
      this.projectInfoLink = this.$t("message.dashboard.projectInfoBaseLink")
        + getProjectNumber(this.active);
    },
  },
  methods: {
    createContainer: function () {
      let projectID = this.$route.params.project;
      const folderName = toRaw(this.folderName);
      const tags = toRaw(this.tags);
      swiftCreateContainer(projectID, folderName, tags.join(";"))
        .then(() => {
          getDB().containers.add({
            projectID: projectID,
            name: folderName,
            tokens: tokenize(folderName),
            tags: tags,
            count: 0,
            bytes: 0,
          });
        }).then(() => {
          swiftCreateContainer(projectID, `${folderName}_segments`, [])
            .then(() => {
              getDB().containers.add({
                projectID: projectID,
                name: `${folderName}_segments`,
                tokens: [],
                tags: [],
                count: 0,
                bytes: 0,
              });
            });
          this.toggleCreateFolderModal();
        })
        .catch(err => {
          let errorMessage = this.$t("message.error.createFail");
          if (err.message.match("Container name already in use")) {
            errorMessage = this.$t("message.error.inUse");
          } else if (err.message.match("Invalid container or tag name")) {
            errorMessage = this.$t("message.error.invalidName");
          }
          document.querySelector("#createModal-toasts").addToast(
            {
              id: "create-toast",
              progress: false,
              type: "error",
              message: errorMessage },
          );
        });
    },
    toggleCreateFolderModal: function () {
      this.$store.commit("toggleCreateFolderModal", false);
      this.folderName = "";
      this.tags = [];
      this.create = true;
      document.querySelector("#createModal-toasts").removeToast("create-toast");
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

.add-folder {
  padding: 3rem;
  position: absolute;
  top: -1rem;
  left: 0;
  right: 0;
  max-height: 75vh;
}

@media screen and (max-width: 766px), (max-height: 580px) {
   .add-folder {
    top: -5rem;
  }
}

@media screen and (max-height: 580px) and (max-width: 766px),
(max-width: 525px) {
  .add-folder {
    top: -9rem;
  }
}

@media screen and (max-height: 580px) and (max-width: 525px) {
  .add-folder {
    top: -13rem;
   }
 }

c-card-content {
  color: var(--csc-dark-grey);
  padding: 1.5rem 0 0 0;
}

c-card-actions {
  padding: 0;
}

c-card-actions > c-button {
  margin: 0;
}

c-link {
  margin-top: -1rem;
}
</style>
