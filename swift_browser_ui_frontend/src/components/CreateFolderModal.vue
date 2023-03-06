<template>
  <c-card class="add-folder">
    <div
      id="createFolder-modal-content"
      class="modal-content-wrapper"
    >
      <h2 class="title is-4 has-text-dark">
        {{ $t("message.container_ops.addContainer") }}
      </h2>
      <c-card-content>
        <p class="info-text is-size-6">
          {{ $t("message.container_ops.norename") }}
        </p>
        <b-field
          custom-class="has-text-dark"
          :label="$t('message.container_ops.folderName')"
          label-for="folderName"
        >
          <b-input
            id="folderName"
            v-model="folderName"
            name="foldername"
            aria-required="true"
            data-testid="folder-name"
          />
        </b-field>
        <label label-for="create-folder-taginput">
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
          :href="`https://my.csc.fi/myProjects/project/${projectNumber}`"
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

import {
  addNewTag,
  deleteTag,
  modifyBrowserPageStyles,
  getProjectNumber,
} from "@/common/globalFunctions";
import TagInput from "@/components/TagInput.vue";

export default {
  name: "CreateFolderModal",
  components: { TagInput },
  data() {
    return {
      folderName: "",
      tags: [],
      projectNumber: "",
    };
  },
  computed: {
    active() {
      return this.$store.state.active;
    },
  },
  watch: {
    active: function () {
      this.projectNumber = getProjectNumber(this.active);
    },
  },
  methods: {
    createContainer: function () {
      let projectID = this.$route.params.project;
      swiftCreateContainer(projectID, this.folderName, this.tags.join(";"))
        .then(() => {
          this.$store.state.db.containers.add({
            projectID: projectID,
            name: this.folderName,
            tokens: tokenize(this.folderName),
            tags: this.tags,
            count: 0,
            bytes: 0,
          });
          this.toggleCreateFolderModal();
        })
        .catch(err => {
          if (err.message.match("Container name already in use")) {
            this.$buefy.toast.open({
              message: this.$t("message.error.inUse"),
              type: "is-danger",
            });
          } else if (err.message.match("Invalid container name")) {
            this.$buefy.toast.open({
              message: this.$t("message.error.invalidName"),
              type: "is-danger",
            });
          } else {
            this.$buefy.toast.open({
              message: this.$t("message.error.createFail"),
              type: "is-danger",
            });
          }
        });
    },
    toggleCreateFolderModal: function () {
      this.$store.commit("toggleCreateFolderModal", false);
      this.folderName = "";
      this.tags = [];
      this.create = true;
      modifyBrowserPageStyles();
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

.add-folder {
  padding: 3rem;
  position: absolute;
  top: -1rem;
  left: 0;
  right: 0;
  max-height: 75vh;
}

@media screen and (max-width: 773px), (max-height: 580px) {
   .add-folder {
    top: -5rem;
  }
}

@media screen and (max-height: 580px) and (max-width: 773px), 
(max-width: 533px) {
  .add-folder {
    top: -9rem;
  }
}

@media screen and (max-height: 580px) and (max-width: 533px) {
  .add-folder {
    top: -13rem;
   }
 }

c-card-content {
  color: var(--csc-dark-grey);
  padding: 1.5rem 0 0 0;
}

label {
  font-weight: bold;
  margin-bottom: -1rem;
}

c-card-actions {
  padding: 0;
}

c-card-actions > c-button {
  margin: 0;
}
</style>
