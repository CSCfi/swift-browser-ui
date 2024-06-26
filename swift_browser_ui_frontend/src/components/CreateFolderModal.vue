<template>
  <c-card
    ref="createFolderContainer"
    class="add-folder"
    data-testid="create-folder-modal"
    @keydown="handleKeyDown"
  >
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
      <h2 class="title is-4">
        {{ $t("message.container_ops.addContainer") }}
      </h2>
      <c-card-content>
        <p class="info-text is-size-6">
          {{ $t("message.container_ops.norename") }}
        </p>
        <c-text-field
          id="newFolder-input"
          v-model="folderName"
          v-csc-control
          :label="$t('message.container_ops.folderName')"
          name="foldername"
          aria-required="true"
          data-testid="folder-name"
          :valid="errorMsg.length === 0"
          :validation="errorMsg"
          required
          validate-on-blur
          @changeValue="interacted=true"
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
        data-testid="cancel-save-folder"
        @click="toggleCreateFolderModal(false)"
        @keyup.enter="toggleCreateFolderModal(true)"
      >
        {{ $t("message.cancel") }}
      </c-button>
      <c-button
        size="large"
        data-testid="save-folder"
        @click="createContainer(false)"
        @keyup.enter="createContainer(true)"
      >
        {{ $t("message.save") }}
      </c-button>
    </c-card-actions>
  </c-card>
</template>

<script>
import { swiftCreateContainer } from "@/common/api";
import { tokenize, getTimestampForContainer } from "@/common/conv";
import { getDB } from "@/common/db";

import {
  addNewTag,
  deleteTag,
  getProjectNumber,
  validateFolderName,
  getCurrentISOtime,
} from "@/common/globalFunctions";
import {
  getFocusableElements,
  moveFocusOutOfModal,
  keyboardNavigationInsideModal,
} from "@/common/keyboardNavigation";
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
      interacted: false, //don't show error when opening modal
      errorMsg: "",
      containers: [],
    };
  },
  computed: {
    active() {
      return this.$store.state.active;
    },
    uname() {
      return this.$store.state.uname;
    },
    controller() {
      return new AbortController();
    },
    prevActiveEl() {
      return this.$store.state.prevActiveEl;
    },
    modalVisible() {
      return this.$store.state.openCreateFolderModal;
    },
  },
  watch: {
    active: function () {
      this.projectInfoLink = this.$t("message.supportMenu.projectInfoBaseLink")
        + getProjectNumber(this.active);
    },
    folderName: function () {
      this.interacted ?
        this.errorMsg = validateFolderName(
          this.folderName, this.$t, this.containers) :
        this.errorMsg = "";
    },
    modalVisible: async function() {
      if (this.modalVisible) {
        this.containers = await getDB().containers
          .where({ projectID: this.active.id })
          .toArray();
      }
    },
  },
  methods: {
    createContainer: function (keypress) {
      this.folderName = this.folderName.trim();
      this.errorMsg = validateFolderName(
        this.folderName, this.$t, this.containers);
      if (this.errorMsg.length) return;

      let projectID = this.$route.params.project;
      const folderName = toRaw(this.folderName);
      const tags = toRaw(this.tags);
      swiftCreateContainer(projectID, folderName, tags.join(";"))
        .then(async () => {
          const containerTimestamp = await getTimestampForContainer(
            projectID, folderName, this.controller.signal);

          getDB().containers.add({
            projectID: projectID,
            name: folderName,
            tokens: tokenize(folderName),
            tags: tags,
            count: 0,
            bytes: 0,
            last_modified: getCurrentISOtime(containerTimestamp*1000),
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
          this.toggleCreateFolderModal(keypress);

          this.$router.push({
            name: "AllFolders",
            params: {
              project: this.active.id,
              user: this.uname,
            },
          });
          this.$store.commit("setNewFolder", folderName);
        })
        .catch(err => {
          let errorMessage = this.$t("message.error.createFail");
          if (err.message.match("Container name already in use")) {
            errorMessage = this.$t("message.error.inUseOtherPrj");
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
    toggleCreateFolderModal: function (keypress) {
      this.$store.commit("toggleCreateFolderModal", false);
      this.folderName = "";
      this.tags = [];
      this.create = true;
      this.interacted = false;
      this.errorMsg = "";
      document.querySelector("#createModal-toasts").removeToast("create-toast");

      if (keypress) moveFocusOutOfModal(this.prevActiveEl);
    },
    addingTag: function (e, onBlur) {
      this.tags = addNewTag(e, this.tags, onBlur);
    },
    deletingTag: function (e, tag) {
      this.tags = deleteTag(e, tag, this.tags);
    },
    handleKeyDown: function (e) {
      const focusableList = this.$refs.createFolderContainer.querySelectorAll(
        "input, c-link, c-button",
      );
      const { first, last } = getFocusableElements(focusableList);
      keyboardNavigationInsideModal(e, first, last);
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

@media screen and (max-width: 767px), (max-height: 580px) {
   .add-folder {
    top: -5rem;
  }
}

@media screen and (max-height: 580px) and (max-width: 767px),
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
  color: var(--csc-dark);
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
