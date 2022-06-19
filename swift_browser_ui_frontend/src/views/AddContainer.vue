<template>
  <c-card class="addContainer">
    <h2 class="title is-3">
      {{
        create
          ? $t("message.container_ops.addContainer")
          : $t("message.container_ops.editContainer") + folderName
      }}
    </h2>
    <c-card-content>
      <p class="info-text is-size-6">
        {{ $t("message.container_ops.norename") }}
      </p>
      <b-field
        custom-class="has-text-dark"
        :label="$t('message.container_ops.containerName')"
      >
        <b-input
          v-model="folderName"
          name="foldername"
          aria-required="true"
          :disabled="!create"
          data-testid="folder-name"
        />
      </b-field>
      <b-field
        custom-class="has-text-dark"
        :label="$t('message.tagName')"
      >
        <b-taginput
          v-model="tags"
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
        <b>{{ $t("message.container_ops.myResearchProject") }}</b>
      </p>
      <c-link
        :href="`https://my.csc.fi/myProjects/project/${currentProjectID}`"
        underline
        target="_blank"
      >
        {{ $t("message.container_ops.viewProjectMembers") }}
        <i class="mdi mdi-open-in-new" />
      </c-link>
    </c-card-content>
    <c-card-actions justify="space-between">
      <c-button
        outlined
        size="large"
        @click="toggleCreateFolderModal"
      >
        Cancel
      </c-button>
      <c-button
        size="large"
        data-testid="save-folder"
        @click="create ? createContainer() : updateContainer()"
      >
        {{ $t("message.save") }}
      </c-button>
    </c-card-actions>
  </c-card>
</template>

<script>
import { swiftCreateContainer, updateContainerMeta } from "@/common/api";
import {
  taginputConfirmKeys,
  getTagsForContainer,
  tokenize,
} from "@/common/conv";

export default {
  name: "CreateContainer",
  data() {
    return {
      create: true,
      folderName: "",
      tags: [],
      taginputConfirmKeys,
    };
  },
  computed: {
    currentProjectID() {
      return this.$route.params.project;
    },
    selectedFolderName() {
      return this.$store.state.selectedFolderName.length > 0
        ? this.$store.state.selectedFolderName
        : "";
    },
  },
  watch: {
    selectedFolderName: function () {
      if (this.selectedFolderName.length > 0) {
        this.create = false;
        this.getContainer();
      }
    },
  },
  methods: {
    handleChangeContainerName: function (e) {
      this.container = e.target.value;
    },
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
    getContainer: async function () {
      this.folderName = this.$store.state.selectedFolderName;
      const container = await this.$store.state.db.containers.get({
        projectID: this.$store.state.active.id,
        name: this.folderName,
      });
      if (!container.tags) {
        this.tags = await getTagsForContainer(
          this.$route.params.project,
          this.folderName,
        );
      } else {
        this.tags = container.tags;
      }
    },
    updateContainer: function () {
      const tags = this.tags;
      const folderName = this.folderName;
      let meta = {
        usertags: tags.join(";"),
      };
      updateContainerMeta(this.$route.params.project, folderName, meta).then(
        async () => {
          await this.$store.state.db.containers
            .where({
              projectID: this.$route.params.project,
              name: folderName,
            })
            .modify({ tags });
        },
      );
      this.toggleCreateFolderModal();
    },
    toggleCreateFolderModal: function () {
      this.$store.commit("toggleCreateFolderModal", false);
      this.folderName = "";
      this.tags = [];
      this.create = true;
      if (this.selectedFolderName.length > 0) {
        this.$store.commit("setFolderName", "");
      }
    },
  },
};
</script>

<style lang="scss" scoped>
@import "@/css/prod.scss";

.addContainer {
  width: 64vw;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 3rem;
}

.addContainer > h2 {
  margin: 0 !important;
  color: var(--csc-dark-grey);
}

c-card-content {
  background-color: $csc-primary-lighter;
  padding: 1.5rem;
  color: var(--csc-dark-grey);
}

c-card-actions {
  padding: 0;
}

c-card-actions > c-button {
  margin: 0;
}
</style>
