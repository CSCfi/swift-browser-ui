<template>
  <c-card>
    <h1 class="title is-3 addcontainerhead">
      {{
        create
          ? $t("message.container_ops.addContainer")
          : $t("message.container_ops.editContainer") + container
      }}
    </h1>
    <c-card-content>
      <p class="info-text is-size-6">
        {{ $t("message.container_ops.norename") }}
      </p>
      <c-text-field
        :label="$t('message.container_ops.containerName')"
        name="foldername"
        type="text"
        required
        :disabled="!create"
        v-csc-model="container"
      />
      <b-field
        custom-class="has-text-dark"
        :label="$t('message.tagName')"
        :message="$t('message.tagMessage')"
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
        />
      </b-field>
      <p class="info-text is-size-6">
        {{ $t("message.container_ops.createdFolder") }}
        <b>{{ $t("message.container_ops.myResearchProject") }}</b>
      </p>
      <c-link href="https://csc.fi" underline target="_blank">
        Default link
        <i class="mdi mdi-login" slot="icon" />
      </c-link>
    </c-card-content>
    <c-card-actions justify="space-between">
      <c-button outlined @click="toggleCreateFolderModal">Cancel</c-button>
      <c-button @click="create ? createContainer() : updateContainer()">
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
      container: "",
      inputTag: "",
      tags: [],
      create: true,
      taginputConfirmKeys,
    };
  },

  beforeMount() {
    if (this.$route.name === "EditContainer") {
      this.create = false;
      this.getContainer();
    }
  },
  methods: {
    handleChangeContainerName: function (e) {
      this.container = e.target.value;
    },
    createContainer: function () {
      let projectID = this.$route.params.project;
      swiftCreateContainer(projectID, this.container, this.tags.join(";"))
        .then(() => {
          this.$store.state.db.containers.add({
            projectID: projectID,
            name: this.container,
            tokens: tokenize(this.container),
            tags: this.tags,
            count: 0,
            bytes: 0,
          });
          this.$store.commit("toggleCreateFolderModal", false);
        })
        .catch((err) => {
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
      const containerName = this.$route.params.container;
      this.container = containerName;

      const container = await this.$store.state.db.containers.get({
        projectID: this.$store.state.active.id,
        name: this.container,
      });
      if (!container.tags) {
        this.tags = await getTagsForContainer(
          this.$route.params.project,
          containerName,
        );
      } else {
        this.tags = container.tags;
      }
    },
    updateContainer: function () {
      let meta = {
        usertags: this.tags.join(";"),
      };
      updateContainerMeta(
        this.$route.params.project,
        this.container,
        meta,
      ).then(async () => {
        await this.$store.state.db.containers
          .where({
            projectID: this.$route.params.project,
            name: this.container,
          })
          .modify({ tags: this.tags });
        this.$router.go(-1);
      });
    },
    toggleCreateFolderModal: function () {
      this.$store.commit("toggleCreateFolderModal", false);
    },
  },
};
</script>

<style scoped>
#addview {
  width: auto;
  margin-left: 5%;
  margin-right: 5%;
}
.addcontainerhead,
.info-text {
  color: var(--csc-dark-grey);
}
</style>
