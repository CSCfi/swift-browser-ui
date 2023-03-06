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
        <b-field
          custom-class="has-text-dark"
          :label="$t('message.tagName')"
          label-for="folder-taginput"
        >
          <b-taginput
            id="folder-taginput"
            v-model="tags"
            aria-close-label="delete-tag"
            ellipsis
            maxlength="20"
            has-counter
            rounded
            type="is-primary"
            :placeholder="$t('message.tagPlaceholder')"
            :confirm-keys="taginputConfirmKeys"
            :on-paste-separators="taginputConfirmKeys"
            data-testid="folder-tag"
          />
        </b-field>
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
  taginputConfirmKeys,
  tokenize,
} from "@/common/conv";

import {
  modifyBrowserPageStyles,
  getProjectNumber,
} from "@/common/globalFunctions";

export default {
  name: "CreateFolderModal",
  data() {
    return {
      folderName: "",
      tags: [],
      taginputConfirmKeys,
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
          let errorMessage = this.$t("message.error.createFail");
          if (err.message.match("Container name already in use")) {
            errorMessage = this.$t("message.error.inUse");
          } else if (err.message.match("Invalid container name")) {
            errorMessage = this.$t("message.error.invalidName");
          }
          document.querySelector("#createModal-toasts").addToast(
            { progress: false,
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
      modifyBrowserPageStyles();
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

@media screen and (max-height: 720px), (max-width: 992px ) {
  .add-folder {
    max-height: 50vh;
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
</style>
